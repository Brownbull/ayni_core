# Notebook to PDF Converter

Utility script to convert Jupyter notebooks to clean PDF documents containing only markdown content and visualizations (no code).

## Location

`notebooks/insights/notebook_to_pdf.py`

## Purpose

Converts Jupyter notebooks to presentation-ready PDF documents by:
- ✅ Extracting all markdown cells (formatted text, headers, lists, etc.)
- ✅ Including all visualizations (charts, graphs, images from code outputs)
- ❌ Excluding all Python code cells
- ✅ Professional formatting with custom styles

## Requirements

```bash
pip install nbformat reportlab pillow
```

**Already installed** in this project environment.

## Usage

### Basic Usage

```bash
cd notebooks/insights
python notebook_to_pdf.py <notebook_name>.ipynb
```

### Examples

```bash
# Convert business insights dashboard
python notebook_to_pdf.py 01_business_insights_dashboard.ipynb

# Convert product performance matrix
python notebook_to_pdf.py 02_product_performance_matrix.ipynb

# Convert with relative path
python notebook_to_pdf.py ../by_user/business_analyst_monthly_report.ipynb

# Convert with absolute path
python notebook_to_pdf.py C:/path/to/notebook.ipynb
```

### Output Location

PDFs are generated in the **same directory as the script** (`notebooks/insights/`), regardless of input notebook location.

**Example:**
```
Input:  notebooks/insights/01_business_insights_dashboard.ipynb
Output: notebooks/insights/01_business_insights_dashboard.pdf
```

## Features

### Markdown Parsing

The script converts markdown elements to professionally styled PDF content:

- **Headers:** H1, H2, H3, H4 with custom colors and spacing
- **Paragraphs:** Justified text with proper line spacing
- **Lists:** Bullet points and numbered lists with indentation
- **Code blocks:** Syntax highlighting for markdown code sections
- **Bold/Italic:** Preserved formatting
- **Horizontal rules:** Converted to visual spacers

### Image Extraction

- Extracts all images from code cell outputs
- Supports PNG and JPEG formats
- Automatically scales images to fit page width (max 6 inches)
- Adds figure captions ("Figure 1", "Figure 2", etc.)
- Handles high-resolution charts and visualizations

### PDF Styling

Professional styling with:
- **Title:** Large, bold header with custom color (#2c3e50)
- **Headers:** Hierarchical sizing and coloring
- **Body text:** Justified, readable font size (11pt)
- **Page size:** US Letter (8.5" × 11")
- **Margins:** 72pt (1 inch) on all sides
- **Colors:** Business-friendly color scheme

## Script Architecture

### Class: `NotebookToPdfConverter`

**Methods:**

1. `__init__(notebook_path)` - Initialize converter with path validation
2. `load_notebook()` - Load .ipynb file using nbformat
3. `parse_markdown(text)` - Convert markdown to structured elements
4. `extract_images_from_outputs(notebook)` - Extract base64 images from code outputs
5. `create_pdf_content(notebook, images)` - Build ReportLab flowables
6. `convert_to_pdf(story)` - Generate final PDF document
7. `convert()` - Main conversion orchestrator

### Custom Styles

Defined in `_setup_custom_styles()`:
- `CustomTitle` - H1 headers (24pt, bold)
- `CustomH2` - H2 headers (18pt, bold)
- `CustomH3` - H3 headers (14pt, bold)
- `CustomBody` - Body text (11pt, justified)
- `CustomBullet` - List items (11pt, indented)
- `CustomCode` - Code blocks (9pt, Courier, gray background)

## Tested Notebooks

Successfully tested with:

| Notebook | Pages | Images | Size | Status |
|----------|-------|--------|------|--------|
| 01_business_insights_dashboard.ipynb | 6 | 6 | 326 KB | ✅ Pass |
| 02_product_performance_matrix.ipynb | 4 | 4 | 337 KB | ✅ Pass |

## Output Example

### Console Output

```
[*] Loading notebook: 01_business_insights_dashboard.ipynb
[*] Output directory: C:\Projects\play\khujta_ai_business\notebooks\insights
[*] Output PDF: 01_business_insights_dashboard.pdf

======================================================================
NOTEBOOK TO PDF CONVERTER
======================================================================

[1/4] Loading notebook...
  [+] Total cells: 20
  [+] Markdown cells: 10
  [+] Code cells: 10 (excluded from PDF)

[2/4] Extracting images from outputs...
  [+] Extracted image from cell 8, output 1
  [+] Extracted image from cell 10, output 1
  [+] Extracted image from cell 12, output 1
  [+] Extracted image from cell 14, output 1
  [+] Extracted image from cell 16, output 1
  [+] Extracted image from cell 18, output 1
  [+] Extracted 6 images

[3/4] Building PDF content...
  [+] Created 78 content elements

[4/4] Generating PDF...

[*] Converting to PDF...
[+] PDF generated successfully!
[*] Location: C:\Projects\play\khujta_ai_business\notebooks\insights\01_business_insights_dashboard.pdf
[*] File size: 325.35 KB

======================================================================
CONVERSION COMPLETE
======================================================================

[+] Success! PDF saved to: C:\Projects\play\khujta_ai_business\notebooks\insights\01_business_insights_dashboard.pdf
```

## Use Cases

### 1. Executive Presentations

Convert insight notebooks to PDF for executive presentations (no code, just insights and visuals).

### 2. Client Reports

Generate client-ready reports from analysis notebooks.

### 3. Documentation

Create documentation PDFs from analysis notebooks with markdown explanations.

### 4. Archival

Archive analysis results in a portable, code-free format.

### 5. Sharing

Share results with non-technical stakeholders who don't need to see the implementation.

## Limitations

### Current Limitations

1. **Markdown parsing:** Simplified parser (doesn't support all markdown features like tables, nested lists)
2. **No syntax highlighting:** Code blocks in markdown shown in monospace but not syntax-highlighted
3. **Fixed page size:** US Letter only (not configurable)
4. **Image positioning:** All images placed after their respective markdown sections
5. **No table of contents:** PDFs don't include auto-generated TOC

### Known Issues

1. **Complex markdown:** Very complex markdown with nested elements may not render perfectly
2. **LaTeX math:** Mathematical equations in markdown are not rendered (shown as raw LaTeX)
3. **HTML in markdown:** Embedded HTML in markdown cells is not processed

### Future Enhancements (Potential)

- [ ] Add table of contents generation
- [ ] Support for markdown tables
- [ ] LaTeX math equation rendering
- [ ] Configurable page sizes (A4, Legal, etc.)
- [ ] Custom color themes
- [ ] Header/footer with page numbers
- [ ] Hyperlink preservation
- [ ] Table of figures

## Error Handling

The script includes comprehensive error handling:

- **FileNotFoundError:** Clear message if notebook doesn't exist
- **Image errors:** Warnings for images that can't be processed (continues conversion)
- **Markdown parsing:** Fallback to plain text if formatting fails
- **Unicode errors:** Fixed to work on Windows console (no emoji errors)

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'reportlab'`

**Solution:**
```bash
pip install reportlab
```

### Issue: `FileNotFoundError: Notebook not found`

**Solution:** Check the path is correct. Use absolute paths or run from correct directory.

### Issue: Images not appearing in PDF

**Possible causes:**
- Code cells didn't execute before conversion
- Images are in unsupported format (only PNG/JPEG supported)
- Image data corrupted

**Solution:** Re-run notebook to generate fresh outputs before conversion.

### Issue: Markdown formatting looks wrong

**Solution:** Check if using unsupported markdown features (tables, nested lists). Consider simplifying markdown.

## Development Notes

### Why ReportLab instead of WeasyPrint?

- **Windows compatibility:** ReportLab works reliably on Windows without additional dependencies
- **No external dependencies:** Doesn't require GTK+ or other system libraries
- **Pure Python:** Easier to install and maintain
- **Production-ready:** Stable, well-documented library

### Code Style

- Type hints for all function signatures
- Docstrings for all methods
- Single Responsibility Principle
- Error handling at all critical points
- Clean console output (no emojis for Windows compatibility)

## Version History

**v1.0 (2025-10-24)**
- Initial release
- Markdown parsing with custom styles
- Image extraction from code outputs
- Professional PDF generation
- Tested with 2 insight notebooks

## License

Part of the GabeDA Business Intelligence project.

## Author

Created using GabeDA Architect skill following Single Responsibility Principle and architectural best practices.

---

**Last Updated:** 2025-10-24
**Script Location:** `notebooks/insights/notebook_to_pdf.py`
**Dependencies:** nbformat, reportlab, pillow
