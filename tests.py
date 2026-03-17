"""Tests for the Static Site Generator Builder."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.builder import Builder, Page


class TestFrontMatterParsing(unittest.TestCase):
    """Test front matter extraction and parsing."""

    def setUp(self):
        self.builder = Builder()

    def test_parse_front_matter_with_metadata(self):
        """Front matter should be extracted correctly."""
        raw_text = """---
title: My Page
order: 5
---

# Content starts here

Regular content.
"""
        metadata, body = self.builder.parse_front_matter(raw_text)
        self.assertEqual(metadata["title"], "My Page")
        self.assertEqual(metadata["order"], "5")
        self.assertIn("# Content starts here", body)

    def test_parse_front_matter_no_metadata(self):
        """Text without front matter should return empty metadata."""
        raw_text = """# Just Content

Some text here.
"""
        metadata, body = self.builder.parse_front_matter(raw_text)
        self.assertEqual(metadata, {})
        self.assertEqual(body, raw_text)

    def test_parse_front_matter_empty_lines(self):
        """Empty lines in front matter should be ignored."""
        raw_text = """---
title: Test

order: 3
---

Content here.
"""
        metadata, body = self.builder.parse_front_matter(raw_text)
        self.assertEqual(metadata["title"], "Test")
        self.assertEqual(metadata["order"], "3")


class TestTitleExtraction(unittest.TestCase):
    """Test page title resolution."""

    def setUp(self):
        self.builder = Builder()

    def test_extract_title_from_metadata(self):
        """Title should come from front matter first."""
        metadata = {"title": "Front Matter Title"}
        markdown_body = "# Heading Title"
        source_path = Path("test.md")

        title = self.builder.extract_title(markdown_body, metadata, source_path)
        self.assertEqual(title, "Front Matter Title")

    def test_extract_title_from_heading(self):
        """Title should fall back to first H1 heading."""
        metadata = {}
        markdown_body = "# My Heading\n\nContent here."
        source_path = Path("test.md")

        title = self.builder.extract_title(markdown_body, metadata, source_path)
        self.assertEqual(title, "My Heading")

    def test_extract_title_from_filename(self):
        """Title should fall back to filename if no heading."""
        metadata = {}
        markdown_body = "Just content, no heading."
        source_path = Path("my-test-page.md")

        title = self.builder.extract_title(markdown_body, metadata, source_path)
        self.assertEqual(title, "My Test Page")


class TestMarkdownConversion(unittest.TestCase):
    """Test Markdown to HTML conversion."""

    def setUp(self):
        self.builder = Builder()

    def test_markdown_to_html_basic(self):
        """Basic Markdown should convert to HTML."""
        markdown_text = "# Heading\n\nParagraph with **bold**."
        html = self.builder.markdown_to_html(Path(tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False).name))
        # We'll test by creating a temp file and reading it
        temp_file = Path(tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False).name)
        try:
            temp_file.write_text(markdown_text, encoding='utf-8')
            html = self.builder.markdown_to_html(temp_file)
            self.assertIn("<h1>Heading</h1>", html)
            self.assertIn("<strong>bold</strong>", html)
        finally:
            temp_file.unlink()

    def test_markdown_with_code_blocks(self):
        """Fenced code blocks should render correctly."""
        markdown_text = """```python
print("hello")
```"""
        temp_file = Path(tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False).name)
        try:
            temp_file.write_text(markdown_text, encoding='utf-8')
            html = self.builder.markdown_to_html(temp_file)
            self.assertIn("<code", html)
            self.assertIn("python", html)
        finally:
            temp_file.unlink()


class TestPageCreation(unittest.TestCase):
    """Test Page object creation and parsing."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.builder = Builder(content_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_parse_page_with_front_matter(self):
        """Page should parse metadata and content."""
        md_file = Path(self.temp_dir) / "test.md"
        md_file.write_text(
            "---\ntitle: Test Page\norder: 2\n---\n\n# Content\n\nBody text.",
            encoding='utf-8'
        )

        page = self.builder.parse_page(md_file)
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.order, 2)
        self.assertIn("<h1>Content</h1>", page.html_content)

    def test_parse_page_preserves_structure(self):
        """Page should preserve relative paths correctly."""
        blog_dir = Path(self.temp_dir) / "blog"
        blog_dir.mkdir()
        md_file = blog_dir / "post.md"
        md_file.write_text("---\ntitle: Blog Post\n---\n\n# Post", encoding='utf-8')

        page = self.builder.parse_page(md_file)
        self.assertEqual(page.relative_output_path, Path("blog/post.html"))
        self.assertEqual(page.url, "blog/post.html")


class TestFileDiscovery(unittest.TestCase):
    """Test finding Markdown files in content directory."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.builder = Builder(content_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_markdown_files_flat(self):
        """Should find Markdown files in flat directory."""
        Path(self.temp_dir).joinpath("page1.md").write_text("# Page 1")
        Path(self.temp_dir).joinpath("page2.md").write_text("# Page 2")
        Path(self.temp_dir).joinpath("readme.txt").write_text("Not markdown")

        files = self.builder.get_markdown_files()
        self.assertEqual(len(files), 2)
        self.assertTrue(all(f.suffix == ".md" for f in files))

    def test_get_markdown_files_nested(self):
        """Should find Markdown files in nested directories."""
        Path(self.temp_dir).joinpath("blog").mkdir()
        Path(self.temp_dir).joinpath("blog/post.md").write_text("# Post")
        Path(self.temp_dir).joinpath("guides").mkdir()
        Path(self.temp_dir).joinpath("guides/getting-started.md").write_text("# Getting Started")

        files = self.builder.get_markdown_files()
        self.assertEqual(len(files), 2)


class TestNavigation(unittest.TestCase):
    """Test navigation generation."""

    def setUp(self):
        self.builder = Builder()

    def test_build_navigation_relative_links(self):
        """Navigation should use relative links based on page location."""
        page1 = Page(
            source_path=Path("index.md"),
            relative_source_path=Path("index.md"),
            output_path=Path("output/index.html"),
            relative_output_path=Path("index.html"),
            url="index.html",
            title="Home",
            order=1,
            html_content="<h1>Home</h1>"
        )
        page2 = Page(
            source_path=Path("blog/post.md"),
            relative_source_path=Path("blog/post.md"),
            output_path=Path("output/blog/post.html"),
            relative_output_path=Path("blog/post.html"),
            url="blog/post.html",
            title="Blog Post",
            order=2,
            html_content="<h1>Blog Post</h1>"
        )

        nav = self.builder.build_navigation(page2, [page1, page2])
        self.assertEqual(len(nav), 2)
        # For page2 (in blog/), relative link to home should go up one level
        self.assertTrue(any("../index.html" in item["href"] for item in nav if item["title"] == "Home"))
        self.assertTrue(any(item["is_current"] for item in nav if item["title"] == "Blog Post"))


class TestStylesheetPath(unittest.TestCase):
    """Test stylesheet href computation for different page depths."""

    def setUp(self):
        self.builder = Builder()

    def test_stylesheet_href_root(self):
        """Stylesheet href should be relative to page location."""
        page = Page(
            source_path=Path("index.md"),
            relative_source_path=Path("index.md"),
            output_path=Path("output/index.html"),
            relative_output_path=Path("index.html"),
            url="index.html",
            title="Home",
            order=1,
            html_content="<h1>Home</h1>"
        )
        href = self.builder.get_stylesheet_href(page)
        self.assertEqual(href, "static/style.css")

    def test_stylesheet_href_nested(self):
        """Stylesheet href should go up for nested pages."""
        page = Page(
            source_path=Path("blog/post.md"),
            relative_source_path=Path("blog/post.md"),
            output_path=Path("output/blog/post.html"),
            relative_output_path=Path("blog/post.html"),
            url="blog/post.html",
            title="Post",
            order=1,
            html_content="<h1>Post</h1>"
        )
        href = self.builder.get_stylesheet_href(page)
        self.assertEqual(href, "../static/style.css")


class TestIntegration(unittest.TestCase):
    """Integration tests for the full build process."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.content_dir = Path(self.temp_dir) / "content"
        self.output_dir = Path(self.temp_dir) / "output"
        self.templates_dir = Path(self.temp_dir) / "templates"
        self.static_dir = Path(self.temp_dir) / "static"

        self.content_dir.mkdir()
        self.templates_dir.mkdir()
        self.static_dir.mkdir()

        # Create a simple base template
        template_path = self.templates_dir / "base.html"
        template_path.write_text(
            "<!DOCTYPE html>\n"
            "<html><head><title>{{ title }}</title></head>"
            "<body>{{ content | safe }}</body></html>",
            encoding='utf-8'
        )

        # Create a CSS file
        css_path = self.static_dir / "style.css"
        css_path.write_text("body { color: blue; }", encoding='utf-8')

        self.builder = Builder(
            content_dir=str(self.content_dir),
            output_dir=str(self.output_dir),
            templates_dir=str(self.templates_dir),
            static_dir=str(self.static_dir)
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_full_build_process(self):
        """Full build should create output files and copy assets."""
        # Create markdown files
        (self.content_dir / "index.md").write_text(
            "---\ntitle: Home\norder: 1\n---\n\n# Welcome",
            encoding='utf-8'
        )
        (self.content_dir / "blog").mkdir()
        (self.content_dir / "blog" / "post.md").write_text(
            "---\ntitle: First Post\norder: 2\n---\n\n# My Post",
            encoding='utf-8'
        )

        # Run build
        self.builder.build()

        # Verify output files
        self.assertTrue((self.output_dir / "index.html").exists())
        self.assertTrue((self.output_dir / "blog" / "post.html").exists())
        self.assertTrue((self.output_dir / "static" / "style.css").exists())

        # Verify content
        html = (self.output_dir / "index.html").read_text(encoding='utf-8')
        self.assertIn("<h1>Welcome</h1>", html)


if __name__ == "__main__":
    unittest.main()
