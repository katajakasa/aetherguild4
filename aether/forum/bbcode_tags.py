from precise_bbcode.tag_pool import tag_pool
from precise_bbcode.bbcode.tag import BBCodeTag
from urllib.parse import urlparse, parse_qs


class YoutubeTag(BBCodeTag):
    name = 'youtube'

    class Options:
        strip = True
        replace_links = False
        transform_newlines = False
        render_embedded = False
        swallow_trailing_newline = True

    @staticmethod
    def parse_youtube_video_id(value):
        query = urlparse(value)
        if query.scheme == '' and query.netloc == '':
            return query.path
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                if not p.get('v'):
                    return None
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        return None

    def render(self, value, option=None, parent=None):
        code = self.parse_youtube_video_id(value)
        return """
        <div class="embed-responsive embed-responsive-16by9">
            <iframe class="embed-responsive-item" src="https://www.youtube.com/embed/{}?rel=0" allowfullscreen></iframe>
        </div>
        """.format(code)


class ImageTag(BBCodeTag):
    name = 'img'

    class Options:
        replace_links = False

    def render(self, value, option=None, parent=None):
        return '<img src="{}" />'.format(value)


class UlListTag(BBCodeTag):
    name = 'ul'
    definition_string = '[ul]{TEXT}[/ul]'
    format_string = '<ul>{TEXT}</ul>'

    class Options:
        strip = True
        swallow_trailing_newline = True


class OlListTag(BBCodeTag):
    name = 'ol'
    definition_string = '[ol]{TEXT}[/ol]'
    format_string = '<ol>{TEXT}</ol>'

    class Options:
        strip = True
        swallow_trailing_newline = True


class ListItemTag(BBCodeTag):
    name = 'li'
    definition_string = '[li]{TEXT}[/li]'
    format_string = '<li>{TEXT}</li>'

    class Options:
        strip = True
        swallow_trailing_newline = True


class CodeTag(BBCodeTag):
    name = 'code'
    definition_string = '[code]{TEXT}[/code]'
    format_string = '<pre class="bbcode-code"><code>{TEXT}</code></pre>'

    class Options:
        strip = True
        swallow_trailing_newline = True


class QuoteTag(BBCodeTag):
    name = 'quote'

    class Options:
        strip = True
        swallow_trailing_newline = True

    def render(self, value, option=None, parent=None):
        if option:
            return """
                <div class="bbcode-quote">
                    <p class="mb-0">{}</p>
                    <footer class="blockquote-footer">{}</footer>
                </div>""".format(value, option)
        else:
            return """
                <div class="bbcode-quote">
                    <p class="mb-0">{}</p>
                </div>""".format(value)


tag_pool.register_tag(YoutubeTag)
tag_pool.register_tag(OlListTag)
tag_pool.register_tag(UlListTag)
tag_pool.register_tag(ListItemTag)
tag_pool.register_tag(QuoteTag)
tag_pool.register_tag(CodeTag)

