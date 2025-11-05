"""
Notebook to PDF Converter

This script converts Jupyter notebooks to PDF documents by extracting:
- Markdown cells (formatted text)
- Output images from code cells
- Excluding all code

Usage:
    python notebook_to_pdf.py <notebook_path>
    python notebook_to_pdf.py 01_business_insights_dashboard.ipynb

Output:
    PDF file generated in the same directory as this script

Requirements:
    - nbformat: Jupyter notebook parsing
    - reportlab: PDF generation
    - Pillow: Image handling

Install:
    pip install nbformat reportlab pillow
"""

import json
import sys
import base64
from pathlib import Path
from typing import Dict, List, Tuple
import nbformat
from io import BytesIO
from PIL import Image as PILImage

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class NotebookToPdfConverter:
    """Convert Jupyter notebook to PDF with markdown and images only"""

    def __init__(self, notebook_path: str):
        """
        Initialize converter with notebook path

        Args:
            notebook_path: Path to .ipynb file (absolute or relative)
        """
        self.notebook_path = Path(notebook_path)
        self.script_dir = Path(__file__).parent
        self.output_path = self.script_dir / f"{self.notebook_path.stem}.pdf"

        if not self.notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {self.notebook_path}")

        print(f"[*] Loading notebook: {self.notebook_path.name}")
        print(f"[*] Output directory: {self.script_dir}")
        print(f"[*] Output PDF: {self.output_path.name}")

        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for markdown elements"""

        # Title style (H1)
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # H2 style
        self.styles.add(ParagraphStyle(
            name='CustomH2',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=15,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))

        # H3 style
        self.styles.add(ParagraphStyle(
            name='CustomH3',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#555555'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=16
        ))

        # Bullet list style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceAfter=6,
            bulletIndent=10
        ))

        # Code style
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            backColor=colors.HexColor('#f4f4f4'),
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10,
            fontName='Courier'
        ))

    def load_notebook(self) -> nbformat.NotebookNode:
        """Load notebook from file"""
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            return nbformat.read(f, as_version=4)

    def parse_markdown(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Parse markdown text into structured elements

        Returns:
            List of (element_type, content, style_name) tuples
        """
        lines = text.split('\n')
        elements = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Headers
            if line.startswith('# '):
                elements.append(('paragraph', line[2:], 'CustomTitle'))
            elif line.startswith('## '):
                elements.append(('paragraph', line[3:], 'CustomH2'))
            elif line.startswith('### '):
                elements.append(('paragraph', line[4:], 'CustomH3'))
            elif line.startswith('#### '):
                elements.append(('paragraph', line[5:], 'CustomH3'))

            # Bullet points
            elif line.startswith('- ') or line.startswith('* '):
                content = '• ' + line[2:]
                elements.append(('paragraph', content, 'CustomBullet'))

            # Numbered lists
            elif len(line) > 2 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
                elements.append(('paragraph', line, 'CustomBullet'))

            # Code blocks
            elif line.startswith('```'):
                # Collect code block
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    elements.append(('code', code_text, 'CustomCode'))

            # Horizontal rule
            elif line in ['---', '***', '___']:
                elements.append(('spacer', '', ''))

            # Bold, italic, inline code handling (simplified)
            else:
                # Replace markdown formatting with reportlab XML tags
                formatted_text = line
                # Bold
                formatted_text = formatted_text.replace('**', '<b>').replace('**', '</b>')
                # Italic
                formatted_text = formatted_text.replace('*', '<i>').replace('*', '</i>')
                # Inline code
                formatted_text = formatted_text.replace('`', '<font face="Courier" color="#c7254e">')
                formatted_text = formatted_text.replace('`', '</font>')

                elements.append(('paragraph', formatted_text, 'CustomBody'))

            i += 1

        return elements

    def extract_images_from_outputs(self, notebook: nbformat.NotebookNode) -> List[Tuple[int, bytes]]:
        """
        Extract images from code cell outputs

        Returns:
            List of tuples (cell_index, image_bytes)
        """
        images = []

        for cell_idx, cell in enumerate(notebook.cells):
            if cell.cell_type != 'code':
                continue

            if not hasattr(cell, 'outputs'):
                continue

            for output_idx, output in enumerate(cell.outputs):
                # Handle display_data and execute_result outputs
                if output.output_type in ['display_data', 'execute_result']:
                    if 'data' in output:
                        # Check for image formats
                        for img_format in ['image/png', 'image/jpeg', 'image/jpg']:
                            if img_format in output.data:
                                # Decode base64 image
                                img_data = output.data[img_format]
                                img_bytes = base64.b64decode(img_data)
                                images.append((cell_idx, img_bytes))
                                print(f"  [+] Extracted image from cell {cell_idx + 1}, output {output_idx + 1}")

        return images

    def create_pdf_content(self, notebook: nbformat.NotebookNode, images: List[Tuple[int, bytes]]) -> List:
        """
        Create PDF content elements from notebook

        Returns:
            List of ReportLab flowable elements
        """
        story = []
        image_counter = 1
        images_dict = {cell_idx: img_bytes for cell_idx, img_bytes in images}

        # Add title
        title = self.notebook_path.stem.replace('_', ' ').title()
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Process cells
        for cell_idx, cell in enumerate(notebook.cells):
            if cell.cell_type == 'markdown':
                # Parse and add markdown content
                elements = self.parse_markdown(cell.source)

                for elem_type, content, style_name in elements:
                    if elem_type == 'paragraph':
                        try:
                            story.append(Paragraph(content, self.styles[style_name]))
                        except Exception as e:
                            # Fallback to plain text if formatting fails
                            story.append(Paragraph(content.replace('<', '&lt;').replace('>', '&gt;'),
                                                 self.styles['CustomBody']))
                    elif elem_type == 'code':
                        # Add code block
                        code_para = Paragraph(f'<font face="Courier" size="9">{content}</font>',
                                             self.styles['CustomCode'])
                        story.append(code_para)
                    elif elem_type == 'spacer':
                        story.append(Spacer(1, 0.2*inch))

                story.append(Spacer(1, 0.1*inch))

            # Add image if this cell produced one
            if cell_idx in images_dict:
                img_bytes = images_dict[cell_idx]

                try:
                    # Load image with PIL to get dimensions
                    pil_image = PILImage.open(BytesIO(img_bytes))
                    img_width, img_height = pil_image.size

                    # Calculate scaled dimensions to fit page width (6 inches max)
                    max_width = 6 * inch
                    max_height = 7 * inch

                    scale = min(max_width / img_width, max_height / img_height, 1.0)
                    display_width = img_width * scale
                    display_height = img_height * scale

                    # Save to temporary BytesIO
                    img_buffer = BytesIO(img_bytes)

                    # Add figure caption
                    story.append(Spacer(1, 0.2*inch))
                    story.append(Paragraph(f'<b>Figure {image_counter}</b>',
                                         self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))

                    # Add image
                    img = Image(img_buffer, width=display_width, height=display_height)
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))

                    image_counter += 1

                except Exception as e:
                    print(f"  [!] Warning: Could not add image from cell {cell_idx + 1}: {e}")
                    story.append(Paragraph(f'[Image {image_counter} - Display Error]',
                                         self.styles['CustomBody']))
                    image_counter += 1

        return story

    def convert_to_pdf(self, story: List) -> None:
        """Generate PDF from story elements"""
        print(f"\n[*] Converting to PDF...")

        # Create PDF document
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build PDF
        doc.build(story)

        print(f"[+] PDF generated successfully!")
        print(f"[*] Location: {self.output_path.absolute()}")

        # Get file size
        file_size = self.output_path.stat().st_size
        size_kb = file_size / 1024
        print(f"[*] File size: {size_kb:.2f} KB")

    def convert(self) -> Path:
        """
        Main conversion method

        Returns:
            Path to generated PDF file
        """
        print("\n" + "="*70)
        print("NOTEBOOK TO PDF CONVERTER")
        print("="*70)

        # Step 1: Load notebook
        print("\n[1/4] Loading notebook...")
        notebook = self.load_notebook()
        total_cells = len(notebook.cells)
        markdown_count = sum(1 for c in notebook.cells if c.cell_type == 'markdown')
        code_count = sum(1 for c in notebook.cells if c.cell_type == 'code')
        print(f"  [+] Total cells: {total_cells}")
        print(f"  [+] Markdown cells: {markdown_count}")
        print(f"  [+] Code cells: {code_count} (excluded from PDF)")

        # Step 2: Extract images
        print("\n[2/4] Extracting images from outputs...")
        images = self.extract_images_from_outputs(notebook)
        print(f"  [+] Extracted {len(images)} images")

        # Step 3: Create PDF content
        print("\n[3/4] Building PDF content...")
        story = self.create_pdf_content(notebook, images)
        print(f"  [+] Created {len(story)} content elements")

        # Step 4: Generate PDF
        print("\n[4/4] Generating PDF...")
        self.convert_to_pdf(story)

        print("\n" + "="*70)
        print("CONVERSION COMPLETE")
        print("="*70)

        return self.output_path


def main():
    """Main entry point for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python notebook_to_pdf.py <notebook_path>")
        print("\nExamples:")
        print("  python notebook_to_pdf.py 01_business_insights_dashboard.ipynb")
        print("  python notebook_to_pdf.py ../other_folder/my_notebook.ipynb")
        print("  python notebook_to_pdf.py C:/path/to/notebook.ipynb")
        sys.exit(1)

    notebook_path = sys.argv[1]

    try:
        converter = NotebookToPdfConverter(notebook_path)
        output_pdf = converter.convert()
        print(f"\n[+] Success! PDF saved to: {output_pdf}")

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
