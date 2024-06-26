"""
Inline Highlighting.

pymdownx.inlinehilite

An alternative inline code extension that highlights code.  Can
use CodeHilite to source its settings or pymdownx.highlight.

`:::javascript var test = 0;`

- or -

`#!javascript var test = 0;`

Copyright 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>
"""

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown import util as md_util
import xml.etree.ElementTree as etree
import functools

ESCAPED_BSLASH = '{}{}{}'.format(md_util.STX, ord('\\'), md_util.ETX)
DOUBLE_BSLASH = '\\\\'
BACKTICK_CODE_RE = r'''(?x)
(?:
(?<!\\)(?P<escapes>(?:\\{2})+)(?=`+) |  # Process code escapes before code
(?<!\\)(?P<tic>`+)
((?:\:{3,}|\#!)(?P<lang>[\w#.+-]*)\s+)? # Optional language
(?P<code>.+?)                           # Code
(?<!`)(?P=tic)(?!`)                     # Closing
)
'''


class InlineHiliteException(Exception):
    """InlineHilite exception."""


def _escape(txt):
    """Basic html escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    return txt


def _test(language, test_language=None):
    """Test language."""

    return test_language is None or test_language == '*' or language == test_language


def _formatter(src="", language="", md=None, class_name="", fmt=None):
    """Formatter wrapper."""

    return fmt(src, language, class_name, md)


class InlineHilitePattern(InlineProcessor):
    """Handle the inline code patterns."""

    def __init__(self, pattern, config, md):
        """Initialize."""

        self.config = config
        InlineProcessor.__init__(self, pattern, md)
        self.md = md

        self.formatters = [
            {
                "name": "inlinehilite",
                "test": _test,
                "formatter": self.highlight_code
            }
        ]

        # Custom Fences
        custom_inline = self.config.get('custom_inline', [])
        for custom in custom_inline:
            name = custom.get('name')
            class_name = custom.get('class')
            inline_format = custom.get('format', self.highlight_code)
            if name is not None and class_name is not None:
                self.extend_custom_inline(
                    name,
                    functools.partial(_formatter, class_name=class_name, fmt=inline_format)
                )

        self.get_hl_settings = False

    def extend_custom_inline(self, name, formatter):
        """Extend SuperFences with the given name, language, and formatter."""

        obj = {
            "name": name,
            "test": functools.partial(_test, test_language=name),
            "formatter": formatter
        }

        if name == '*':
            self.formatters[0] = obj
        else:
            self.formatters.append(obj)

    def get_settings(self):
        """Check for Highlight extension settings."""

        if not self.get_hl_settings:
            self.get_hl_settings = True
            self.style_plain_text = self.config['style_plain_text']

            config = None
            self.highlighter = None
            for ext in self.md.registeredExtensions:
                try:
                    config = ext.get_pymdownx_highlight_settings()
                    self.highlighter = ext.get_pymdownx_highlighter()
                    break
                except AttributeError:
                    pass

            css_class = self.config['css_class']
            self.css_class = css_class if css_class else config['css_class']

            self.extend_pygments_lang = config.get('extend_pygments_lang', None)
            self.guess_lang = config['guess_lang']
            self.pygments_style = config['pygments_style']
            self.use_pygments = config['use_pygments']
            self.noclasses = config['noclasses']
            self.language_prefix = config['language_prefix']
            self.pygments_lang_class = config['pygments_lang_class']

    def highlight_code(self, src='', language='', classname=None, md=None):
        """Syntax highlight the inline code block."""

        process_text = self.style_plain_text or language or self.guess_lang
        default_lang = self.style_plain_text if isinstance(self.style_plain_text, str) else ''

        if process_text:
            el = self.highlighter(
                guess_lang=self.guess_lang,
                pygments_style=self.pygments_style,
                use_pygments=self.use_pygments,
                noclasses=self.noclasses,
                extend_pygments_lang=self.extend_pygments_lang,
                language_prefix=self.language_prefix,
                pygments_lang_class=self.pygments_lang_class,
                default_lang=default_lang
            ).highlight(src, language, self.css_class, inline=True)
            el.text = self.md.htmlStash.store(el.text)
        else:
            el = etree.Element('code')
            el.text = self.md.htmlStash.store(_escape(src))
        return el

    def handle_code(self, lang, src):
        """Handle code block."""

        for entry in reversed(self.formatters):
            if entry["test"](lang):
                value = entry["formatter"](
                    src=src,
                    language=lang,
                    md=self.md
                )
                if isinstance(value, str):
                    value = self.md.htmlStash.store(value)
                return value

    def handleMatch(self, m, data):
        """Handle the pattern match."""

        if m.group('escapes'):
            return m.group('escapes').replace(DOUBLE_BSLASH, ESCAPED_BSLASH), m.start(0), m.end(0)
        else:
            lang = m.group('lang') if m.group('lang') else ''
            src = m.group('code').strip()
            self.get_settings()
            try:
                return self.handle_code(lang, src), m.start(0), m.end(0)
            except InlineHiliteException:
                raise
            except Exception:
                return m.group(0), None, None


class InlineHiliteExtension(Extension):
    """Add inline highlighting extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.inlinehilite = []
        self.config = {
            'style_plain_text': [
                0,
                "Process inline code even when a language is not specified. "
                "When 'False', no classes will be added to code blocks without shebangs "
                "and no scoping will performed. The content will just be escaped."
                "If a language string is provided, then that language will be assumed "
                "for any inline code block without a shebang. "
                "- Default: False"
            ],
            'css_class': [
                '',
                "Set class name for wrapper element. The default of Highlight will be used"
                "if nothing is set. - "
                "Default: ''"
            ],
            'custom_inline': [[], "Custom inline - default []"]
        }
        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Add support for `:::language code` and `#!language code` highlighting."""

        config = self.getConfigs()
        md.inlinePatterns.register(InlineHilitePattern(BACKTICK_CODE_RE, config, md), "backtick", 190)
        md.registerExtensions(["pymdownx.highlight"], {"pymdownx.highlight": {"_enabled": False}})


def makeExtension(*args, **kwargs):
    """Return extension."""

    return InlineHiliteExtension(*args, **kwargs)
