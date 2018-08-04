from precise_bbcode.tag_pool import tag_pool
from aether.utils.bbcode import YoutubeTag, ListItemTag, OlListTag, UlListTag, QuoteTag, CodeTag


tag_pool.register_tag(YoutubeTag)
tag_pool.register_tag(OlListTag)
tag_pool.register_tag(UlListTag)
tag_pool.register_tag(ListItemTag)
tag_pool.register_tag(QuoteTag)
tag_pool.register_tag(CodeTag)

