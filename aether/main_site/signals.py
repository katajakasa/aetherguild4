from aether.forum import tasks


def postprocess_newsitem(sender, instance, created, **kwargs):
    tasks.postprocess.apply_async(("newsitem", instance.id))
