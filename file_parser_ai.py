import csv


def parse_csv(filename):
    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)