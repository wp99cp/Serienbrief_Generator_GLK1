# Serienbrief Generator GLK1

Einfaches Python-Script, dass es erlaubt mehrere PDFs zusammenzufügen und mit einem Namen zu versehen

## Running

```bash
python3 main.py \
  --csv-file "./resources/empfaenger.csv" \
  --output "./output/Serienbrief.pdf" \
  --pdf-base-path "./resources"
```

## CSV-File

```csv
Vorname,Nachname,Ceviname,Abteilung,Gruppe,pdf_Infobrief,pdf_TNK,pdf_Geschichte,pdf_Spiel,pdf_Knoten
Cyrill,Püntener,JPG,Z11,1,1,1,5,6,7
```
