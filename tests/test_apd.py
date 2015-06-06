import json

from sforparser.apd import scraper

INPUT_FILE = 'data/apd/input.txt'


def test_output_strips_email_spaces():
    json_str = scraper(open(INPUT_FILE))

    data = json.loads(json_str)
    offensive_field = data[70]["locations"][0]["emails"]
    expected = [
        "ronald.sanders@sfdph.org",
        "juanita.alvarado@sfdph.org",
        "joseph.calderon@sfdph.org",
    ]

    assert offensive_field == expected
