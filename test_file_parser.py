from file_parser_trad import parse_csv
def test_parse_csv_returns_list():
    result = parse_csv('sample.csv')
    assert isinstance(result, list) 




from file_parser_ai import parse_csv


def test_parse_csv():
    result = parse_csv("sample.csv")

    assert isinstance(result, list)
    assert len(result) == 3


def test_csv_rows_are_dictionaries():
    result = parse_csv("sample.csv")

    assert all(isinstance(row, dict) for row in result)


def test_csv_has_expected_columns():
    result = parse_csv("sample.csv")

    assert all("Name" in row for row in result)
    assert all("Age" in row for row in result)
    assert all("State" in row for row in result)


def test_first_row_contains_values():
    result = parse_csv("sample.csv")

    assert result[0]["Name"] == "James"
    assert result[0]["Age"] == "23"
    assert result[0]["State"] == "Florida"


