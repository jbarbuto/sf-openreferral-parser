import re


class AbstractStringConverter(object):
    list_conversions = []
    list_splitter = ','

    def to_list(self, pre_string):
        post_string = pre_string
        for conversion in self.list_conversions:
            post_string = post_string.replace(conversion[0], conversion[1])

        return [self._strip(s) for s in post_string.split(self.list_splitter)]

    def _strip(self, pre_string):
        raise NotImplementedError


class EnglishStringConverter(AbstractStringConverter):
    list_conversions = [
        (' or ', ' and '),
        (' & ', ' and '),
        (', and ', ' and '),
        (' and ', ','),
    ]

    def _strip(self, pre_string):
        post_string = re.sub(r'\. *$', '', pre_string)
        return post_string.strip()
