#!/usr/bin/env python3
"""
Test script to verify markdown to HTML conversion
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from builder import Builder


def test_markdown_parsing():
    """Test markdown parsing functionality"""
    builder = Builder(content_dir="content", output_dir="output")
    
    # Test 1: Convert test.md to HTML
    print("=" * 60)
    print("Test 1: Converting test.md to HTML")
    print("=" * 60)
    
    test_md_path = Path("content/test.md")
    if test_md_path.exists():
        html_output = builder.markdown_to_html(test_md_path)
        print("HTML Output:")
        print(html_output)
        print()
        
        # Save the output to verify
        output_file = Path("output/test.html")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)
        print(f"✓ HTML saved to {output_file}")
    else:
        print(f"✗ File not found: {test_md_path}")
    
    # Test 2: Scan directory for markdown files
    print("\n" + "=" * 60)
    print("Test 2: Scanning content directory for markdown files")
    print("=" * 60)
    
    md_files = builder.get_markdown_files()
    print(f"Found {len(md_files)} markdown file(s):")
    for md_file in md_files:
        print(f"  - {md_file}")


if __name__ == "__main__":
    test_markdown_parsing()
