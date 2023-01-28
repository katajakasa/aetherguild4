from urllib.parse import parse_qs, urlparse

from precise_bbcode.bbcode.tag import BBCodeTag
from precise_bbcode.tag_pool import tag_pool

from aether.forum.models import BBCodeImage


class YoutubeTag(BBCodeTag):
    name = "youtube"

    class Options:
        strip = True
        replace_links = False
        transform_newlines = False
        render_embedded = False
        swallow_trailing_newline = True

    @staticmethod
    def parse_youtube_video_id(value):
        query = urlparse(value)
        if query.scheme == "" and query.netloc == "":
            return query.path
        if query.hostname == "youtu.be":
            return query.path[1:]
        if query.hostname in ("www.youtube.com", "youtube.com"):
            if query.path == "/watch":
                p = parse_qs(query.query)
                if not p.get("v"):
                    return None
                return p["v"][0]
            if query.path[:7] == "/embed/":
                return query.path.split("/")[2]
            if query.path[:3] == "/v/":
                return query.path.split("/")[2]
        return None

    def render(self, value, option=None, parent=None):
        code = self.parse_youtube_video_id(value)
        return """
        <div class="embed-responsive embed-responsive-16by9">
            <iframe class="embed-responsive-item" src="https://www.youtube.com/embed/{}?rel=0" allowfullscreen></iframe>
        </div>
        """.format(
            code
        )


class ImageTag(BBCodeTag):
    name = "img"

    class Options:
        replace_links = False

    def render(self, value, option=None, parent=None):
        url = value.strip()
        entry = BBCodeImage.objects.filter(source_url=url).first()
        medium_url = entry.medium.url if entry else url
        original_url = entry.original.url if entry else url
        return '<a href="{}" data-featherlight="image" class="fl-image"><img src="{}" /></a>'.format(
            original_url, medium_url
        )


class UlListTag(BBCodeTag):
    name = "ul"
    definition_string = "[ul]{TEXT}[/ul]"
    format_string = "<ul>{TEXT}</ul>"

    class Options:
        strip = True
        swallow_trailing_newline = True


class OlListTag(BBCodeTag):
    name = "ol"
    definition_string = "[ol]{TEXT}[/ol]"
    format_string = "<ol>{TEXT}</ol>"

    class Options:
        strip = True
        swallow_trailing_newline = True


class ListItemTag(BBCodeTag):
    name = "li"
    definition_string = "[li]{TEXT}[/li]"
    format_string = "<li>{TEXT}</li>"

    class Options:
        strip = True
        swallow_trailing_newline = True


class CodeTag(BBCodeTag):
    name = "code"
    definition_string = "[code]{TEXT}[/code]"
    format_string = '<pre class="bbcode-code"><code>{TEXT}</code></pre>'

    class Options:
        strip = True
        swallow_trailing_newline = True


class QuoteTag(BBCodeTag):
    name = "quote"

    class Options:
        strip = True
        swallow_trailing_newline = True

    def render(self, value, option=None, parent=None):
        if option:
            return """
                <div class="bbcode-quote">
                    <p class="mb-0">{}</p>
                    <footer class="blockquote-footer">{}</footer>
                </div>""".format(
                value, option
            )
        else:
            return """
                <div class="bbcode-quote">
                    <p class="mb-0">{}</p>
                </div>""".format(
                value
            )


tag_pool.register_tag(ImageTag)
tag_pool.register_tag(YoutubeTag)
tag_pool.register_tag(OlListTag)
tag_pool.register_tag(UlListTag)
tag_pool.register_tag(ListItemTag)
tag_pool.register_tag(QuoteTag)
tag_pool.register_tag(CodeTag)
