from django.contrib.auth.models import Permission, User
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    Model,
    TextField,
)
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from precise_bbcode.fields import BBCodeTextField

from aether.utils.misc import utc_now


class GalleryGroup(Model):
    name = CharField(max_length=32, null=False, blank=False)
    description = BBCodeTextField(null=False, blank=True)
    created_at = DateTimeField(default=utc_now, null=False, db_index=True)

    def __str__(self) -> str:
        return self.name

    @property
    def sorted_images(self):
        return self.images.order_by("created_at").all()

    class Meta:
        app_label = "gallery"
        verbose_name = "Gallery Group"
        verbose_name_plural = "Gallery Groups"


class GalleryImage(Model):
    group = ForeignKey(GalleryGroup, null=False, on_delete=CASCADE, related_name="images")
    created_at = DateTimeField(default=utc_now, null=False, db_index=True)
    name = CharField(max_length=32, null=False, blank=False)
    original = ImageField(upload_to="gallery", null=False)
    thumbnail = ImageSpecField(
        source="original", processors=[ResizeToFit(width=200, height=200, upscale=True)], format="PNG"
    )

    def __str__(self) -> str:
        return "{}: {}".format(self.group.name, self.name)

    class Meta:
        app_label = "gallery"
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
