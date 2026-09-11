import json
import math

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class RequestConsumer(AsyncJsonWebsocketConsumer):

    #########################################################
    # CONNECT
    #########################################################

    async def connect(self):

        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4401)
            return

        #################################################
        # TECHNICIAN GROUP
        #################################################

        self.request_id = self.scope['url_route']['kwargs'].get('id')
        self.is_tracking_connection = bool(self.request_id)

        if self.is_tracking_connection:
            self.service_request = await self.get_service_request(self.request_id)
            if not self.service_request:
                await self.close(code=4404)
                return

            self.role = await self.get_tracking_role(self.user, self.service_request)
            if not self.role:
                await self.close(code=4403)
                return

            self.tracking_group_name = f"tracking_{self.request_id}"

            await self.channel_layer.group_add(
                self.tracking_group_name,
                self.channel_name
            )
        else:
            # /ws/requests/ is the technician dashboard notification channel.
            if not await self.is_technician(self.user):
                await self.close(code=4403)
                return

            self.group_name = 'technicians'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

        #################################################
        # ACCEPT SOCKET
        #################################################

        await self.accept()

        #################################################
        # SEND CONNECT MESSAGE
        #################################################

        await self.send(text_data=json.dumps({
            'message': 'Connected'
        }))

        # A newly opened or refreshed customer page must immediately receive
        # the latest authorized technician position; it should not have to wait
        # for the next physical GPS movement.
        if self.is_tracking_connection and self.role == 'customer':
            snapshot = self.tracking_snapshot(self.service_request)
            if snapshot:
                await self.send_json(snapshot)

    @database_sync_to_async
    def get_service_request(self, request_id):
        from core.models import ServiceRequest

        try:
            return ServiceRequest.objects.get(id=request_id)
        except ServiceRequest.DoesNotExist:
            return None

    @database_sync_to_async
    def get_tracking_role(self, user, service_request):
        """Return the participant role only when the logged-in user owns it."""
        from core.models import Technician_signup, customer_signup

        customer = customer_signup.objects.filter(user=user).first()
        if customer and customer.username == service_request.customer_username:
            return 'customer'

        technician = Technician_signup.objects.filter(user=user).first()
        if technician and technician.username == service_request.technician_username:
            return 'technician'

        return None

    @database_sync_to_async
    def is_technician(self, user):
        from core.models import Technician_signup

        return Technician_signup.objects.filter(user=user).exists()

    @database_sync_to_async
    def save_tracking_snapshot(self, request_id, user, latitude, longitude,
                               route_distance_meters, route_eta_seconds, tracking_arrived):
        """Authorize and persist the latest location in the same DB operation."""
        from core.models import ServiceRequest, Technician_signup
        from django.utils import timezone

        try:
            service_request = ServiceRequest.objects.get(id=request_id)
        except ServiceRequest.DoesNotExist:
            return None

        technician = Technician_signup.objects.filter(user=user).first()
        if not (
            technician
            and technician.username == service_request.technician_username
            and service_request.tracking_active
            and service_request.status != 'Completed'
        ):
            return None

        service_request.technician_latitude = latitude
        service_request.technician_longitude = longitude
        service_request.tracking_updated_at = timezone.now()
        update_fields = [
            'technician_latitude', 'technician_longitude', 'tracking_updated_at', 'tracking_arrived'
        ]
        service_request.tracking_arrived = tracking_arrived
        if route_distance_meters is not None:
            service_request.route_distance_meters = route_distance_meters
            update_fields.append('route_distance_meters')
        if route_eta_seconds is not None:
            service_request.route_eta_seconds = route_eta_seconds
            update_fields.append('route_eta_seconds')
        service_request.save(update_fields=update_fields)

        return self.tracking_snapshot(service_request)

    #########################################################
    # DISCONNECT
    #########################################################

    async def disconnect(self, code):

        print("[ICON] SOCKET DISCONNECTED")

        #################################################
        # REMOVE TECHNICIAN GROUP
        #################################################

        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

        #################################################
        # REMOVE TRACKING GROUP
        #################################################

        if hasattr(self, 'tracking_group_name'):

            await self.channel_layer.group_discard(
                self.tracking_group_name,
                self.channel_name
            )

    

    #########################################################
    # NEW REQUEST NOTIFICATION
    #########################################################

    async def new_request(self, event):

        print("[FIRE] CONSUMER RECEIVED EVENT")

        await self.send(text_data=json.dumps(
            event['content']
        ))

    #########################################################
    # REMOVE NOTIFICATION
    #########################################################

    async def notification_removed(self, event):

        print("[FIRE] notification_removed HIT")

        await self.send(text_data=json.dumps({
            'type': 'notification_removed',
            'request_id': event['request_id']
        }))

    #########################################################
    # TECHNICIAN MESSAGE
    #########################################################

    async def technicians_message(self, event):

        await self.send_json(event['content'])

    #########################################################
    # RECEIVE LIVE GPS
    #########################################################

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data is None:
            return

        try:
            data = json.loads(text_data)
        except (TypeError, json.JSONDecodeError):
            return

        print("[ICON] RECEIVED:", data)

        #################################################
        # LIVE LOCATION TRACKING
        ##################################
        if data.get('type') == 'live_location':
            if not getattr(self, 'is_tracking_connection', False):
                return

            latitude = self.valid_coordinate(data.get('latitude'), -90, 90)
            longitude = self.valid_coordinate(data.get('longitude'), -180, 180)

            if latitude is None or longitude is None:
                return

            route_distance_meters = self.valid_nonnegative_number(
                data.get('route_distance_meters'), 10_000_000
            )
            route_eta_seconds = self.valid_nonnegative_number(
                data.get('route_eta_seconds'), 86_400
            )
            tracking_arrived = data.get('journey_status') == 'arrived'
            snapshot = await self.save_tracking_snapshot(
                self.request_id,
                self.user,
                latitude,
                longitude,
                route_distance_meters,
                route_eta_seconds,
                tracking_arrived,
            )
            if not snapshot:
                return

            #################################################
            # SEND TO REQUEST-SPECIFIC TRACKING GROUP
            #################################################

            await self.channel_layer.group_send(
                self.tracking_group_name,
                snapshot
            )

    @staticmethod
    def valid_coordinate(value, minimum, maximum):
        # JSON booleans are subclasses of int in Python, but are not coordinates.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        value = float(value)
        if not math.isfinite(value) or not minimum <= value <= maximum:
            return None
        return value

    @staticmethod
    def valid_nonnegative_number(value, maximum):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        value = float(value)
        if not math.isfinite(value) or not 0 <= value <= maximum:
            return None
        return value

    @classmethod
    def tracking_snapshot(cls, service_request):
        latitude = cls.valid_coordinate(service_request.technician_latitude, -90, 90)
        longitude = cls.valid_coordinate(service_request.technician_longitude, -180, 180)
        if latitude is None or longitude is None:
            return None

        snapshot = {
            'type': 'location_update',
            'latitude': latitude,
            'longitude': longitude,
            'journey_status': 'arrived' if service_request.tracking_arrived else 'on_the_way',
        }
        distance = cls.valid_nonnegative_number(
            service_request.route_distance_meters, 10_000_000
        )
        eta = cls.valid_nonnegative_number(service_request.route_eta_seconds, 86_400)
        if distance is not None and eta is not None:
            snapshot['route_distance_meters'] = distance
            snapshot['route_eta_seconds'] = eta
        return snapshot

    #########################################################
    # SEND LIVE LOCATION TO CUSTOMER
    #########################################################

    async def location_update(self, event):

        await self.send_json(event)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    
    @database_sync_to_async
    def get_service_request(self, request_id):
        from core.models import ServiceRequest
        try:
            return ServiceRequest.objects.get(id=request_id)
        except ServiceRequest.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_role_and_verify(self, user, service_request):
        # Determine if the user is the customer or technician for this request
        if user.username == service_request.customer_username:
            return 'customer'
        elif user.username == service_request.technician_username:
            return 'technician'
        return None
        
    @database_sync_to_async
    def get_chat_conversation(self, service_request):
        from core.models import ChatConversation
        try:
            return ChatConversation.objects.get(service_request=service_request)
        except ChatConversation.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, conversation, sender_username, message_text):
        from core.models import ChatMessage
        msg = ChatMessage.objects.create(
            conversation=conversation,
            sender_username=sender_username,
            message=message_text
        )
        return msg

    async def connect(self):
        print("[CHAT] SOCKET CONNECTED")
        
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            print("[CHAT] User not authenticated")
            await self.close()
            return

        self.request_id = self.scope['url_route']['kwargs'].get('request_id')
        if not self.request_id:
            print("[CHAT] No request ID")
            await self.close()
            return

        self.service_request = await self.get_service_request(self.request_id)
        if not self.service_request:
            print("[CHAT] ServiceRequest not found")
            await self.close()
            return

        self.role = await self.get_user_role_and_verify(self.user, self.service_request)
        if not self.role:
            print("[CHAT] User not authorized for this request")
            await self.close()
            return

        if self.service_request.status == 'Pending':
            print("[CHAT] Request is Pending, chat not allowed")
            await self.close()
            return

        if self.service_request.status == 'Assigned' and not getattr(self.service_request, 'tracking_active', False):
            print("[CHAT] Journey not started, chat not allowed")
            await self.close()
            return

        self.conversation = await self.get_chat_conversation(self.service_request)
        if not self.conversation:
            print("[CHAT] Conversation not found")
            await self.close()
            return

        self.chat_group_name = f"chat_{self.request_id}"

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': 'Connected to chat'
        }))

    async def disconnect(self, code):
        print("[CHAT] SOCKET DISCONNECTED")
        if hasattr(self, 'chat_group_name'):
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data is None:
            return
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            # Refresh service request to check status
            self.service_request = await self.get_service_request(self.request_id)
            if not self.service_request:
                return
            if self.service_request.status == 'Completed':
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Chat is closed. Service is completed.'
                }))
                return
                
            if self.service_request.status == 'Assigned' and not getattr(self.service_request, 'tracking_active', False):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Chat is unavailable until journey starts.'
                }))
                return

            self.conversation = await self.get_chat_conversation(self.service_request)
            if not self.conversation or not self.conversation.is_active:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Chat conversation is not active.'
                }))
                return

            message_text = data.get('message', '').strip()
            if not message_text:
                return

            # Ensure sender is derived from self.scope['user'] server-side
            sender_username = self.user.username if self.user else "System"

            msg = await self.save_message(self.conversation, sender_username, message_text)

            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message_broadcast',
                    'sender_username': sender_username,
                    'message': message_text,
                    'created_at': msg.created_at.isoformat()
                }
            )

    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'sender_username': event['sender_username'],
            'message': event['message'],
            'created_at': event['created_at']
        }))

class TechnicianSupportConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    def get_session(self, session_pk):
        from core.models import TechnicianSupportSession
        try:
            return TechnicianSupportSession.objects.get(id=session_pk)
        except TechnicianSupportSession.DoesNotExist:
            return None

    @database_sync_to_async
    def verify_ownership(self, session, user):
        from core.models import Technician_signup
        if user.is_staff or user.is_superuser:
            return 'admin'
        
        technician = Technician_signup.objects.filter(user=user).first()
        if technician and session.technician_id == technician.id:
            return 'technician'
        
        return None

    @database_sync_to_async
    def save_message(self, session, sender_type, user, message_text, options_snapshot=None):
        from core.models import TechnicianSupportMessage
        msg = TechnicianSupportMessage.objects.create(
            session=session,
            sender_type=sender_type,
            sender_user=user if sender_type != 'SYSTEM' else None,
            message=message_text,
            options_snapshot=options_snapshot
        )
        # Update unread count and latest message timestamp if escalated
        if session.status == 'ESCALATED':
            if hasattr(session, 'ticket'):
                ticket = session.ticket
                if sender_type == 'ADMIN':
                    ticket.unread_technician_count += 1
                elif sender_type == 'TECHNICIAN':
                    ticket.unread_admin_count += 1
                from django.utils import timezone
                ticket.last_message_at = timezone.now()
                ticket.save()
        return msg

    @database_sync_to_async
    def process_guided_action(self, session, action_value, user):
        from core.services.support_flow import SupportFlowService
        from core.models import Technician_signup
        technician = Technician_signup.objects.filter(user=user).first()
        
        # Check if action contains context
        context_id = None
        if '|' in action_value:
            parts = action_value.split('|')
            action_value = parts[0]
            context_id = parts[1]
            
        return SupportFlowService.process_action(session, action_value, technician, context_id)

    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.session_pk = self.scope['url_route']['kwargs'].get('session_pk')
        if not self.session_pk:
            await self.close()
            return

        self.session = await self.get_session(self.session_pk)
        if not self.session:
            await self.close()
            return

        self.role = await self.verify_ownership(self.session, self.user)
        if not self.role:
            await self.close()
            return

        self.support_group_name = f"support_session_{self.session_pk}"

        await self.channel_layer.group_add(
            self.support_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'support_group_name'):
            await self.channel_layer.group_discard(
                self.support_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if not text_data:
            return
            
        data = json.loads(text_data)
        message_type = data.get('type')
        
        # Refresh session status
        self.session = await self.get_session(self.session_pk)
        
        if message_type == 'chat_message' or message_type == 'support_action':
            message_text = data.get('message', '').strip()
            action_value = data.get('action_value') # Sent when clicking an option
            
            # Identify sender
            sender_type = 'ADMIN' if self.role == 'admin' else 'TECHNICIAN'
            
            # 1. Save user's message
            msg_text_to_save = message_text
            if not msg_text_to_save and action_value:
                msg_text_to_save = data.get('action_label', f"Selected: {action_value}")
                
            if msg_text_to_save:
                user_msg = await self.save_message(
                    self.session, 
                    sender_type, 
                    self.user, 
                    msg_text_to_save
                )
                await self.broadcast_message(user_msg)
            
            # 2. Process guided logic if NOT escalated
            if self.session.status == 'ACTIVE' and self.role == 'technician' and action_value:
                response = await self.process_guided_action(self.session, action_value, self.user)
                
                # Save system response
                system_msg = await self.save_message(
                    self.session,
                    'SYSTEM',
                    None,
                    response['message'],
                    options_snapshot=response.get('options')
                )
                await self.broadcast_message(system_msg)
                
                if response.get('escalated'):
                    # Broadcast escalation status
                    await self.channel_layer.group_send(
                        self.support_group_name,
                        {
                            'type': 'status_update',
                            'status': 'ESCALATED'
                        }
                    )
            
    async def broadcast_message(self, msg):
        await self.channel_layer.group_send(
            self.support_group_name,
            {
                'type': 'support_message_broadcast',
                'sender_type': msg.sender_type,
                'sender_name': msg.sender_user.username if msg.sender_user else 'System Assistant',
                'message': msg.message,
                'options': msg.options_snapshot,
                'created_at': msg.created_at.isoformat()
            }
        )

    async def support_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'support_message',
            'sender_type': event['sender_type'],
            'sender_name': event['sender_name'],
            'message': event['message'],
            'options': event['options'],
            'created_at': event['created_at']
        }))
        
    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status']
        }))