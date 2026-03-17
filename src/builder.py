"""Builder module - Core SSG functionality."""

from dataclasses import dataclass
import os
import re
import shutil
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


@dataclass
class Page:
    """Represents a source markdown page and its generated HTML metadata."""

    source_path: Path
    relative_source_path: Path
    output_path: Path
    relative_output_path: Path
    url: str
    title: str
    order: int
    html_content: str


class Builder:
    """Main builder class for the Static Site Generator."""

    def __init__(
        self,
        content_dir="content",
        templates_dir="templates",
        output_dir="output",
        static_dir="static",
    ):
        self.content_dir = Path(content_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.static_dir = Path(static_dir)
        self.markdown_extensions = ["fenced_code", "tables"]

    def markdown_to_html(self, md_file_path):
        """Convert a markdown file to HTML."""
        raw_text = Path(md_file_path).read_text(encoding="utf-8")
        _, markdown_body = self.parse_front_matter(raw_text)
        return markdown.markdown(markdown_body, extensions=self.markdown_extensions)

    def get_markdown_files(self):
        """Scan the content directory for all markdown files."""
        return sorted(self.content_dir.glob("**/*.md"))

    def parse_front_matter(self, raw_text):
        """Extract simple YAML-like front matter and return metadata and body."""
        metadata = {}

        if not raw_text.startswith("---\n"):
            return metadata, raw_text

        parts = raw_text.split("\n---\n", 1)
        if len(parts) != 2:
            raise ValueError("Front matter must be closed with '---'.")

        raw_metadata, body = parts
        for line in raw_metadata.splitlines()[1:]:
            stripped = line.strip()
            if not stripped:
                continue
            if ":" not in stripped:
                raise ValueError(f"Invalid front matter line: {line}")
            key, value = stripped.split(":", 1)
            metadata[key.strip()] = value.strip()

        return metadata, body.lstrip()

    def extract_title(self, markdown_body, metadata, source_path):
        """Resolve the page title from metadata, heading, or file name."""
        if metadata.get("title"):
            return metadata["title"]

        heading_match = re.search(r"^#\s+(.+)$", markdown_body, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()

        return source_path.stem.replace("-", " ").replace("_", " ").title()

    def parse_page(self, md_file_path):
        """Parse a markdown file into a Page object."""
        source_path = Path(md_file_path)
        raw_text = source_path.read_text(encoding="utf-8")
        metadata, markdown_body = self.parse_front_matter(raw_text)
        html_content = markdown.markdown(markdown_body, extensions=self.markdown_extensions)

        relative_source_path = source_path.relative_to(self.content_dir)
        relative_output_path = relative_source_path.with_suffix(".html")
        output_path = self.output_dir / relative_output_path
        order_value = metadata.get("order", "999")

        try:
            order = int(order_value)
        except ValueError as exc:
            raise ValueError(f"Invalid order value '{order_value}' in {source_path}") from exc

        return Page(
            source_path=source_path,
            relative_source_path=relative_source_path,
            output_path=output_path,
            relative_output_path=relative_output_path,
            url=relative_output_path.as_posix(),
            title=self.extract_title(markdown_body, metadata, source_path),
            order=order,
            html_content=html_content,
        )

    def load_pages(self):
        """Load and parse all markdown files in the content directory."""
        if not self.content_dir.exists():
            raise FileNotFoundError(f"Content directory not found: {self.content_dir}")

        markdown_files = self.get_markdown_files()
        if not markdown_files:
            raise FileNotFoundError(f"No markdown files found in: {self.content_dir}")

        pages = [self.parse_page(md_file_path) for md_file_path in markdown_files]
        return sorted(pages, key=lambda page: (page.order, page.title.lower(), page.url))

    def build_navigation(self, current_page, pages):
        """Build navigation data with per-page relative links."""
        current_dir = current_page.output_path.parent
        navigation = []

        for page in pages:
            relative_href = os.path.relpath(page.output_path, start=current_dir).replace("\\", "/")
            navigation.append(
                {
                    "title": page.title,
                    "href": relative_href,
                    "is_current": page.url == current_page.url,
                }
            )

        return navigation

    def get_stylesheet_href(self, current_page):
        """Compute the stylesheet path relative to the current page."""
        stylesheet_path = self.output_dir / self.static_dir.name / "style.css"
        return os.path.relpath(stylesheet_path, start=current_page.output_path.parent).replace("\\", "/")

    def create_template_environment(self):
        """Create the Jinja2 environment used for page rendering."""
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        return Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def prepare_output_directory(self):
        """Clear and recreate the output directory."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_page(self, page, pages, template):
        """Render a single page using the base template."""
        return template.render(
            title=page.title,
            content=page.html_content,
            navigation=self.build_navigation(page, pages),
            stylesheet_href=self.get_stylesheet_href(page),
        )

    def write_page(self, page, rendered_html):
        """Write one rendered HTML page to the output directory."""
        page.output_path.parent.mkdir(parents=True, exist_ok=True)
        page.output_path.write_text(rendered_html, encoding="utf-8")

    def copy_static_assets(self):
        """Copy static assets to the output directory if they exist."""
        if not self.static_dir.exists():
            return

        destination = self.output_dir / self.static_dir.name
        shutil.copytree(self.static_dir, destination, dirs_exist_ok=True)

    def build(self):
        """Build the static site."""
        try:
            pages = self.load_pages()
            environment = self.create_template_environment()
            template = environment.get_template("base.html")
        except TemplateNotFound as exc:
            raise FileNotFoundError("Template 'base.html' was not found.") from exc

        self.prepare_output_directory()

        for page in pages:
            rendered_html = self.render_page(page, pages, template)
            self.write_page(page, rendered_html)

        self.copy_static_assets()

        print(f"Built {len(pages)} page(s) into '{self.output_dir}'.")
