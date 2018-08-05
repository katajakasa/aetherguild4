import hashlib
from collections import OrderedDict

from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext_noop as _

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash


class CustomSHA256PasswordHasher(BasePasswordHasher):
    algorithm = "sha256"

    def encode(self, password, salt):
        assert password is not None
        assert salt and '$' not in salt
        hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

    def verify(self, password, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt)
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return OrderedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])

    def harden_runtime(self, password, encoded):
        pass
