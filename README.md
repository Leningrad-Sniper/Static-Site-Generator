# Static Site Generator

A small Python static site generator that reads Markdown files from `content/`, renders them through a Jinja2 template, and writes a complete HTML site to `output/`.

## Requirements

- Python 3.10+
- `pip`

## Project Structure

```text
my-ssg/
├── content/      # Markdown source files
├── output/       # Generated HTML site
├── src/          # Builder logic
├── static/       # CSS and other static assets
├── templates/    # Jinja2 HTML templates
├── ssg.py        # CLI entry point
└── test_phase2.py
```

## Setup

Create and activate a virtual environment, then install dependencies.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Build The Site

From the project root, run:

```bash
python ssg.py build
```

This command:

- Reads all Markdown files under `content/`
- Parses simple front matter like `title` and `order`
- Renders each page with `templates/base.html`
- Generates navigation links for all pages
- Copies files from `static/` into `output/static/`
- Writes the final site into `output/`

## Optional CLI Arguments

You can override the default directories:

```bash
python ssg.py build --content content --templates templates --output output --static static
```

## Run Tests

The project includes a comprehensive test suite covering the builder logic. Run all tests with:

```bash
python -m unittest tests -v
```

### Test Categories

- **Front Matter Parsing**: Extracting metadata from Markdown front matter
- **Title Extraction**: Resolving page titles from metadata, headings, or filenames
- **Markdown Conversion**: Converting Markdown to HTML with code blocks and styling
- **Page Creation**: Parsing complete pages and preserving directory structure
- **File Discovery**: Finding all Markdown files recursively
- **Navigation**: Building relative navigation links for all pages
- **Stylesheet Paths**: Computing correct relative paths for CSS files at different depths
- **Integration**: Full build process from content to output files

### Helper Script: Test The Markdown Pipeline

To run the legacy helper script that verifies Markdown conversion and file discovery:

```bash
python test_phase2.py
```

## Preview The Generated Site

After building, start a local server from the `output/` directory:

### Windows PowerShell

```powershell
cd output
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

You can also open individual files directly, for example `output/index.html`.

## Front Matter Format

Markdown files can include simple front matter at the top:

```markdown
---
title: Home
order: 1
---

# Welcome
```

- `title` controls the page title and navigation label
- `order` controls navigation order

If front matter is missing, the generator falls back to the first Markdown heading or the file name.

## Example Workflow

```bash
python ssg.py build
cd output
python -m http.server 8000
```

## Output Mapping

The build preserves the folder structure from `content/`:

```text
content/blog/post.md -> output/blog/post.html
content/guides/getting-started.md -> output/guides/getting-started.html
```

### Instructions on how to run 

```pip install -r requirements.txt
python ssg.py build
python -m unittest tests -v```
