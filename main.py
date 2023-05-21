import argparse
import io
import os
from copy import copy

import pandas as pd
from pypdf import PdfMerger, PdfWriter, PdfReader, Transformation
from reportlab.pdfgen.canvas import Canvas


class PDFAnnotator:
    def __init__(self, template):
        self.template_pdf = PdfReader(open(template, "rb"))
        self.template_pages = self.template_pdf.pages

        self.packet = io.BytesIO()
        self.c = Canvas(self.packet,
                        pagesize=(self.template_pages[0].mediabox.width, self.template_pages[0].mediabox.height))

    def addText(self, text, point):
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
    parser.add_argument('--pdfs', help='Path of the PDF files containing the letter')

    parser.add_argument('--output', help='Path of the output file name')

    args = parser.parse_args()

    csv_file_path = args.csv_file
    pdfs_files = args.pdfs.split(',')

    # strip the file name from the path and the file extension
    pdfs_files = list(map(lambda x: x.strip(), pdfs_files))

    pdfs_file_name = list(map(lambda x: x.split('/')[-1].split('.')[0].strip(), copy(pdfs_files)))

    output_file = args.output

    # use pandas to read the csv file
    df = pd.read_csv(csv_file_path, sep=',')

    # combine the pdfs to a single document, but select only the ones that are needed,
    # i.g. only pdfs_file_name that are marked as true in the corresponding column
    merger = PdfMerger()

    for _, row in df.iterrows():

        for i, pdf_file_name in enumerate(pdfs_file_name):

            # convert the row into a dictionary and check if the pdf_file_name is marked as true
            dict_row = dict(row)
            if pdf_file_name in dict_row and dict_row[pdf_file_name]:
                # annotate the PDF
                annotator = PDFAnnotator(pdfs_files[i])
                annotator.addText(dict_row['Vorname'], (500, 800))
                annotator.addText(dict_row['Nachname'], (500, 780))
                annotator.generate("temp.pdf")

                # append to master document and delete the temporary file
                merger.append('temp.pdf')
                os.remove("temp.pdf")

            # add an empty page if the pdf has an odd number of pages
            page_count = len(merger.pages)
            if page_count % 2 != 0:
                merger.append('empty.pdf')

    # write the merged pdf to a file
    merger.write(output_file)
    merger.close()


if __name__ == '__main__':
    main()
