import argparse
import io
import os

import pandas as pd
from pypdf import PdfWriter, PdfReader, Transformation
from reportlab.pdfgen.canvas import Canvas


class PDFAnnotator:
    def __init__(self, template):
        self.template_pdf = PdfReader(open(template, "rb"))
        self.template_pages = self.template_pdf.pages

        self.packet = io.BytesIO()
        self.c = Canvas(self.packet,
                        pagesize=(self.template_pages[0].mediabox.width, self.template_pages[0].mediabox.height))

    def addText(self, text, point, bold_font=False, font_size=12):
        self.c.setFont("Helvetica-Bold" if bold_font else "Helvetica", font_size)
        self.c.drawString(point[0], point[1], text)

    def merge(self):
        self.c.save()
        self.packet.seek(0)
        result_pdf = PdfReader(self.packet)
        result = result_pdf.pages[0]

        self.output = PdfWriter()

        op = Transformation().rotate(0).translate(tx=0, ty=0)
        result.add_transformation(op)

        for page in self.template_pages:
            page.merge_page(result)
            self.output.add_page(page)

    def generate(self, dest):
        self.merge()
        outputStream = open(dest, "wb")
        self.output.write(outputStream)


def main():
    parser = argparse.ArgumentParser(description="""

    Serienbrief Generator - Ein Programm zum Erstellen von Serienbriefen.

    Generiert Druckdateien im PDF-Format basierend auf mehreren Input-Dateien und einer
    CSV Datei mit den Namen der Empfänger.
    """)
    parser.add_argument('--csv-file', help='Path of the CSV file containing the names')
    parser.add_argument('--pdf-base-path', help='Base path of the PDF files (e.g., "resources/")')
    parser.add_argument('--merge', help='Merge the PDF files into a single document', action='store_true')
    parser.add_argument('--output', help='Path of the output file name or directory for individual PDFs')

    args = parser.parse_args()

    csv_file_path = args.csv_file
    pdf_base_path = args.pdf_base_path  # This will be the base path like 'resources/pdf_name'
    output_location = args.output  # This can be a file or a directory

    # use pandas to read the csv file
    df = pd.read_csv(csv_file_path, sep=',')

    merger = PdfWriter()

    for i, row in df.iterrows():
        dict_row = dict(row)
        name = str(dict_row['Ceviname']) if 'Ceviname' in dict_row and str(dict_row['Ceviname']) != "nan" else str(
            dict_row['Vorname'])

        # Determine the department, default to an empty string if not present
        department = str(dict_row.get('Abteilung', '')).strip()
        if department == "nan":  # Handle pandas 'nan' representation
            department = ""

        for key, value in dict_row.items():
            # Check if the column name starts with 'pdf_' and the value is a number
            if key.startswith('pdf_') and isinstance(value, (int, float)):
                pdf_name_prefix = key  # e.g., 'pdf_namea'
                # remove 'pdf_' prefix to get the base name
                pdf_name_prefix = pdf_name_prefix[4:]
                pdf_version = int(value)  # e.g., 2

                # Construct the full PDF file path
                # Assuming PDFs are named like 'pdf_namea_1.pdf', 'pdf_namea_2.pdf', etc.
                # The pdf_base_path should be something like 'resources' if your PDFs are in 'resources/pdf_namea_1.pdf'
                pdf_file_to_annotate = os.path.join(pdf_base_path, f"{pdf_name_prefix}_{pdf_version}.pdf")

                if os.path.exists(pdf_file_to_annotate):
                    # Annotate the PDF
                    annotator = PDFAnnotator(pdf_file_to_annotate)
                    annotator.addText(name, (50, 795), bold_font=True, font_size=16)
                    if department:  # Only add department if it exists
                        annotator.addText(f"({department})", (50, 778))

                    # Create a temporary file name to avoid conflicts
                    temp_pdf_name = f"temp_{os.getpid()}_{i}_{key}.pdf"
                    annotator.generate(temp_pdf_name)

                    # Append to master document and delete the temporary file
                    merger.append(temp_pdf_name)
                    fill_double_page(merger)
                    os.remove(temp_pdf_name)
                else:
                    print(f"Warning: PDF file not found: {pdf_file_to_annotate}. Skipping.")

        fill_double_page(merger)

        # save the pdf if not merging
        if not args.merge:
            # Sanitize department for filename
            sanitized_department = department.replace('/', '_').replace(' ', '')
            output_file_name = f"{name}_{sanitized_department}.pdf"

            # Ensure the output directory exists
            output_dir = output_location
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            full_output_path = os.path.join(output_dir, output_file_name)

            # write the merged pdf to a file
            merger.write(full_output_path)
            merger.close()
            merger = PdfWriter()  # Reset merger for the next individual document

    if args.merge:
        # For merged output, `output_location` should be the full output file path
        merger.write(output_location)
        merger.close()


def fill_double_page(merger):
    # add an empty page if the pdf has an odd number of pages
    page_count = len(merger.pages)
    if page_count > 0 and page_count % 2 != 0:
        # You'll need an 'empty.pdf' file for this to work.
        # Make sure 'empty.pdf' exists in your execution directory or provide a full path.
        empty_pdf_path = "empty.pdf"
        if os.path.exists(empty_pdf_path):
            merger.append(empty_pdf_path)
        else:
            print(f"Warning: 'empty.pdf' not found at '{empty_pdf_path}'. Cannot add blank page.")


if __name__ == '__main__':
    main()
