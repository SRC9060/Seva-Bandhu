import json

code = """

def customer_support_tickets(request):
    if not request.user.is_authenticated:
        return redirect('customer_login')
    
    try:
        customer = customer_signup.objects.filter(user=request.user).first()
        if not customer:
            return redirect('customer_login')
    except Exception:
        return redirect('customer_login')
        
    from core.models import SupportTicket
    tickets = SupportTicket.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'customer/support_tickets_c.html', {'support_tickets': tickets})

@csrf_exempt
def customer_api_create_ticket(request):
    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body)
            ticket_type = data.get('ticket_type')
            description = data.get('description')
            technician_name = data.get('technician_name', '')
            service_request_id = data.get('service_request_id', '')

            if not request.user.is_authenticated:
                return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
                
            customer = customer_signup.objects.filter(user=request.user).first()
            if not customer:
                return JsonResponse({'status': 'error', 'message': 'Customer not found'}, status=404)
            
            from core.models import SupportTicket
            SupportTicket.objects.create(
                customer=customer,
                ticket_type=ticket_type,
                description=description,
                technician_name=technician_name,
                service_request_id=service_request_id,
                status='Open'
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
"""

with open('backend/core/views.py', 'a', encoding='utf-8') as f:
    f.write(code)
print('Appended missing views!')
