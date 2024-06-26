r"""
Arithmatex.

pymdownx.arithmatex
Extension that preserves the following for MathJax use:

```
$Equation$, \(Equation\)

$$
  Display Equations
$$

\[
  Display Equations
\]

\begin{align}
  Display Equations
\end{align}
```

and `$Inline MathJax Equations$`

Inline and display equations are converted to scripts tags. You can optionally generate previews.

MIT license.

Copyright (c) 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from markdown import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown import util as md_util
from functools import partial
import xml.etree.ElementTree as etree
from . import util
import re

RE_SMART_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$)|(?<!\\)(\$)(?!\s)((?:\\.|[^\\$])+?)(?<!\s)(?:\$))'
RE_DOLLAR_INLINE = r'(?:(?<!\\)((?:\\{2})+)(?=\$)|(?<!\\)(\$)((?:\\.|[^\\$])+?)(?:\$))'
RE_BRACKET_INLINE = r'(?:(?<!\\)((?:\\{2})+?)(?=\\\()|(?<!\\)(\\\()((?:\\[^)]|[^\\])+?)(?:\\\)))'

RE_DOLLAR_BLOCK = r'(?P<dollar>[$]{2})(?P<math>((?:\\.|[^\\])+?))(?P=dollar)'
RE_TEX_BLOCK = r'(?P<math2>\\begin\{(?P<env>[a-z]+\*?)\}(?:\\.|[^\\])+?\\end\{(?P=env)\})'
RE_BRACKET_BLOCK = r'\\\[(?P<math3>(?:\\[^\]]|[^\\])+?)\\\]'


def _escape(txt):
    """Basic html escaping."""

    txt = txt.replace('&', '&amp;')
    txt = txt.replace('<', '&lt;')
    txt = txt.replace('>', '&gt;')
    txt = txt.replace('"', '&quot;')
    return txt


# Formatters usable with InlineHilite
@util.deprecated(
    "The inline MathJax Preview formatter has been deprecated in favor of the configurable 'arithmatex_fenced_format'. "
    "Please see relevant documentation for more information on how to switch before this function is "
    "removed in the future."
)
def inline_mathjax_preview_format(math, language='math', class_name='arithmatex', md=None):
    """Inline math formatter with preview."""

    return _inline_mathjax_format(math, preview=True)


@util.deprecated(
    "The inline MathJax formatter has been deprecated in favor of the configurable 'arithmatex_fenced_format'. "
    "Please see relevant documentation for more information on how to switch before this function is "
    "removed in the future."
)
def inline_mathjax_format(math, language='math', class_name='arithmatex', md=None):
    """Inline math formatter."""

    return _inline_mathjax_format(math, preview=False)


@util.deprecated(
    "The inline generic math formatter has been deprecated in favor of the configurable 'arithmatex_inline_format'. "
    "Please see relevant documentation for more information on how to switch before this function is "
    "removed in the future."
)
def inline_generic_format(math, language='math', class_name='arithmatex', md=None, **kwargs):
    """Inline generic formatter."""

    return _inline_generic_format(math, language, class_name, md, **kwargs)


def _inline_mathjax_format(math, language='math', class_name='arithmatex', md=None, tag='span', preview=False):
    """Inline math formatter."""

    el = etree.Element(tag, {'class': 'arithmatex'})
    if preview:
        pre = etree.SubElement(el, 'span', {'class': 'MathJax_Preview'})
        pre.text = md_util.AtomicString(math)
    script = etree.SubElement(el, 'script', {'type': 'math/tex'})
    script.text = md_util.AtomicString(math)
    return el


def _inline_generic_format(math, language='math', class_name='arithmatex', md=None, wrap='\\({}\\)', tag='span'):
    """Inline generic formatter."""

    el = etree.Element(tag, {'class': class_name})
    el.text = md_util.AtomicString(wrap.format(math))
    return el


def arithmatex_inline_format(**kwargs):
    """Specify which type of formatter you want and the wrapping tag."""

    mode = kwargs.get('mode', 'generic')
    tag = kwargs.get('tag', 'span')
    preview = kwargs.get('preview', False)

    if mode == 'generic':
        return partial(_inline_generic_format, tag=tag)
    elif mode == 'mathjax':
        return partial(_inline_mathjax_format, preview=preview)


# Formatters usable with SuperFences
@util.deprecated(
    "The fenced MathJax preview formatter has been deprecated in favor of the configurable 'arithmatex_fenced_format'. "
    "Please see relevant documentation for more information on how to switch before this function is "
    "removed in the future."
)
def fence_mathjax_preview_format(math, language='math', class_name='arithmatex', options=None, md=None, **kwargs):
    """Block MathJax formatter with preview."""

    return _fence_mathjax_format(math, preview=True)


@util.deprecated(
    "The fenced MathJax preview formatter has been deprecated in favor of the configurable 'arithmatex_fenced_format'. "
    "Please see relevant documentation for more information on how to switch before this function is "
    "removed in the future."
)
def fence_mathjax_format(math, language='math', class_name='arithmatex', options=None, md=None, **kwargs):
    """Block MathJax formatter."""

    return _fence_mathjax_format(math, preview=False)


@util.deprecated(
    "The generic math formatter has been deprecated in favor of the configurable 'arithmatex_fenced_format'. "
    "Please see relevant documentation for more information on how to switch before this function is "
    "removed in the future."
)
def fence_generic_format(math, language='math', class_name='arithmatex', options=None, md=None, **kwargs):
    """Generic block formatter."""

    return _fence_generic_format(math, language, class_name, options, md, **kwargs)


def _fence_mathjax_format(
    math, language='math', class_name='arithmatex', options=None, md=None, preview=False, tag="div", **kwargs
):
    """Block math formatter."""

    text = f'<{tag} class="arithmatex">\n'
    if preview:
        text += (
            '<div class="MathJax_Preview">\n' +
            _escape(math) +
            '\n</div>\n'
        )

    text += (
        '<script type="math/tex; mode=display">\n' +
        math +
        '\n</script>\n'
    )
    text += '</div>'

    return text


def _fence_generic_format(
    math, language='math', class_name='arithmatex', options=None, md=None, wrap='\\[\n{}\n\\]', tag='div', **kwargs
):
    """Generic block formatter."""

    classes = kwargs['classes']
    id_value = kwargs['id_value']
    attrs = kwargs['attrs']

    classes.insert(0, class_name)

    id_value = f' id="{id_value}"' if id_value else ''
    classes = ' class="{}"'.format(' '.join(classes))
    attrs = ' ' + ' '.join(f'{k}="{v}"' for k, v in attrs.items()) if attrs else ''

    return f'<{tag}{id_value}{classes}{attrs}>{wrap.format(math)}</{tag}>'


def arithmatex_fenced_format(**kwargs):
    """Specify which type of formatter you want and the wrapping tag."""

    mode = kwargs.get('mode', 'generic')
    tag = kwargs.get('tag', 'div')
    preview = kwargs.get('preview', False)

    if mode == 'generic':
        return partial(_fence_generic_format, tag=tag)
    elif mode == 'mathjax':
        return partial(_fence_mathjax_format, tag=tag, preview=preview)


class InlineArithmatexPattern(InlineProcessor):
    """Arithmatex inline pattern handler."""

    ESCAPED_BSLASH = '{}{}{}'.format(md_util.STX, ord('\\'), md_util.ETX)

    def __init__(self, pattern, config):
        """Initialize."""

        # Generic setup
        self.generic = config.get('generic', False)
        wrap = config.get('tex_inline_wrap', ["\\(", "\\)"])
        self.wrap = (
            wrap[0].replace('{', '}}').replace('}', '}}') + '{}' + wrap[1].replace('{', '}}').replace('}', '}}')
        )
        self.inline_tag = config.get('inline_tag', 'span')

        # Default setup
        self.preview = config.get('preview', True)
        InlineProcessor.__init__(self, pattern)

    def handleMatch(self, m, data):
        """Handle notations and switch them to something that will be more detectable in HTML."""

        # Handle escapes
        groups = m.groups()
        escapes = groups[0]
        if not escapes and len(groups) > 3:
            escapes = groups[3]
        if escapes:
            return escapes.replace('\\\\', self.ESCAPED_BSLASH), m.start(0), m.end(0)

        # Handle Tex
        math = groups[2]
        if not math and len(groups) > 3:
            math = groups[5]

        if self.generic:
            return _inline_generic_format(math, wrap=self.wrap, tag=self.inline_tag), m.start(0), m.end(0)
        else:
            return _inline_mathjax_format(math, tag=self.inline_tag, preview=self.preview), m.start(0), m.end(0)


class BlockArithmatexProcessor(BlockProcessor):
    """MathJax block processor to find $$MathJax$$ content."""

    def __init__(self, pattern, config, md):
        """Initialize."""

        # Generic setup
        self.generic = config.get('generic', False)
        wrap = config.get('tex_block_wrap', ['\\[', '\\]'])
        self.wrap = (
            wrap[0].replace('{', '}}').replace('}', '}}') + '{}' + wrap[1].replace('{', '}}').replace('}', '}}')
        )
        self.block_tag = config.get('block_tag', 'div')

        # Default setup
        self.preview = config.get('preview', False)

        self.match = None
        self.pattern = re.compile(pattern)

        BlockProcessor.__init__(self, md.parser)

    def test(self, parent, block):
        """Return 'True' for future Python Markdown block compatibility."""

        self.match = self.pattern.match(block) if self.pattern is not None else None
        return self.match is not None

    def mathjax_output(self, parent, math):
        """Default MathJax output."""

        grandparent = parent
        parent = etree.SubElement(grandparent, self.block_tag, {'class': 'arithmatex'})
        if self.preview:
            preview = etree.SubElement(parent, 'div', {'class': 'MathJax_Preview'})
            preview.text = md_util.AtomicString(math)
        el = etree.SubElement(parent, 'script', {'type': 'math/tex; mode=display'})
        el.text = md_util.AtomicString(math)

    def generic_output(self, parent, math):
        """Generic output."""

        el = etree.SubElement(parent, self.block_tag, {'class': 'arithmatex'})
        el.text = md_util.AtomicString(self.wrap.format(math))

    def run(self, parent, blocks):
        """Find and handle block content."""

        blocks.pop(0)

        groups = self.match.groupdict()
        math = groups.get('math', '')
        if not math:
            math = groups.get('math2', '')
        if not math:
            math = groups.get('math3', '')

        if self.generic:
            self.generic_output(parent, math)
        else:
            self.mathjax_output(parent, math)

        return True


class ArithmatexExtension(Extension):
    """Adds delete extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'tex_inline_wrap': [
                ["\\(", "\\)"],
                "Wrap inline content with the provided text ['open', 'close'] - Default: ['', '']"
            ],
            'tex_block_wrap': [
                ["\\[", "\\]"],
                "Wrap blick content with the provided text ['open', 'close'] - Default: ['', '']"
            ],
            "smart_dollar": [True, "Use Arithmatex's smart dollars - Default True"],
            "block_syntax": [
                ['dollar', 'square', 'begin'],
                'Enable block syntax: "dollar" ($$...$$), "square" (\\[...\\]), and '
                '"begin" (\\begin{env}...\\end{env}). - Default: ["dollar", "square", "begin"]'
            ],
            "inline_syntax": [
                ['dollar', 'round'],
                'Enable block syntax: "dollar" ($$...$$), "bracket" (\\(...\\)) '
                ' - Default: ["dollar", "round"]'
            ],
            'generic': [False, "Output in a generic format for non MathJax libraries - Default: False"],
            'preview': [
                True,
                "Insert a preview for scripts. - Default: False"
            ],
            'block_tag': ['div', "Specify wrapper tag - Default 'div'"],
            'inline_tag': ['span', "Specify wrapper tag - Default 'span'"]
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Extend the inline and block processor objects."""

        md.registerExtension(self)
        util.escape_chars(md, ['$'])

        config = self.getConfigs()

        # Inline patterns
        allowed_inline = set(config.get('inline_syntax', ['dollar', 'round']))
        smart_dollar = config.get('smart_dollar', True)
        inline_patterns = []
        if 'dollar' in allowed_inline:
            inline_patterns.append(RE_SMART_DOLLAR_INLINE if smart_dollar else RE_DOLLAR_INLINE)
        if 'round' in allowed_inline:
            inline_patterns.append(RE_BRACKET_INLINE)
        if inline_patterns:
            inline = InlineArithmatexPattern('(?:%s)' % '|'.join(inline_patterns), config)
            md.inlinePatterns.register(inline, 'arithmatex-inline', 189.9)

        # Block patterns
        allowed_block = set(config.get('block_syntax', ['dollar', 'square', 'begin']))
        block_pattern = []
        if 'dollar' in allowed_block:
            block_pattern.append(RE_DOLLAR_BLOCK)
        if 'square' in allowed_block:
            block_pattern.append(RE_BRACKET_BLOCK)
        if 'begin' in allowed_block:
            block_pattern.append(RE_TEX_BLOCK)
        if block_pattern:
            block = BlockArithmatexProcessor(r'(?s)^(?:%s)[ ]*$' % '|'.join(block_pattern), config, md)
            md.parser.blockprocessors.register(block, "arithmatex-block", 79.9)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return ArithmatexExtension(*args, **kwargs)
