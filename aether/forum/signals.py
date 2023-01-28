from aether.forum import tasks


def postprocess_forumuser(sender, instance, created, **kwargs):
    tasks.postprocess.apply_async(("forumuser", instance.id))


def postprocess_forumpost(sender, instance, created, **kwargs):
    tasks.postprocess.apply_async(("forumpost", instance.id))
