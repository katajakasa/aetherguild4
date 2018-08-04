from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.boards, name='boards'),
    path('<int:board_id>/', views.threads, name='threads'),
    path('<int:board_id>/<int:thread_id>/', views.posts, name='posts'),
    path('<int:board_id>/<int:thread_id>/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:board_id>/<int:thread_id>/move/', views.move_thread, name='move_thread'),
    path('<int:board_id>/<int:thread_id>/delete/', views.delete_thread, name='delete_thread'),
    path('<int:board_id>/<int:thread_id>/toggle_closed/', views.toggle_closed, name='toggle_closed'),
    path('<int:board_id>/<int:thread_id>/toggle_sticky/', views.toggle_sticky, name='toggle_sticky'),
]
