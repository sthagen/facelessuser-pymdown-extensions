"""
EscapeAll.

pymdownx.escapeall
Escape everything.

MIT license.

Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

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
from markdown.inlinepatterns import InlineProcessor, SubstituteTagInlineProcessor
from markdown import util as md_util
from . import util

# We need to ignore these as they are used in Markdown processing
STX = '\u0002'
ETX = '\u0003'
ESCAPE_RE = r'\\(.)'
ESCAPE_NO_NL_RE = r'\\([^\n])'
HARDBREAK_RE = r'\\\n'


class EscapeAllPattern(InlineProcessor):
    """Return an escaped character."""

    def __init__(self, pattern, nbsp, md):
        """Initialize."""

        self.nbsp = nbsp
        InlineProcessor.__init__(self, pattern, md)

    def handleMatch(self, m, data):
        """Convert the char to an escaped character."""

        char = m.group(1)
        if char in ('<', '>', '&'):
            if char == '<':
                char = '&lt;'
            elif char == '>':
                char = '&gt;'
            elif char == '&':
                char = '&amp;'
            escape = self.md.htmlStash.store(char)
        elif self.nbsp and char == ' ':
            escape = self.md.htmlStash.store('&nbsp;')
        elif char in (STX, ETX):
            escape = char
        else:
            escape = '{}{}{}'.format(md_util.STX, util.get_ord(char), md_util.ETX)
        return escape, m.start(0), m.end(0)


class EscapeAllExtension(Extension):
    """Extension that allows you to escape everything."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'hardbreak': [
                False,
                "Turn escaped newlines to hardbreaks - Default: False"
            ],
            'nbsp': [
                False,
                "Turn escaped spaces to non-breaking spaces - Default: False"
            ]
        }
        super().__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Escape all."""

        config = self.getConfigs()
        hardbreak = config['hardbreak']
        md.inlinePatterns.register(
            EscapeAllPattern(ESCAPE_NO_NL_RE if hardbreak else ESCAPE_RE, config['nbsp'], md),
            "escape",
            180
        )

        if config['hardbreak']:
            md.inlinePatterns.register(SubstituteTagInlineProcessor(HARDBREAK_RE, 'br'), "hardbreak", 5.1)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return EscapeAllExtension(*args, **kwargs)
