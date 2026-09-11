import json
from django.utils import timezone
from core.models import TechnicianSupportMessage, TechnicianSupportTicket, ServiceRequest, TechnicianWalletTransaction, WithdrawalRequest, Incentive

# Predefined Decision Tree
SUPPORT_TREE = {
    'start': {
        'message': "Hi! How can we help you today?",
        'options': [
            {'label': 'Payment / Earnings', 'value': 'payment_start'},
            {'label': 'Service / Booking', 'value': 'service_start'},
            {'label': 'Wallet / Withdrawal', 'value': 'wallet_start'},
            {'label': 'Incentive / Reward', 'value': 'incentive_start'},
            {'label': 'App / Technical Issue', 'value': 'app_start'},
            {'label': 'Account / Profile', 'value': 'account_start'},
            {'label': 'Other', 'value': 'other_start'},
        ]
    },
    
    # -----------------------------
    # PAYMENT / EARNINGS
    # -----------------------------
    'payment_start': {
        'message': "What problem are you facing with your earnings?",
        'options': [
            {'label': 'Missing earnings', 'value': 'payment_specific_service'},
            {'label': 'Payment delayed', 'value': 'payment_specific_service'},
            {'label': 'Completed service not credited', 'value': 'payment_specific_service'},
            {'label': 'Incorrect earnings', 'value': 'payment_specific_service'},
            {'label': 'Other payment issue', 'value': 'other_start'},
        ]
    },
    'payment_specific_service': {
        'message': "Which specific service is this about?",
        'context_type': 'recent_services',
        'next_node': 'payment_troubleshoot_1',
    },
    'payment_troubleshoot_1': {
        'message': "Please check whether the service is marked as 'Completed' and verify your Wallet -> Earnings section. Did this solve your problem?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'payment_troubleshoot_2'},
        ]
    },
    'payment_troubleshoot_2': {
        'message': "If the service is completed, the payment might take up to 24 hours to process into your wallet. If it has been more than 24 hours, check your transaction history. Did this solve it?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },
    
    # -----------------------------
    # SERVICE / BOOKING
    # -----------------------------
    'service_start': {
        'message': "What is the issue with the service/booking?",
        'options': [
            {'label': 'Booking issue', 'value': 'service_specific_service'},
            {'label': 'Customer issue', 'value': 'service_specific_service'},
            {'label': 'Cancellation issue', 'value': 'service_specific_service'},
            {'label': 'Other', 'value': 'other_start'},
        ]
    },
    'service_specific_service': {
        'message': "Please select the service/booking this is about.",
        'context_type': 'recent_services',
        'next_node': 'service_troubleshoot_1',
    },
    'service_troubleshoot_1': {
        'message': "For booking issues, please ensure you have checked the customer's contact details and location. If the customer is unresponsive, you can cancel it with 'Customer Unavailable' reason. Did this solve it?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },
    
    # -----------------------------
    # WALLET / WITHDRAWAL
    # -----------------------------
    'wallet_start': {
        'message': "What is the issue with your wallet or withdrawal?",
        'options': [
            {'label': 'Wallet balance incorrect', 'value': 'wallet_troubleshoot_1'},
            {'label': 'Withdrawal pending', 'value': 'withdrawal_specific'},
            {'label': 'Withdrawal failed', 'value': 'withdrawal_specific'},
            {'label': 'Other', 'value': 'other_start'},
        ]
    },
    'wallet_troubleshoot_1': {
        'message': "Please verify all your completed jobs in the 'My Jobs' section against the transaction history in your wallet. Sometimes deductions are made for penalties. Did this solve your issue?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },
    'withdrawal_specific': {
        'message': "Which withdrawal request is this about?",
        'context_type': 'recent_withdrawals',
        'next_node': 'withdrawal_troubleshoot_1',
    },
    'withdrawal_troubleshoot_1': {
        'message': "Withdrawals can take up to 2-3 business days depending on the bank. If it failed, please check if your bank details are correct. Did this solve it?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },

    # -----------------------------
    # INCENTIVE / REWARD
    # -----------------------------
    'incentive_start': {
        'message': "What is the issue with your incentive or reward?",
        'options': [
            {'label': 'Incentive not credited', 'value': 'incentive_specific'},
            {'label': 'Progress incorrect', 'value': 'incentive_specific'},
            {'label': 'Other', 'value': 'other_start'},
        ]
    },
    'incentive_specific': {
        'message': "Which incentive is this regarding?",
        'context_type': 'recent_incentives',
        'next_node': 'incentive_troubleshoot_1',
    },
    'incentive_troubleshoot_1': {
        'message': "Incentives are usually credited at the end of the week or after the specific threshold is fully met and verified. Did this clarify your issue?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },

    # -----------------------------
    # APP / TECHNICAL ISSUE
    # -----------------------------
    'app_start': {
        'message': "What technical issue are you facing?",
        'options': [
            {'label': 'App not loading properly', 'value': 'app_troubleshoot_1'},
            {'label': 'GPS / Tracking issue', 'value': 'app_troubleshoot_1'},
            {'label': 'Notification issue', 'value': 'app_troubleshoot_1'},
            {'label': 'Other technical problem', 'value': 'other_start'},
        ]
    },
    'app_troubleshoot_1': {
        'message': "Please try logging out and logging back in, or reinstalling the app. Make sure Location services are enabled. Did this resolve the issue?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },

    # -----------------------------
    # ACCOUNT / PROFILE
    # -----------------------------
    'account_start': {
        'message': "What account issue are you facing?",
        'options': [
            {'label': 'Profile information update', 'value': 'account_troubleshoot_1'},
            {'label': 'Account status/warning', 'value': 'account_troubleshoot_1'},
            {'label': 'Other', 'value': 'other_start'},
        ]
    },
    'account_troubleshoot_1': {
        'message': "If your account is warned, please ensure you complete all accepted services. Profile details can be updated in the Account section. Did this resolve it?",
        'options': [
            {'label': '✅ Problem Solved', 'value': 'solved'},
            {'label': '❌ Still Having Problem', 'value': 'auto_escalate'},
        ]
    },

    # -----------------------------
    # OTHER
    # -----------------------------
    'other_start': {
        'message': "Please describe your issue below, or click Contact Admin to speak with our support team.",
        'options': [
            {'label': 'Contact Admin', 'value': 'escalate_confirm'}
        ]
    },
    
    # -----------------------------
    # ESCALATION
    # -----------------------------
    'auto_escalate': {
        'message': "We couldn't resolve this automatically. Would you like to contact an Admin?",
        'options': [
            {'label': 'Contact Admin', 'value': 'escalate_confirm'},
            {'label': 'Continue Troubleshooting (Restart)', 'value': 'start'},
        ]
    },
    'escalate_confirm': {
        'message': "Your request has been sent to Admin Support. An Admin will respond here.",
        'options': [] # Triggers escalation in process_action
    },
    'solved': {
        'message': "Great! We're glad we could help. If you need anything else, feel free to start a new support chat.",
        'options': []
    }
}


class SupportFlowService:

    @staticmethod
    def get_initial_node():
        return 'start'

    @staticmethod
    def process_action(session, action_value, technician, context_id=None):
        """
        Process the action from the user and advance the state.
        Returns a dictionary containing the new system message and options.
        """
        
        # 1. Handle Escape Hatch explicitly (user always has a Contact Admin button)
        if action_value == 'contact_admin':
            return SupportFlowService._escalate(session, technician)
            
        # 2. Check current state context requirement
        current_node = session.flow_state.get('current_node', 'start')
        
        # If the action is a context selection (e.g. they clicked a specific service request)
        if context_id and action_value.startswith('context_'):
            # The action_value might be "context_recent_services"
            context_type = action_value.replace('context_', '')
            SupportFlowService._save_context(session, context_type, context_id, technician)
            
            # Find the next node from the current node's config
            node_config = SUPPORT_TREE.get(current_node)
            next_node_id = node_config.get('next_node', 'start') if node_config else 'start'
            action_value = next_node_id

        # 3. Handle standard state transition
        if action_value not in SUPPORT_TREE:
            # Fallback
            action_value = 'start'

        node = SUPPORT_TREE[action_value]
        
        # Update session state
        session.flow_state['current_node'] = action_value
        session.save()

        # Handle terminal states
        if action_value == 'escalate_confirm':
            return SupportFlowService._escalate(session, technician)
        
        if action_value == 'solved':
            session.status = 'SOLVED'
            session.completed_at = timezone.now()
            session.save()
            return {
                'message': node['message'],
                'options': [],
                'is_terminal': True
            }

        # 4. Generate options
        raw_options = node.get('options', [])
        options = raw_options.copy() if isinstance(raw_options, list) else []
        
        # If node requires context selection, inject dynamic options
        if 'context_type' in node:
            dynamic_options = SupportFlowService._get_context_options(node['context_type'], technician)
            options.extend(dynamic_options)
            
        # Contact Admin escape path removed to allow bot to resolve issues first
        # However, we must prevent dead ends. If no options are available (e.g. empty context), provide a fallback.
        if not options:
            options.append({'label': 'I need more help / None found', 'value': 'auto_escalate'})
        return {
            'message': node['message'],
            'options': options,
            'is_terminal': False
        }

    @staticmethod
    def _escalate(session, technician):
        """Handle the actual escalation logic."""
        session.status = 'ESCALATED'
        session.save()
        
        # Create the ticket
        import uuid
        ticket_id = f"#TS-{str(uuid.uuid4().int)[:6]}"
        
        # Determine category and issue from state if possible
        # (This is basic; could be improved by tracking selected labels)
        state_node = session.flow_state.get('current_node', 'start')
        
        ticket = TechnicianSupportTicket.objects.create(
            session=session,
            ticket_id=ticket_id,
            category="Support Escalation",
            issue=f"Escalated at step: {state_node}",
            priority='MEDIUM',
            status='OPEN'
        )
        
        return {
            'message': SUPPORT_TREE['escalate_confirm']['message'],
            'options': [],
            'is_terminal': False,
            'escalated': True,
            'ticket': ticket
        }

    @staticmethod
    def _save_context(session, context_type, context_id, technician):
        """Securely verify and attach the selected context to the session."""
        try:
            if context_type == 'recent_services':
                req = ServiceRequest.objects.get(id=context_id, technician_username=technician.user.username)
                session.related_service_request = req
            elif context_type == 'recent_withdrawals':
                req = WithdrawalRequest.objects.get(id=context_id, technician=technician)
                session.related_withdrawal = req
            elif context_type == 'recent_incentives':
                req = Incentive.objects.get(id=context_id) # Incentives are global, awards are specific
                session.related_incentive = req
            session.save()
        except Exception:
            pass # Ignore invalid IDs - don't let frontend forge them

    @staticmethod
    def _get_context_options(context_type, technician):
        """Fetch records securely to present as inline chat options."""
        options = []
        if context_type == 'recent_services':
            # Fetch last 5 jobs
            jobs = ServiceRequest.objects.filter(technician_username=technician.user.username).order_by('-created_at')[:5]
            for job in jobs:
                options.append({
                    'label': f"Job #{job.id} - {job.service_detail.service_category} ({job.status})",
                    'value': f"context_recent_services", 
                    'context_id': job.id,
                    'is_context': True
                })
        elif context_type == 'recent_withdrawals':
            reqs = WithdrawalRequest.objects.filter(technician=technician).order_by('-requested_at')[:5]
            for req in reqs:
                options.append({
                    'label': f"Withdrawal {req.amount} ({req.status})",
                    'value': f"context_recent_withdrawals",
                    'context_id': req.id,
                    'is_context': True
                })
        elif context_type == 'recent_incentives':
            reqs = Incentive.objects.filter(is_active=True).order_by('-created_at')[:5]
            for req in reqs:
                options.append({
                    'label': f"Incentive: {req.name}",
                    'value': f"context_recent_incentives",
                    'context_id': req.id,
                    'is_context': True
                })
        return options
