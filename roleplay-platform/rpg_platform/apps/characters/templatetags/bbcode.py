import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import escape
import urllib.parse

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def bbcode(value):
    """
    Convert BBCode to HTML.

    Extended support for:
    [b] - Bold
    [i] - Italic
    [u] - Underline
    [s] - Strikethrough
    [url] - Link
    [color] - Text color
    [size] - Text size
    [font] - Font family
    [align] - Text alignment (center, left, right, justify)
    [quote] - Blockquote
    [list] - Unordered list
    [olist] - Ordered list
    [*] - List item
    [img] - Image
    [code] - Code block
    [table], [tr], [td] - Tables
    [sub] - Subscript
    [sup] - Superscript
    [spoiler] - Spoiler text
    [hr] - Horizontal rule
    [youtube] - YouTube embed
    [vimeo] - Vimeo embed
    [soundcloud] - SoundCloud embed
    [columns] - Columns layout
    [column] - Single column
    [accordion] - Accordion container
    [section] - Accordion section
    [indent] - Text indentation
    [progress] - Progress bar
    [icon] - Font awesome icon
    [map] - Google Maps embed
    [audio] - Audio player
    """
    # Escape HTML first to prevent injection
    value = escape(value)

    # Basic formatting
    value = re.sub(r'\[b\](.*?)\[/b\]', r'<strong>\1</strong>', value, flags=re.DOTALL)
    value = re.sub(r'\[i\](.*?)\[/i\]', r'<em>\1</em>', value, flags=re.DOTALL)
    value = re.sub(r'\[u\](.*?)\[/u\]', r'<u>\1</u>', value, flags=re.DOTALL)
    value = re.sub(r'\[s\](.*?)\[/s\]', r'<del>\1</del>', value, flags=re.DOTALL)

    # URLs
    value = re.sub(r'\[url\](.*?)\[/url\]', r'<a href="\1" target="_blank" rel="noopener nofollow">\1</a>', value, flags=re.DOTALL)
    value = re.sub(r'\[url=(.*?)\](.*?)\[/url\]', r'<a href="\1" target="_blank" rel="noopener nofollow">\2</a>', value, flags=re.DOTALL)

    # Color & Font styling
    value = re.sub(r'\[color=(#[0-9a-fA-F]{3,6}|[a-zA-Z]+)\](.*?)\[/color\]', r'<span style="color:\1">\2</span>', value, flags=re.DOTALL)
    value = re.sub(r'\[size=(\d+)(px|pt|em|rem|%|)\](.*?)\[/size\]', r'<span style="font-size:\1\2">\3</span>', value, flags=re.DOTALL)
    value = re.sub(r'\[font=([^]]+)\](.*?)\[/font\]', r'<span style="font-family:\1">\2</span>', value, flags=re.DOTALL)

    # Text alignment
    value = re.sub(r'\[center\](.*?)\[/center\]', r'<div style="text-align:center">\1</div>', value, flags=re.DOTALL)
    value = re.sub(r'\[left\](.*?)\[/left\]', r'<div style="text-align:left">\1</div>', value, flags=re.DOTALL)
    value = re.sub(r'\[right\](.*?)\[/right\]', r'<div style="text-align:right">\1</div>', value, flags=re.DOTALL)
    value = re.sub(r'\[justify\](.*?)\[/justify\]', r'<div style="text-align:justify">\1</div>', value, flags=re.DOTALL)
    value = re.sub(r'\[align=(left|right|center|justify)\](.*?)\[/align\]', r'<div style="text-align:\1">\2</div>', value, flags=re.DOTALL)

    # Images
    value = re.sub(r'\[img\](.*?)\[/img\]', r'<img src="\1" alt="Image" class="img-fluid" loading="lazy">', value, flags=re.DOTALL)
    value = re.sub(r'\[img=(\d+)x(\d+)\](.*?)\[/img\]', r'<img src="\3" alt="Image" width="\1" height="\2" class="img-fluid" loading="lazy">', value, flags=re.DOTALL)

    # Quotes
    value = re.sub(r'\[quote\](.*?)\[/quote\]', r'<blockquote class="blockquote">\1</blockquote>', value, flags=re.DOTALL)
    value = re.sub(r'\[quote=(.*?)\](.*?)\[/quote\]', r'<blockquote class="blockquote"><p class="blockquote-footer">\1</p>\2</blockquote>', value, flags=re.DOTALL)

    # Code blocks
    value = re.sub(r'\[code\](.*?)\[/code\]', r'<pre><code>\1</code></pre>', value, flags=re.DOTALL)
    value = re.sub(r'\[code=([a-zA-Z0-9+#]+)\](.*?)\[/code\]', r'<pre><code class="language-\1">\2</code></pre>', value, flags=re.DOTALL)

    # Lists - unordered
    def replace_list(match):
        list_content = match.group(1)
        # Replace individual list items
        list_content = re.sub(r'\[\*\](.*?)(?=\[\*\]|\[/list\])', r'<li>\1</li>', list_content, flags=re.DOTALL)
        return f'<ul class="bbcode-list">{list_content}</ul>'

    value = re.sub(r'\[list\](.*?)\[/list\]', replace_list, value, flags=re.DOTALL)

    # Lists - ordered
    def replace_olist(match):
        list_content = match.group(1)
        list_type = match.group(2) if match.group(2) else '1'

        # Replace individual list items
        list_content = re.sub(r'\[\*\](.*?)(?=\[\*\]|\[/olist\])', r'<li>\1</li>', list_content, flags=re.DOTALL)

        type_attr = ''
        if list_type in ['a', 'A', 'i', 'I']:
            type_attr = f' type="{list_type}"'

        return f'<ol class="bbcode-list"{type_attr}>{list_content}</ol>'

    value = re.sub(r'\[olist(?:=([aAiI1]))?\](.*?)\[/olist\]', replace_olist, value, flags=re.DOTALL)

    # Tables
    value = re.sub(r'\[table\](.*?)\[/table\]', r'<table class="table table-bordered">\1</table>', value, flags=re.DOTALL)
    value = re.sub(r'\[tr\](.*?)\[/tr\]', r'<tr>\1</tr>', value, flags=re.DOTALL)
    value = re.sub(r'\[td\](.*?)\[/td\]', r'<td>\1</td>', value, flags=re.DOTALL)
    value = re.sub(r'\[th\](.*?)\[/th\]', r'<th>\1</th>', value, flags=re.DOTALL)

    # Subscript and superscript
    value = re.sub(r'\[sub\](.*?)\[/sub\]', r'<sub>\1</sub>', value, flags=re.DOTALL)
    value = re.sub(r'\[sup\](.*?)\[/sup\]', r'<sup>\1</sup>', value, flags=re.DOTALL)

    # Spoiler
    value = re.sub(r'\[spoiler\](.*?)\[/spoiler\]', r'<div class="spoiler"><div class="spoiler-toggle">Spoiler (click to show/hide)</div><div class="spoiler-content" style="display:none">\1</div></div>', value, flags=re.DOTALL)
    value = re.sub(r'\[spoiler=(.*?)\](.*?)\[/spoiler\]', r'<div class="spoiler"><div class="spoiler-toggle">\1 (click to show/hide)</div><div class="spoiler-content" style="display:none">\2</div></div>', value, flags=re.DOTALL)

    # Horizontal rule
    value = re.sub(r'\[hr\]', r'<hr>', value)

    # YouTube video
    value = re.sub(r'\[youtube\](?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)(?:&.*?)?\[/youtube\]',
                  r'<div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://www.youtube.com/embed/\1" allowfullscreen></iframe></div>',
                  value, flags=re.DOTALL)

    # Vimeo videos
    value = re.sub(r'\[vimeo\](?:https?://)?(?:www\.)?vimeo\.com/(\d+)(?:\?.*?)?\[/vimeo\]',
                 r'<div class="embed-responsive embed-responsive-16by9"><iframe class="embed-responsive-item" src="https://player.vimeo.com/video/\1" allowfullscreen></iframe></div>',
                 value, flags=re.DOTALL)

    # SoundCloud embed
    value = re.sub(r'\[soundcloud\](.*?)\[/soundcloud\]',
                  r'<div class="soundcloud-embed"><iframe width="100%" height="166" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=\1&amp;color=ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false"></iframe></div>',
                  value, flags=re.DOTALL)

    # Columns layout
    def replace_columns(match):
        columns_content = match.group(1)
        columns = re.findall(r'\[column\](.*?)\[/column\]', columns_content, re.DOTALL)

        column_count = len(columns)
        if column_count == 0:
            return ""

        column_width = 12 // min(column_count, 4)  # Bootstrap's grid is 12 columns wide

        html = '<div class="row">'
        for column in columns:
            html += f'<div class="col-md-{column_width}">{column}</div>'
        html += '</div>'

        return html

    value = re.sub(r'\[columns\](.*?)\[/columns\]', replace_columns, value, flags=re.DOTALL)

    # Accordion
    def replace_accordion(match):
        accordion_content = match.group(1)
        accordion_id = f'accordion-{hash(accordion_content) & 0xFFFFFFFF}'

        sections = re.findall(r'\[section=([^]]+)\](.*?)\[/section\]', accordion_content, re.DOTALL)

        if not sections:
            return ""

        html = f'<div class="accordion" id="{accordion_id}">'
        for i, (title, content) in enumerate(sections):
            item_id = f'{accordion_id}-item-{i}'
            collapsed = "" if i == 0 else "collapsed"
            show = "show" if i == 0 else ""

            html += f'''
                <div class="accordion-item">
                    <h2 class="accordion-header" id="heading-{item_id}">
                        <button class="accordion-button {collapsed}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{item_id}" aria-expanded="{str(i == 0).lower()}" aria-controls="collapse-{item_id}">
                            {title}
                        </button>
                    </h2>
                    <div id="collapse-{item_id}" class="accordion-collapse collapse {show}" aria-labelledby="heading-{item_id}" data-bs-parent="#{accordion_id}">
                        <div class="accordion-body">
                            {content}
                        </div>
                    </div>
                </div>
            '''

        html += '</div>'
        return html

    value = re.sub(r'\[accordion\](.*?)\[/accordion\]', replace_accordion, value, flags=re.DOTALL)

    # Indentation
    value = re.sub(r'\[indent\](.*?)\[/indent\]', r'<div style="padding-left: 2em">\1</div>', value, flags=re.DOTALL)
    value = re.sub(r'\[indent=(\d+)(px|em|%)?\](.*?)\[/indent\]', r'<div style="padding-left: \1\2">\3</div>', value, flags=re.DOTALL)

    # Progress bar
    value = re.sub(r'\[progress=(\d+)\](.*?)\[/progress\]',
                  r'<div class="progress"><div class="progress-bar" role="progressbar" style="width: \1%;" aria-valuenow="\1" aria-valuemin="0" aria-valuemax="100">\2</div></div>',
                  value, flags=re.DOTALL)

    # Font Awesome icons
    value = re.sub(r'\[icon=([a-z0-9- ]+)\]',
                  r'<i class="fas fa-\1" aria-hidden="true"></i>',
                  value)

    # Google Maps
    value = re.sub(r'\[map\]([^[]+)\[/map\]',
                  lambda m: f'<div class="map-embed"><iframe width="100%" height="400" frameborder="0" src="https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q={urllib.parse.quote_plus(m.group(1))}" allowfullscreen></iframe></div>',
                  value, flags=re.DOTALL)

    # Audio player
    value = re.sub(r'\[audio\](.*?)\[/audio\]',
                  r'<audio controls class="w-100"><source src="\1" type="audio/mpeg">Your browser does not support the audio element.</audio>',
                  value, flags=re.DOTALL)

    # Convert newlines to <br>
    value = value.replace('\n', '<br>')

    return mark_safe(value)

@register.filter(is_safe=True)
@stringfilter
def bbcode_preview(value, length=300):
    """
    Convert BBCode to HTML with a character limit for previews
    """
    # Remove BBCode tags and limit length
    preview = re.sub(r'\[.*?\]', '', value)
    if len(preview) > length:
        preview = preview[:length] + '...'

    return mark_safe(escape(preview))
