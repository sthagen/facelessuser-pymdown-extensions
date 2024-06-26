"""Test slugs."""
from .. import util
from pymdownx import slugs


class TestUslugify(util.MdCase):
    """Test Unicode slugs."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(case="lower")
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Testing unicode-slugs_headers ±♠Ωℑ',
            r'<h1 id="testing-unicode-slugs_headers-ωℑ">Testing unicode-slugs_headers ±♠Ωℑ</h1>'
        )


class TestUslugifyEncoded(util.MdCase):
    """Test Unicode encoded slugs."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(case="lower", percent_encode=True)
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Testing unicode-slugs_headers ±♠Ωℑ with encoding',
            r'<h1 id="testing-unicode-slugs_headers-%CF%89%E2%84%91-with-encoding">'
            'Testing unicode-slugs_headers ±♠Ωℑ with encoding</h1>'
        )


class TestUslugifyCased(util.MdCase):
    """Test Unicode cased slugs."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify()
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Testing cased unicode-slugs_headers ±♠Ωℑ',
            r'<h1 id="Testing-cased-unicode-slugs_headers-Ωℑ">Testing cased unicode-slugs_headers ±♠Ωℑ</h1>'
        )


class TestUslugifyCasedEncoded(util.MdCase):
    """Test Unicode cased, encoded slugs."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(percent_encode=True)
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Testing cased unicode-slugs_headers ±♠Ωℑ with encoding',
            r'<h1 id="Testing-cased-unicode-slugs_headers-%CE%A9%E2%84%91-with-encoding">'
            'Testing cased unicode-slugs_headers ±♠Ωℑ with encoding</h1>'
        )


class TestGFM(util.MdCase):
    """Test GitHub Flavored Markdown style slugs."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(case="lower-ascii")
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Testing GFM unicode-slugs_headers ±♠Ωℑ',
            r'<h1 id="testing-gfm-unicode-slugs_headers-Ωℑ">Testing GFM unicode-slugs_headers ±♠Ωℑ</h1>'
        )


class TestGFMEncoded(util.MdCase):
    """Test encoded GitHub Flavored Markdown style slugs."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(case="lower-ascii", percent_encode=True)
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Testing GFM unicode-slugs_headers ±♠Ωℑ with encoding',
            r'<h1 id="testing-gfm-unicode-slugs_headers-%CE%A9%E2%84%91-with-encoding">'
            r'Testing GFM unicode-slugs_headers ±♠Ωℑ with encoding</h1>'
        )


class TestNormalize(util.MdCase):
    """Test different normalization methods."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(normalize='NFD')
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# Théâtre',
            r'<h1 id="Theatre">Théâtre</h1>'
        )


class TestFold(util.MdCase):
    """Test different normalization methods."""

    extension = ['markdown.extensions.toc']
    extension_configs = {
        'markdown.extensions.toc': {
            "slugify": slugs.slugify(case='fold')
        }
    }

    def test_slug(self):
        """Test the slug output."""

        self.check_markdown(
            r'# ß',
            r'<h1 id="ss">ß</h1>'
        )
