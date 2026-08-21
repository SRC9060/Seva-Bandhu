from django.conf import settings


def firebase_config(request):
    return {
        'firebase_config': {
            'api_key': settings.FIREBASE_API_KEY,
            'auth_domain': settings.FIREBASE_AUTH_DOMAIN,
            'project_id': settings.FIREBASE_PROJECT_ID,
            'storage_bucket': settings.FIREBASE_STORAGE_BUCKET,
            'messaging_sender_id': settings.FIREBASE_MESSAGING_SENDER_ID,
            'app_id': settings.FIREBASE_APP_ID,
        }
    }
