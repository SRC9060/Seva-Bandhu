from django.conf import settings


def firebase_config(request):
    firebase_config = getattr(settings, 'FIREBASE_CONFIG', {})
    return {
        'firebase_config': {
            'api_key': firebase_config.get('api_key', ''),
            'auth_domain': firebase_config.get('auth_domain', ''),
            'project_id': firebase_config.get('project_id', ''),
            'storage_bucket': firebase_config.get('storage_bucket', ''),
            'messaging_sender_id': firebase_config.get('messaging_sender_id', ''),
            'app_id': firebase_config.get('app_id', ''),
        }
    }
