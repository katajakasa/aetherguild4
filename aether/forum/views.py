from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.db.models import F
from django.contrib.auth.decorators import login_required, permission_required
from .models import ForumBoard, ForumSection, ForumThread, ForumLastRead, ForumPost
from .forms import NewThreadForm, NewMessageForm, MoveThreadForm, EditMessageForm
from aether.utils.misc import get_page


def boards(request):
    sections = ForumSection.objects.filter(deleted=False).prefetch_related('boards').order_by('sort_index')
    return render(request, 'forum/boards.html', {
        'sections': sections
    })


def threads(request, board_id):
    board = get_object_or_404(ForumBoard, pk=board_id, deleted=False)
    if not board.can_read(request.user):
        raise Http404

    if request.method == 'POST':
        if not request.user.is_authenticated:
            raise Http404
        if not board.can_write(request.user):
            raise Http404
        form = NewThreadForm(request.POST)
        if form.is_valid():
            thread, post = form.save(board=board, user=request.user)
            return HttpResponseRedirect(reverse('forum:posts', args=(board.id, thread.id)))
    else:
        form = NewThreadForm()

    show_count = request.user.profile.thread_limit if request.user.is_authenticated else settings.FORUM_THREAD_LIMIT
    paginator = Paginator(board.visible_threads, show_count)
    page = get_page(request)

    return render(request, 'forum/threads.html', {
        'board': board,
        'threads': paginator.get_page(page),
        'can_manage': request.user.has_perm('forum.can_manage_boards'),
        'can_write': board.can_write(request.user),
        'form': form
    })


def posts(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, deleted=False)
    if not thread.board.can_read(request.user):
        raise Http404

    if request.method == 'POST':
        if not request.user.is_authenticated:
            raise Http404
        if not thread.board.can_write(request.user):
            raise Http404
        if thread.closed:
            raise Http404
        form = NewMessageForm(request.POST)
        if form.is_valid():
            thread, post = form.save(thread=thread, user=request.user)
            return HttpResponseRedirect("{}?page={}#{}".format(
                reverse('forum:posts', args=(thread.board.id, thread.id)),
                post.page_for(request.user),
                post.id
            ))
    else:
        form = NewMessageForm()

    # Refresh last viewed values for this user/thread
    if request.user.is_authenticated:
        ForumLastRead.refresh_last_read(request.user, thread)

    # Update the views counter atomically
    ForumThread.objects.filter(pk=thread.pk).update(views=F('views')+1)

    show_count = request.user.profile.message_limit if request.user.is_authenticated else settings.FORUM_MESSAGE_LIMIT
    paginator = Paginator(thread.visible_posts, show_count)
    page = get_page(request)

    return render(request, 'forum/posts.html', {
        'thread': thread,
        'form': form,
        'posts': paginator.get_page(page),
        'can_manage': request.user.has_perm('forum.can_manage_boards'),
        'can_write': thread.board.can_write(request.user)
    })


@login_required
def edit_post(request, board_id, thread_id, post_id):
    post = get_object_or_404(ForumPost, pk=post_id, thread_id=thread_id, deleted=False)
    thread = post.thread

    # User must be either admin or owner of the post
    # User must have write rights to the board
    # Thread must not be locked
    if not (request.user.has_perm('forum.can_manage_boards') or post.user.id == request.user.id):
        raise Http404
    if not thread.board.can_write(request.user):
        raise Http404
    if thread.closed:
        raise Http404

    if request.method == 'POST':
        form = EditMessageForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("{}?page={}#{}".format(
                reverse('forum:posts', args=(thread.board.id, thread.id)),
                post.page_for(request.user),
                post.id
            ))
    else:
        form = EditMessageForm(instance=post)

    return render(request, 'forum/edit_post.html', {
        'thread': thread,
        'post': post,
        'form': form
    })


@login_required
@permission_required('forum.can_manage_boards')
def toggle_sticky(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)
    thread.sticky = not thread.sticky
    thread.save()
    return HttpResponseRedirect(reverse('forum:threads', args=(board_id,)))


@login_required
@permission_required('forum.can_manage_boards')
def toggle_closed(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)
    thread.closed = not thread.closed
    thread.save()
    return HttpResponseRedirect(reverse('forum:threads', args=(board_id,)))


@login_required
@permission_required('forum.can_manage_boards')
def delete_thread(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)
    thread.deleted = True
    thread.save()
    return HttpResponseRedirect(reverse('forum:threads', args=(board_id,)))


@login_required
@permission_required('forum.can_manage_boards')
def move_thread(request, board_id, thread_id):
    thread = get_object_or_404(ForumThread, pk=thread_id, board_id=board_id, deleted=False)

    if request.method == 'POST':
        form = MoveThreadForm(request.POST, instance=thread)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(reverse('forum:threads', args=(obj.board.id, )))
    else:
        form = MoveThreadForm()

    return render(request, 'forum/move_thread.html', {'form': form, 'thread': thread})
