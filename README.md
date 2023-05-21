# Serienbrief Generator GLK1

Einfaches Python-Script, dass es erlaubt mehrere PDFs zusammenzufügen und mit einem Namen zu versehen

## Running

```bash
python3 main.py \
--csv-file "./resources/empfaenger.csv" \
--pdfs "./resources/pdf1.pdf,./resources/pdf2.pdf,./resources/pdf3.pdf" \
--output "./output/Test.pdf"
```


## CSV-File

```csv
Vorname,Nachname,pdf1,pdf2,pdf3
Cyrill,Püntener,True,False,True
Tim,Tester,True,True,True
Max,Musterman,True,False,False
```