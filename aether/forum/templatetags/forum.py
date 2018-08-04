from django import template

register = template.Library()


@register.filter
def readable_by(items, user):
    return (x for x in items if x.can_read(user))


@register.filter
def page_for(item, user):
    return item.page_for(user)
