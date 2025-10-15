from .models import MpgService, MpgBlog

def global_context(request):
    """
    Provides global context to all templates, specifically for the footer.
    """
    try:
        latest_services_footer = MpgService.objects.filter(is_active=True).order_by('-created_at')[:4]
        latest_blogs_footer = MpgBlog.objects.filter(is_published=True).order_by('-posted_date')[:4]
    except Exception:
        latest_services_footer = []
        latest_blogs_footer = []
        
    return {
        'latest_services_footer': latest_services_footer,
        'latest_blogs_footer': latest_blogs_footer,
    }
