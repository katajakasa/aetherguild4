from django.contrib import admin
from imagekit.admin import AdminThumbnail

from .models import GalleryGroup, GalleryImage


class GalleryImageInline(admin.StackedInline):
    model = GalleryImage
    admin_thumbnail = AdminThumbnail(image_field="thumbnail")
    readonly_fields = ("admin_thumbnail",)
    extra = 0


class GalleryGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    inlines = (GalleryImageInline,)


# Everything else
admin.site.register(GalleryGroup, GalleryGroupAdmin)
