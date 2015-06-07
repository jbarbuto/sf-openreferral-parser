from sforparser.helper.string_converter import EnglishStringConverter

class TestEnglishStringConverterToList(object):
    def setup_class(cls):
        cls.esc = EnglishStringConverter()

    def test_language_string_with_ampersand(self):
        languages = self.esc.to_list("English & Spanish")

        assert languages == ["English", "Spanish"]

    def test_language_string_with_commas(self):
        languages = self.esc.to_list("English, Spanish")

        assert languages == ["English", "Spanish"]

    def test_language_string_with_and(self):
        languages = self.esc.to_list("English and Spanish")

        assert languages == ["English", "Spanish"]

    def test_embedded_and(self):
        email_string = "justin.sanders@example.com and foo@example.com"
        emails = self.esc.to_list(email_string)

        assert emails == ["justin.sanders@example.com", "foo@example.com"]

    def test_trailing_period(self):
        languages = self.esc.to_list("French, Spanish.")

        assert languages == ["French", "Spanish"]

    def test_oxford_comma(self):
        language_string = "Tagalog, Farsi, and Chinese"
        languages = self.esc.to_list(language_string)

        assert languages == ["Tagalog", "Farsi", "Chinese"]

    def test_or(self):
        emails = "foo@example.com, or bar@example.com or baz@example.com"
        email_list = self.esc.to_list(emails)

        assert email_list == ["foo@example.com", "bar@example.com", "baz@example.com"]

    def test_ampersand(self):
        languages = self.esc.to_list("French, & Spanish")

        assert languages == ["French", "Spanish"]
