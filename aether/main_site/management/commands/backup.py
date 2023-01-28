import os
import tarfile
import time
from datetime import datetime
from io import BytesIO, TextIOWrapper

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-d", "--dir", dest="dir", type=str, help="Output directory")

    @staticmethod
    def generate_db_backup(tar):
        fd = BytesIO()
        wrapper = TextIOWrapper(
            fd,
            encoding="utf-8",
            write_through=True,
        )
        call_command("dumpdata", "auth", "forum", "gallery", "main_site", "-a", "-v2", stdout=wrapper)
        tarinfo = tarfile.TarInfo("database.json")
        fd.seek(0, os.SEEK_END)
        tarinfo.size = fd.tell()
        fd.seek(0)
        tarinfo.uname = "www-data"
        tarinfo.gname = "www-data"
        tarinfo.mtime = time.time()
        tar.addfile(tarinfo, fd)

    def handle(self, *args, **options):
        output_dir = options["dir"]
        filename = os.path.join(output_dir, f"{datetime.now():aether_backup_%Y-%m-%d_%H-%M-%S}.tar.gz")
        print(f"Saving to {filename}")

        with tarfile.open(filename, mode="w:gz") as tar:
            self.generate_db_backup(tar)
            tar.add(settings.MEDIA_ROOT, arcname=os.path.basename(settings.MEDIA_ROOT))
