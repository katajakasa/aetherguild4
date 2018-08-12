import logging
import os
import io
import re
import mimetypes
from urllib import parse
from tempfile import NamedTemporaryFile

from PIL import Image
import requests
from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.db import IntegrityError, transaction
from django.utils import timezone
from precise_bbcode.bbcode import get_parser

from aether.forum.models import BBCodeImage, ForumPost, ForumUser
from aether.main_site.models import NewsItem


log = logging.getLogger('tasks')

mimetypes.init()
match_url = re.compile(r'\[img\](\s*)(.+?)(\s*)\[\/img\]')


class DownloadFailedException(Exception):
    pass


class ImageVerificationException(Exception):
    pass


def fetch_url_to_file(fd, url):
    with requests.get(url, stream=True) as r:
        # Make sure response code is okay
        if r.status_code != requests.codes.ok:
            raise DownloadFailedException("Unexpected response code {}".format(r.status_code))

        # Make sure the reported MIME type is acceptable
        if 'Content-Type' in r.headers:
            content_type = r.headers['Content-Type']
            log.info("Content type is %s", content_type)
            if content_type not in settings.BBCODE_CACHE_IMAGE_MIME_TYPES:
                raise DownloadFailedException("Image type {} is not acceptable".format(content_type))

        # Make sure that the reported content length is smaller than maximum
        if 'Content-Length' in r.headers:
            image_size = int(r.headers['Content-Length'])
            log.info("Content length is %d bytes", image_size)
            if image_size > settings.BBCODE_CACHE_IMAGE_MAX_SIZE:
                raise DownloadFailedException("Imagefile size exceeds maximum of {}".format(
                    settings.BBCODE_CACHE_IMAGE_MAX_SIZE))

        # Read data from remote host to a file, stop and fail if any problems
        done = 0
        for chunk in r.iter_content(chunk_size=4096):
            done += len(chunk)
            if done > settings.BBCODE_CACHE_IMAGE_MAX_SIZE:
                raise DownloadFailedException("Imagefile size exceeds maximum of {}".format(
                    settings.BBCODE_CACHE_IMAGE_MAX_SIZE))
            fd.write(chunk)
        fd.seek(0)


def guess_image_extension(img):
    ext = mimetypes.guess_extension(Image.MIME[img.format])
    if ext == '.jpe':
        ext = '.jpg'
    return ext


def verify_image(fd):
    try:
        img = Image.open(io.BytesIO(fd.read()))
        img.load()
        ext = guess_image_extension(img)
        img.close()
        fd.seek(0)
        return ext
    except Image.DecompressionBombError as e:
        raise ImageVerificationException("Decompression bomb detected!") from e
    except Exception as e:
        raise ImageVerificationException("Failed to open imagefile") from e


def cache_bbcode_image(url):
    log.info("Attempting to fetch {}".format(url))
    p = parse.urlparse(url)

    # Ensure that the url seems okay
    if p.scheme not in ['http', 'https']:
        log.error("Unknown scheme %s", p.scheme, extra={'url': url})
        return False

    # Read content to a file. Spool to memory until 2M, then write to disk.
    with NamedTemporaryFile() as fd:
        # Download with requests
        try:
            fetch_url_to_file(fd, url)
        except Exception as e:
            log.exception("Unable to download source image", extra={'url': url}, exc_info=e)
            return False

        # Verify with Pillow
        try:
            ext = verify_image(fd)
        except Exception as e:
            log.exception("Failed to verify image", extra={'url': url}, exc_info=e)
            return False

        # If this file already exists, overwrite it
        try:
            entry = BBCodeImage.objects.get(source_url=url)
            entry.original.delete()
        except BBCodeImage.DoesNotExist:
            entry = BBCodeImage()
            entry.source_url = url

        # Add extension if one does not exist already
        name = os.path.basename(p.path)
        if name == '':
            name = f'{timezone.now():%Y-%m-%d_%H-%M-%S}'
        if os.path.splitext(name)[1] == '' and ext:
            name = f"{name}{ext}"

        # Add produced file
        entry.original.save(name, File(fd, name), save=False)

        # ... and then save everything
        try:
            entry.save()
        except IntegrityError:
            log.exception("Source url has already been downloaded. Concurrency issue ?")
            return False

    # Download part is done
    log.info("Downloaded to %s.", entry.original.name)
    return True


@transaction.atomic
def postprocess_bbcode_img(model, object_id, field_name):
    obj = model.objects.select_for_update().get(pk=object_id)
    text = getattr(obj, field_name)
    hits = match_url.findall(text.raw)
    urls = set([h[1] for h in hits])
    if urls:
        # Fetch urls to cache
        refresh = False
        for url in urls:
            if cache_bbcode_image(url):
                refresh = True
        if refresh:
            # Re-render bbcode
            model.objects.filter(id=obj.id).update(**{
                '_{}_rendered'.format(field_name): get_parser().render(text.raw)
            })


@shared_task()
def postprocess(object_type, object_id):
    log.info("Postprocessing object type {} with pk={}".format(object_type, object_id))
    if object_type == 'newsitem':
        postprocess_bbcode_img(NewsItem, object_id, 'message')
    elif object_type == 'forumpost':
        postprocess_bbcode_img(ForumPost, object_id, 'message')
    elif object_type == 'forumuser':
        postprocess_bbcode_img(ForumUser, object_id, 'signature')
