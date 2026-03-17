#!/usr/bin/env python3
"""
Static Site Generator - Main CLI Entry Point
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.builder import Builder


def main():
    """Main entry point for the SSG CLI"""
    parser = argparse.ArgumentParser(
        description="Static Site Generator - Convert markdown content to HTML",
        prog="ssg"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build the static site")
    build_parser.add_argument(
        "--content",
        default="content",
        help="Path to content directory (default: content)"
    )
    build_parser.add_argument(
        "--templates",
        default="templates",
        help="Path to templates directory (default: templates)"
    )
    build_parser.add_argument(
        "--output",
        default="output",
        help="Path to output directory (default: output)"
    )
    build_parser.add_argument(
        "--static",
        default="static",
        help="Path to static assets directory (default: static)"
    )
    
    args = parser.parse_args()
    
    if args.command == "build":
        try:
            builder = Builder(
                content_dir=args.content,
                templates_dir=args.templates,
                output_dir=args.output,
                static_dir=args.static,
            )
            builder.build()
        except (FileNotFoundError, ValueError) as exc:
            print(f"Build failed: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
