import json
import logging
import re
import sys

from sforparser.parsers import english

# Mapping of APD fields to ohana
IMPORTANT_WORDS = [
    ('Administration Mailing Address', "address"),
    ('Administrative Office', "address"),
    ('Office location', "address"),
    ('Intake location', "address"),
    ('Mailing Address', "address"),
    ('Main Office', "address"),
    ('Corporate Office', "address"),
    ('24-Hour Hotline', "phone"),
    ('Toll-Free Telephone', "phone"),
    ('General Inquiries', "phone"),
    ('Emergency Center Phone', "phone"),
    ('Emergency Bed Call-in #', "phone"),
    ('Address', "address"),
    ('Primary Community Served', "audience"),
    ('Notes', "description"),
    ('Info Line', "phone"),
    ('Phone', "phone"),
    ('Main Phone', "phone"),
    ('Intake Phone', "phone"),
    ('Hours', "hours"),
    ('Clinic Hours', "hours"),
    ('Hours/Meeting times', "hours"),
    ('Intake Hours', "hours"),
    ('Drop-in Hours', "hours"),
    ('Program Hours', "hours"),
    ('Specific Intake Days and Times', "hours"),
    ('Days and Hours', "hours"),
    ('TDD', "phone"),
    ('Fax', "fax"),
    ('Email', "emails"),
    ('E-mail', "emails"),
    ('url', "urls"),
    ('Languages Spoken', "languages"),
    ('What to Bring', "how_to_apply"),
    ('Things to Know', "how_to_apply"),
    ('Accessibility', "accessibility"),
    ('Client fees, if any', "fees"),
    ('Client fee, if any', "fees"),
    ('Client fees', "fees"),
    ('Eligible Population', "audience"),
    ('Eligible Populations', "audience"),
    ('Eligible Population Served', "audience"),
    ('Not Eligible', "eligibility"),
    ('Restrictions', "eligibility"),
    ('Direct Services', "keywords"),
    ('Direct Service', "keywords"),
    ('Faith Based', "description"),
    ('Contact Persons', "name"),
    ('Contact Person', "name"),
    ('Contact', "name"),
    ('Person to Contact', "name"),
    ('Intake Days', "hours"),
    ('Facility Hours', "hours"),
    ('Drop-In Clinic Hours', "hours"),
    ('Location', "address"),
    ('Locations', "address"),
    ('Services', "keywords"),
    ('Days and Times', "hours"),
    ('Note', "description"),
]


class Entry:
    pass


def scraper(data):
    item_count = 1
    not_matched = ''
    record_line_num = 1
    direct_services = ''
    entries = []

    for i, line in enumerate(data):
        line = line.strip()

        # Skip if it's blank or contains a known header
        if line and not ('Things To Know' in line or 'To Get Connected' in line):
            # We're at the first line of the file or the first line
            # of a new record, must be the title
            if record_line_num == 1:
                were_at = 0
                entry = Entry()
                setattr(entry, "eligibility", "")
                setattr(entry, "fees", "")
                setattr(entry, "accessibility", "")
                setattr(entry, "audience", "")
                setattr(entry, "how_to_apply", "")
                setattr(entry, "hours", "")
                setattr(entry, "emails", "")
                setattr(entry, "urls", "")
                setattr(entry, "languages", "")
                setattr(entry, "fax", "")
                setattr(entry, "phone", "")
                setattr(entry, "name", "")
                setattr(entry, "address", "")
                setattr(entry, "audience", "")
                setattr(entry, "description", "")
                setattr(entry, "keywords", "")
                setattr(entry, "organization_name", "")
                setattr(entry, "program_name", "")

                # First line often contains two values, org and program
                for items in line.split(" " * 3):
                    if were_at == 0:
                        logging.debug("Organization: %s", items)
                        setattr(entry, "organization_name", items)

                        were_at += 1
                    else:
                        logging.debug("Program: %s", items)
                        setattr(entry, "program_name", items)
                were_at = 0

            # Second line is the description...hopefully
            elif record_line_num == 2:
                logging.debug("Description: %s", line)
                setattr(entry, "description", line)
            else:
                matched = False

                # Loop through every important word and look for a match
                # on this line
                for word in IMPORTANT_WORDS:

                    matched = match_with_word(word, line)
                    if matched:

                        label_text = line.split(":")[0] + ':'
                        just_data = line.replace(label_text, "").strip();
                        setattr(entry, word[1], getattr(entry, word[1]) + just_data.replace(";",",").strip())

                        # Are we at the end of the record?
                        if word[0].lower() == "direct services":
                            direct_services += "; " + line
                            # Print the list of non matching data so we
                            # can deal with later
                            if not_matched:
                                logging.warn("THIS DATA NOT MATCHED: %s", not_matched)

                            # TODO: figure out what to do with this extra
                            # info that doesn't match a field label

                            entries.append(entry)

                            item_count += 1
                            not_matched = ''
                            record_line_num = 0
                        # Found a match so break out of loop and go to
                        # next word
                        break

                if not matched:
                    # Load all of these non-matching lines into one field
                    # so we can analyze
                    not_matched += "\n" + line

            record_line_num += 1

    entries = [to_open_referral(e) for e in entries]
    return json.dumps(entries, indent=2, ensure_ascii=True)


def match_with_word(word, line):
    return line.split(":")[0].lower() == word[0].lower()


def to_open_referral(entry):
    # Default values
    city, state, zip, = '', '', ''
    languages = entry.languages
    emails = entry.emails
    short_description = entry.description[:100]

    phonePattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')

    newphone = phonePattern.search(entry.phone)

    newphonebase = ""
    newext = ""

    if newphone:
        newphonebase = newphone.group(1) + newphone.group(2) + newphone.group(3)
        newext = newphone.group(4)

    newfax = phonePattern.search(entry.fax)

    newfaxbase = ""

    if newfax:
        newfaxbase = newfax.group(1) + newfax.group(2) + newfax.group(3)

    # Apply fanciness
    if ', San Francisco' in entry.address:
        entry.address = entry.address.replace(', San Francisco', '')
        city = 'San Francisco'
    if ', CA' in entry.address:
        entry.address = entry.address.replace(', CA', '')
        state = 'CA'
    zip_regex = '( [0-9]{5})$'
    match = re.search(zip_regex, entry.address)
    if match:
        zip = match.group(0).strip()
        entry.address = re.sub(zip_regex, '', entry.address)

    if not entry.program_name.strip():
        entry.program_name = entry.organization_name

    languages = english.parse_list(languages)
    emails = english.parse_list(emails)

    comma_pos = entry.name.find(',')
    full_len = len(entry.name)

    if comma_pos > 0:
        contact_name = entry.name[0:comma_pos]
        contact_title = entry.name[comma_pos+1:full_len].strip()
    else:
        contact_name = entry.name
        contact_title = 'NA'

    # Look here for field definitions: https://github.com/sfbrigade/ohana-api/wiki/Populating-the-Postgres-database-from-a-JSON-file
    return {
        'name': entry.organization_name,
        'locations': [
            {
                'name': entry.program_name,
                'contacts_attributes': [
                    {
                        'name': contact_name,
                        # TODO: need to split out from name based on comma
                        'title': contact_title,
                    }
                ],
                'description': entry.description,
                'short_desc': short_description,
                'address_attributes':{
                    'street': entry.address ,
                    # TODO: need to grab out cities other than SF
                    'city': city,
                    'state': state,
                    'zip': zip
                },
                "hours": entry.hours,
                "accessibility": [
                    entry.accessibility
                ],
                "languages": languages,
                "emails": emails,
                "faxes_attributes": [
                    {
                        "number": newfaxbase
                    }
                ],
                "phones_attributes": [
                    {
                        "number": newphonebase,
                        "extension": newext
                    }
                ],
                "urls": [
                    entry.urls
                ],
                "services_attributes": [
                    {
                        "name": entry.program_name,
                        "description": entry.description,
                        "audience": entry.audience,
                        "eligibility": entry.eligibility,
                        "fees": entry.fees,
                        "how_to_apply": entry.how_to_apply,
                        # TODO: wrap items in double quotes.  I think...
                        "keywords": [entry.keywords],
                    }
                ],
            }
        ],
    }


if __name__ == '__main__':
    print(scraper(open(sys.argv[1])))
