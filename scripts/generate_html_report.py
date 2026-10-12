"""
Generates a styled, publication-ready HTML version of the Technical Report.
Includes KaTeX math rendering, responsive typography, table formatting, and print CSS.
"""

import os
import markdown_it

def build_html_report():
    md_path = "docs/TECHNICAL_REPORT.md"
    html_path = "docs/TECHNICAL_REPORT.html"

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    md = markdown_it.MarkdownIt()
    body_html = md.render(md_content)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Task Placement: DAA Technical Report</title>
    <!-- KaTeX for Math -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.65;
            color: #24292e;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #ffffff;
        }}
        h1, h2, h3, h4 {{
            color: #0d47a1;
            font-weight: 700;
        }}
        h1 {{
            border-bottom: 2px solid #1e88e5;
            padding-bottom: 12px;
            font-size: 2.2em;
            margin-top: 0;
        }}
        h2 {{
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 8px;
            margin-top: 36px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 0.95em;
        }}
        th, td {{
            border: 1px solid #d0d7de;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #fbfcfd;
        }}
        pre, code {{
            background-color: #f6f8fa;
            border-radius: 4px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
        }}
        code {{
            padding: 2px 5px;
            font-size: 0.9em;
        }}
        pre {{
            padding: 16px;
            overflow-x: auto;
            border: 1px solid #e1e4e8;
        }}
        pre code {{
            padding: 0;
            background: none;
        }}
        blockquote {{
            border-left: 4px solid #1e88e5;
            margin: 16px 0;
            padding: 8px 16px;
            background-color: #f1f8ff;
            color: #032f62;
        }}
        hr {{
            border: none;
            border-top: 1px solid #eaecef;
            margin: 30px 0;
        }}
        @media print {{
            body {{
                max-width: 100%;
                padding: 10mm;
                font-size: 11pt;
            }}
            h1, h2 {{
                page-break-after: avoid;
            }}
            table, pre {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
{body_html}
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Generated HTML Technical Report: {html_path}")

if __name__ == "__main__":
    build_html_report()
