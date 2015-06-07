import re


def parse_list(list_string):
    split_list = list_string \
            .replace(" or ", " and ") \
            .replace(" & ", " and ") \
            .replace(", and ", " and ") \
            .replace(" and ", ",") \
            .split(",")

    return map(_strip, split_list)


def _strip(pre_string):
    post_string = re.sub(r'\. *$', '', pre_string)
    return post_string.strip()
