from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt


register = template.Library()
_markdown = MarkdownIt("commonmark", {"html": False})


@register.filter
def render_markdown(value):
    """Render CommonMark while escaping raw HTML from the AI response."""
    if not isinstance(value, str):
        return ""
    return mark_safe(_markdown.render(value))
