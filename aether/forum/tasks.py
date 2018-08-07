import logging
import os
import io
from urllib import parse
from tempfile import NamedTemporaryFile

from PIL import Image
import requests
from requests.exceptions import ConnectionError
from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.contrib.contenttypes.models import ContentType

from aether.forum.models import BBCodeImage, ForumPost, ForumUser
from aether.main_site.models import NewsItem


log = logging.getLogger('tasks')


class DownloadFailedException(Exception):
    pass


class ImageVerificationException(Exception):
    pass


def fetch_url_to_file(fd, url):
    with requests.get(url, stream=True) as r:
        # Make sure response code is okay
        if r.status_code != requests.codes.ok:
            raise DownloadFailedException("Unexpected response code %d", r.status_code)

        # Make sure that the reported content length is smaller than maximum
        if 'content-length' in r.headers:
            image_size = int(r.headers['content-length'])
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


def verify_image(fd):
    try:
        img = Image.open(io.BytesIO(fd.read()))
        img.load()
        img.close()
        fd.seek(0)
    except Image.DecompressionBombError as e:
        raise ImageVerificationException("Decompression bomb detected!") from e
    except Exception as e:
        raise ImageVerificationException("Failed to open imagefile") from e


@shared_task
def cache_bbcode_image(url):
    log.info("Attempting to fetch {}".format(url))
    p = parse.urlparse(url)

    # Ensure that the url seems okay
    if p.scheme not in ['http', 'https']:
        log.error("Unknown scheme %s", p.scheme, extra={'url': url})
        return

    # Make sure the file extension is supported
    ext = os.path.splitext(p.path)[1][1:]
    if ext not in settings.BBCODE_CACHE_IMAGE_FORMATS:
        log.error("Unknown file extension: %s", ext, extra={'url': url})
        return

    # Read content to a file. Spool to memory until 2M, then write to disk.
    with NamedTemporaryFile() as fd:
        # Download with requests
        try:
            fetch_url_to_file(fd, url)
        except (DownloadFailedException, ConnectionError):
            log.exception("Unable to download source image", extra={'url': url})
            return

        # Verify with Pillow
        try:
            verify_image(fd)
        except ImageVerificationException:
            log.exception("Failed to verify image", extra={'url': url})
            return

        # That's that, write to django model + filesystem
        entry = BBCodeImage()
        entry.source_url = url
        entry.original = File(fd, name=os.path.basename(p.path))
        entry.save()

        # Download part is done
        log.info("Downloaded to %s.", entry.original.name)


@shared_task
def postprocess(app, model, id):
    content_type = ContentType.objects.get(app_label=app, model=model)
    log.info(content_type)
