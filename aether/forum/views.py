from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import never_cache

from aether.utils.misc import get_page

from .forms import EditMessageForm, MoveThreadForm, NewMessageForm, NewThreadForm
from .models import ForumBoard, ForumLastRead, ForumPost, ForumSection, ForumThread


@never_cache
def boards(request):
    sections = ForumSection.objects.filter(deleted=False).order_by("sort_index")
    return render(request, "forum/boards.html", {"sections": sections})


@never_cache
def threads(request, board_id):
    try:
        board = ForumBoard.objects.select_related(
            "read_perm", "read_perm__content_type", "write_perm", "write_perm__content_type"
        ).get(pk=board_id, deleted=False)
    except ForumBoard.DoesNotExist:
        raise Http404
    if not board.can_read(request.user):
        raise Http404

    if request.method == "POST":
        if not request.user.is_authenticated:
            raise Http404
        if not board.can_write(request.user):
            raise Http404
        form = NewThreadForm(request.POST, user=request.user, board=board)
        if form.is_valid():
            post = form.save()
            return HttpResponseRedirect(reverse("forum:posts", args=(board.id, post.thread.id)))
    else:
        form = NewThreadForm(user=request.user, board=board)

    show_count = (
        request.user.profile.thread_limit if request.user.is_authenticated else settings.FORUM_THREAD_LIMIT
    )
    paginator = Paginator(board.visible_threads(request.user), show_count)
    page = get_page(request)
    thread_list = paginator.get_page(page)
    latest_posts = board.get_latest_posts([x.latest_post_id for x in list(thread_list)])

    return render(
        request,
        "forum/threads.html",
        {
            "board": board,
            "threads": thread_list,
            "latest_posts": latest_posts,
            "can_manage": request.user.has_perm("forum.can_manage_boards"),
            "can_write": board.can_write(request.user),
            "form": form,
        },
    )


@never_cache
def posts(request, board_id, thread_id):
    try:
        thread = ForumThread.objects.select_related(
            "board__read_perm",
            "board__read_perm__content_type",
            "board__write_perm",
            "board__write_perm__content_type",
        ).get(pk=thread_id, deleted=False)
    except ForumThread.DoesNotExist:
        raise Http404
    if not thread.board.can_read(request.user):
        raise Http404

    if request.method == "POST":
        if not request.user.is_authenticated:
            raise Http404
        if not thread.board.can_write(request.user):
            raise Http404
        if thread.closed:
            raise Http404
        form = NewMessageForm(request.POST, thread=thread, user=request.user)
        if form.is_valid():
            post = form.save()
            return HttpResponseRedirect(
                "{}?page={}#{}".format(
                    reverse("forum:posts", args=(thread.board.id, thread.id)),
                    post.page_for(request.user),
                    post.id,
                )
            )
    else:
        form = NewMessageForm(thread=thread, user=request.user)

    # Refresh last viewed values for this user/thread
    if request.user.is_authenticated:
        ForumLastRead.refresh_last_read(request.user, thread)

    # Update the views counter atomically
    ForumThread.objects.filter(pk=thread.pk).update(views=F("views") + 1)

    show_count = (
        request.user.profile.message_limit if request.user.is_authenticated else settings.FORUM_MESSAGE_LIMIT
    )
    paginator = Paginator(thread.visible_posts, show_count)
    page = get_page(request)

    return render(
        request,
        "forum/posts.html",
        {
            "thread": thread,
            "form": form,
            "posts": paginator.get_page(page),
            "can_manage": request.user.has_perm("forum.can_manage_boards"),
            "can_write": thread.board.can_write(request.user),
        },
    )


@login_required
def edit_post(request, board_id, thread_id, post_id):
    post = get_object_or_404(ForumPost, pk=post_id, thread_id=thread_id, deleted=False)
    thread = post.thread
    page = request.GET.get("page", "1")

    # User must be either admin or owner of the post
    # User must have write rights to the board
    if not (request.user.has_perm("forum.can_manage_boards") or post.user.id == request.user.id):
        raise Http404
    if not thread.board.can_write(request.user):
        raise Http404

    if request.method == "POST":
        form = EditMessageForm(request.POST, instance=post, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                "{}?page={}#{}".format(
                    reverse("forum:posts", args=(thread.board.id, thread.id)), page, post.id
                )
            )
    else:
        form = EditMessageForm(instance=post, user=request.user)

    return render(
        request, "forum/edit_post.html", {"thread": thread, "post": post, "form": form, "page": page}
    )


@login_required
@permission_required("forum.can_manage_boards")
def toggle_sticky(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)
    thread.sticky = not thread.sticky
    thread.save()
    return HttpResponseRedirect(reverse("forum:threads", args=(board_id,)))


@login_required
@permission_required("forum.can_manage_boards")
def toggle_closed(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)
    thread.closed = not thread.closed
    thread.save()
    return HttpResponseRedirect(reverse("forum:threads", args=(board_id,)))


@login_required
@permission_required("forum.can_manage_boards")
def delete_thread(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)
    thread.deleted = True
    thread.save()
    return HttpResponseRedirect(reverse("forum:threads", args=(board_id,)))


@login_required
@permission_required("forum.can_manage_boards")
def move_thread(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)

    if request.method == "POST":
        form = MoveThreadForm(request.POST, instance=thread)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(reverse("forum:threads", args=(obj.board.id,)))
    else:
        form = MoveThreadForm()

    return render(request, "forum/move_thread.html", {"form": form, "thread": thread})


@login_required
def mark_all_read(request):
    request.user.profile.mark_all_read(request.user)
    return HttpResponseRedirect(reverse("forum:boards"))
