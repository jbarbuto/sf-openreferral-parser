from sforparser.parsers import english


def test_language_string_with_ampersand():
    languages = english.parse_list("English & Spanish")

    assert languages == ["English", "Spanish"]

def test_language_string_with_commas():
    languages = english.parse_list("English, Spanish")

    assert languages == ["English", "Spanish"]

def test_language_string_with_and():
    languages = english.parse_list("English and Spanish")

    assert languages == ["English", "Spanish"]

def test_embedded_and():
    email_string = "justin.sanders@example.com and foo@example.com"
    emails = english.parse_list(email_string)

    assert emails == ["justin.sanders@example.com", "foo@example.com"]

def test_trailing_period():
    languages = english.parse_list("French, Spanish.")

    assert languages == ["French", "Spanish"]

def test_oxford_comma():
    language_string = "Tagalog, Farsi, and Chinese"
    languages = english.parse_list(language_string)

    assert languages == ["Tagalog", "Farsi", "Chinese"]

def test_or():
    emails = "foo@example.com, or bar@example.com or baz@example.com"
    email_list = english.parse_list(emails)

    assert email_list == ["foo@example.com", "bar@example.com", "baz@example.com"]

def test_ampersand():
    languages = english.parse_list("French, & Spanish")

    assert languages == ["French", "Spanish"]
