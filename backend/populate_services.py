import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seva_bandhu.settings')
django.setup()

from core.models import Service

# The services in the picture
services_data = [
    {'name': 'AC Repair', 'price': 500},
    {'name': 'Cleaning', 'price': 500},
    {'name': 'Electrical', 'price': 500},
    {'name': 'Plumbing', 'price': 500}
]

# Clear existing test services if needed? The user might have created them, let's just get_or_create to be safe
for s in services_data:
    obj, created = Service.objects.get_or_create(
        name=s['name'],
        defaults={'price': s['price'], 'is_enabled': True}
    )
    if not created:
        obj.price = int(s['price'])
        obj.is_enabled = True
        obj.save()
    print(f"Service {obj.name} processed.")

print('All services populated successfully!')
