import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(text):
    if not text:
        return ""
    # Use extensions for better rendering (tables, code highlighting, etc.)
    return mark_safe(markdown.markdown(text, extensions=['extra', 'codehilite', 'toc']))
