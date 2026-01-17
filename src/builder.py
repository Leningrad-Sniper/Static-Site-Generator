"""
Builder module - Core SSG functionality
"""

import glob
import markdown
from pathlib import Path


class Builder:
    """Main builder class for the Static Site Generator"""
    
    def __init__(self, content_dir="content", templates_dir="templates", output_dir="output"):
        """
        Initialize the builder.
        
        Args:
            content_dir: Path to content directory containing markdown files
            templates_dir: Path to templates directory containing HTML templates
            output_dir: Path to output directory for generated files
        """
        self.content_dir = Path(content_dir)
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
    
    def markdown_to_html(self, md_file_path):
        """
        Convert a markdown file to HTML.
        
        Args:
            md_file_path: Path to the markdown file
            
        Returns:
            HTML string generated from markdown
        """
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html = markdown.markdown(md_content)
        return html
    
    def get_markdown_files(self):
        """
        Scan the content directory for all markdown files.
        
        Returns:
            List of Path objects for all .md files found
        """
        md_files = list(self.content_dir.glob('**/*.md'))
        return sorted(md_files)
    
    def build(self):
        """Build the static site"""
        print("Hello World")
        print(f"Building site from '{self.content_dir}' using templates from '{self.templates_dir}'")
        print(f"Output will be written to '{self.output_dir}'")
