import json
import os

import pytest

from sforparser.apd import scraper

INPUT_FILE = 'data/apd/input.txt'


@pytest.fixture
def data():
    json_str = scraper(open(INPUT_FILE))

    artifact_dir = os.getenv('CIRCLE_ARTIFACTS')
    if artifact_dir:
        artifact_file = os.path.join(artifact_dir, 'apd.json')
        open(artifact_file, 'w').write(json_str)

    return json.loads(json_str)


def test_output_strips_email_spaces(data):
    offensive_field = data[70]["locations"][0]["emails"]
    expected = [
        "ronald.sanders@sfdph.org",
        "juanita.alvarado@sfdph.org",
        "joseph.calderon@sfdph.org",
    ]

    assert offensive_field == expected
