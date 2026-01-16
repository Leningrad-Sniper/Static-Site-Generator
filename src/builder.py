"""
Builder module - Core SSG functionality
"""

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
    
    def build(self):
        """Build the static site"""
        print("Hello World")
        print(f"Building site from '{self.content_dir}' using templates from '{self.templates_dir}'")
        print(f"Output will be written to '{self.output_dir}'")
