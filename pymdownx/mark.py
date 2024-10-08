"""
Mark.

pymdownx.mark
Really simple plugin to add support for
<mark>test</mark> tags as ==test==

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
import re
from markdown import Extension
from markdown.inlinepatterns import SimpleTextInlineProcessor
from . import util

SMART_CONTENT = r'((?:(?<=\s)=+?(?=\s)|.)+?=*?)'
CONTENT = r'((?:[^=]|(?<!={2})=)+?)'

# Avoid starting a pattern with caret tokens that are surrounded by white space.
NOT_MARK = r'((^|(?<=\s))(=+)(?=\s|$))'

# ==mark==
MARK = r'(={{2}})(?!\s){}(?<!\s)\1'.format(CONTENT)
# ==mark==
SMART_MARK = r'(?:(?<=_)|(?<![\w=]))(={{2}})(?![\s=]){}(?<!\s)\1(?:(?=_)|(?![\w=]))'.format(SMART_CONTENT)


class MarkProcessor(util.PatternSequenceProcessor):
    """Handle mark patterns."""

    PATTERNS = [
        util.PatSeqItem(re.compile(MARK, re.DOTALL | re.UNICODE), 'single', 'mark')
    ]


class MarkSmartProcessor(util.PatternSequenceProcessor):
    """Handle smart mark patterns."""

    PATTERNS = [
        util.PatSeqItem(re.compile(SMART_MARK, re.DOTALL | re.UNICODE), 'single', 'mark')
    ]


class MarkExtension(Extension):
    """Add the mark extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'smart_mark': [True, "Treat ==connected==words== intelligently - Default: True"]
        }

        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Insert `<mark>test</mark>` tags as `==test==`."""

        config = self.getConfigs()
        smart = bool(config.get('smart_mark', True))

        md.registerExtension(self)

        escape_chars = []
        escape_chars.append('=')
        util.escape_chars(md, escape_chars)

        md.inlinePatterns.register(SimpleTextInlineProcessor(NOT_MARK), 'not_tilde', 70)
        mark = MarkSmartProcessor(r'=') if smart else MarkProcessor(r'=')
        md.inlinePatterns.register(mark, "mark", 65)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return MarkExtension(*args, **kwargs)
