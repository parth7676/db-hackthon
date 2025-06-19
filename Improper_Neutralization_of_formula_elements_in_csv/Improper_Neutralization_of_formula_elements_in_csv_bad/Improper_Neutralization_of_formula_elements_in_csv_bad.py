# VULNERABLE
import csv
def export_csv_vulnerable(data):
    with open('export.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)