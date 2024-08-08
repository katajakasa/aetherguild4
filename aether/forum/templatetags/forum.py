from django import template

register = template.Library()


@register.filter
def sections_readable_by(items, user):
    return [x for x in items if x.can_read(user)]


@register.filter
def boards_readable_by(section, user):
    boards = [x for x in section.visible_boards(user) if x.can_read(user)]
    latest_posts = section.get_latest_posts([x.latest_post_id for x in boards])
    for board in boards:
        if board.latest_post_id is None:
            board.latest_post = None
        else:
            board.latest_post = latest_posts[board.latest_post_id]  # Hacketyhack
    return boards


@register.filter
def page_for(item, user):
    return item.page_for(user, item.post_count)


@register.filter
def dict_get(d: dict, item: str):
    return d.get(item)
