from django.conf import settings


def modo_publico(request):
    return {"PUBLIC_DEMO_MODE": settings.PUBLIC_DEMO_MODE}
