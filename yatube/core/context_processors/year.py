from django.utils import timezone


def year(request):
    tz = timezone.now().year
    return {
        'year': tz
    }
