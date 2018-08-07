from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from imagekit.admin import AdminThumbnail

from .models import (ForumUser, ForumSection, ForumBoard, ForumThread, ForumPost, ForumPostEdit, ForumLastRead,
                     BBCodeImage)


class ForumUserInline(admin.StackedInline):
    model = ForumUser
    can_delete = False
    verbose_name = 'profile'
    verbose_name_plural = 'profile'
    admin_thumbnail = AdminThumbnail(image_field='avatar_thumbnail')
    readonly_fields = ('admin_thumbnail', )


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'last_login', 'date_joined', 'is_staff')
    inlines = (ForumUserInline, )


class BBCodeImageAdmin(admin.ModelAdmin):
    list_display = ('source_url', 'created_at', 'admin_thumbnail')
    admin_thumbnail = AdminThumbnail(image_field='small')
    readonly_fields = ('admin_thumbnail', )


class ForumSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sort_index', 'deleted')
    search_fields = ('title',)


class ForumBoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'section', 'title', 'description', 'sort_index', 'deleted')
    search_fields = ('title',)


class ForumPostEditInlineAdmin(admin.TabularInline):
    model = ForumPostEdit
    extra = 0


class ForumPostInlineAdmin(admin.TabularInline):
    model = ForumPost
    extra = 0


class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'user', 'title', 'created_at', 'modified_at', 'sticky', 'closed', 'deleted')
    inlines = [ForumPostInlineAdmin]
    search_fields = ('title', )


class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'user', 'created_at', 'deleted')
    inlines = [ForumPostEditInlineAdmin]


class ForumLastReadAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'user', 'created_at')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Everything else
admin.site.register(BBCodeImage, BBCodeImageAdmin)
admin.site.register(ForumLastRead, ForumLastReadAdmin)
admin.site.register(ForumPost, ForumPostAdmin)
admin.site.register(ForumThread, ForumThreadAdmin)
admin.site.register(ForumBoard, ForumBoardAdmin)
admin.site.register(ForumSection, ForumSectionAdmin)
