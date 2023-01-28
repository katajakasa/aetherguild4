from django.contrib.auth.models import Permission, User


def has_perm_obj(user: User, perm: Permission):
    key = perm.natural_key()
    codename = "{}.{}".format(key[1], key[0])
    return user.has_perm(codename)
