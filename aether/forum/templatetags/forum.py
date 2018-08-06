from django import template

register = template.Library()


@register.filter
def sections_readable_by(items, user):
    return [x for x in items if x.can_read(user)]


@register.filter
def boards_readable_by(section, user):
    return [x for x in section.visible_boards(user) if x.can_read(user)]


@register.filter
def page_for(item, user):
    return item.page_for(user, item.post_count)
