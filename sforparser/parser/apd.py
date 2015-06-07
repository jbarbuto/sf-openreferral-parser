import json
import logging
import re
import sys

from . import BaseParser
from ..helper.string_converter import EnglishStringConverter

# Mapping of APD fields to ohana
FIELDS = [
    ('Administration Mailing Address', 'address'),
    ('Administrative Office', 'address'),
    ('Office location', 'address'),
    ('Intake location', 'address'),
    ('Mailing Address', 'address'),
    ('Main Office', 'address'),
    ('Corporate Office', 'address'),
    ('24-Hour Hotline', 'phone'),
    ('Toll-Free Telephone', 'phone'),
    ('General Inquiries', 'phone'),
    ('Emergency Center Phone', 'phone'),
    ('Emergency Bed Call-in #', 'phone'),
    ('Address', 'address'),
    ('Primary Community Served', 'audience'),
    ('Notes', 'description'),
    ('Info Line', 'phone'),
    ('Phone', 'phone'),
    ('Main Phone', 'phone'),
    ('Intake Phone', 'phone'),
    ('Hours', 'hours'),
    ('Clinic Hours', 'hours'),
    ('Hours/Meeting times', 'hours'),
    ('Intake Hours', 'hours'),
    ('Drop-in Hours', 'hours'),
    ('Program Hours', 'hours'),
    ('Specific Intake Days and Times', 'hours'),
    ('Days and Hours', 'hours'),
    ('TDD', 'phone'),
    ('Fax', 'fax'),
    ('Email', 'emails'),
    ('E-mail', 'emails'),
    ('url', 'urls'),
    ('Languages Spoken', 'languages'),
    ('What to Bring', 'how_to_apply'),
    ('Things to Know', 'how_to_apply'),
    ('Accessibility', 'accessibility'),
    ('Client fees, if any', 'fees'),
    ('Client fee, if any', 'fees'),
    ('Client fees', 'fees'),
    ('Eligible Population', 'audience'),
    ('Eligible Populations', 'audience'),
    ('Eligible Population Served', 'audience'),
    ('Not Eligible', 'eligibility'),
    ('Restrictions', 'eligibility'),
    ('Direct Services', 'keywords'),
    ('Direct Service', 'keywords'),
    ('Faith Based', 'description'),
    ('Contact Persons', 'name'),
    ('Contact Person', 'name'),
    ('Contact', 'name'),
    ('Person to Contact', 'name'),
    ('Intake Days', 'hours'),
    ('Facility Hours', 'hours'),
    ('Drop-In Clinic Hours', 'hours'),
    ('Location', 'address'),
    ('Locations', 'address'),
    ('Services', 'keywords'),
    ('Days and Times', 'hours'),
    ('Note', 'description'),
]
FINAL_FIELD = 'direct services'


class ApdParser(BaseParser):

    def parse(self, data):
        entries = []

        not_matched = []
        entry_line_num = 0
        for line in data:
            line = line.strip()

            # Skip if it's blank or contains a known header
            if line and not ('Things To Know' in line or 'To Get Connected' in line):
                entry_line_num += 1

                # We're at the first line of the file or the first line
                # of a new entry, must be the title
                if entry_line_num == 1:
                    entry = self.init_entry()
                    # First line often contains two values, org and program
                    for i, items in enumerate(line.split(' ' * 3)):
                        if i == 0:
                            logging.debug("Organization: %s", items)
                            entry['organization_name'] = items
                        else:
                            logging.debug("Program: %s", items)
                            entry['program_name'] = items
                # Second line is the description...hopefully
                elif entry_line_num == 2:
                    logging.debug("Description: %s", line)
                    entry['description'] = line
                else:
                    # Loop through every field and look for a match
                    for field in FIELDS:
                        apd_field, ohana_field = field
                        matched = self.match_with_field(apd_field, line)
                        if matched:
                            field_value = line.split(':')[-1].replace(';', ',')
                            entry[ohana_field] += field_value.strip()

                            # Are we at the end of the record?
                            if apd_field.lower() == FINAL_FIELD:
                                # TODO: figure out what to do with extra data
                                # that doesn't match a known field
                                if not_matched:
                                    logging.warn("THIS DATA NOT MATCHED:\n%s",
                                                 '\n'.join(not_matched))

                                entries.append(entry)

                                not_matched = []
                                entry_line_num = 0
                            # Found a match so break out of loop and go to next line
                            break
                    else:
                        # Load all non-matching lines into one field so we can analyze
                        not_matched.append(line)

        entries = [self.to_open_referral(e) for e in entries]
        return json.dumps(entries, indent=2, ensure_ascii=True, sort_keys=True)

    def init_entry(self):
        entry = {
            'eligibility': "",
            'fees': "",
            'accessibility': "",
            'audience': "",
            'how_to_apply': "",
            'hours': "",
            'emails': "",
            'urls': "",
            'languages': "",
            'fax': "",
            'phone': "",
            'name': "",
            'address': "",
            'audience': "",
            'description': "",
            'keywords': "",
            'organization_name': "",
            'program_name': "",
        }
        return entry

    def match_with_field(self, field, line):
        return line.split(':')[0].lower() == field.lower()

    def to_open_referral(self, entry):
        # Default values
        city, state, zipcode, = '', '', ''
        languages = entry['languages']
        emails = entry['emails']
        short_description = entry['description'][:100]

        phonePattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')

        newphone = phonePattern.search(entry['phone'])
        if newphone:
            newphonebase = newphone.group(1) + newphone.group(2) + newphone.group(3)
            newext = newphone.group(4)
        else:
            newphonebase = ""
            newext = ""

        newfax = phonePattern.search(entry['fax'])
        if newfax:
            newfaxbase = newfax.group(1) + newfax.group(2) + newfax.group(3)
        else:
            newfaxbase = ""

        # Apply fanciness
        if ', San Francisco' in entry['address']:
            entry['address'] = entry['address'].replace(', San Francisco', '')
            city = 'San Francisco'
        if ', CA' in entry['address']:
            entry['address'] = entry['address'].replace(', CA', '')
            state = 'CA'

        zipcode_regex = '( [0-9]{5})$'
        match = re.search(zipcode_regex, entry['address'])
        if match:
            zipcode = match.group(0).strip()
            entry['address'] = re.sub(zipcode_regex, '', entry['address'])

        if not entry['program_name'].strip():
            entry['program_name'] = entry['organization_name']

        english_string_converter = EnglishStringConverter()
        languages = english_string_converter.to_list(languages)
        emails = english_string_converter.to_list(emails)

        comma_pos = entry['name'].find(',')
        full_len = len(entry['name'])

        if comma_pos > 0:
            contact_name = entry['name'][0:comma_pos]
            contact_title = entry['name'][comma_pos+1:full_len].strip()
        else:
            contact_name = entry['name']
            contact_title = 'NA'

        # Look here for field definitions: https://github.com/sfbrigade/ohana-api/wiki/Populating-the-Postgres-database-from-a-JSON-file
        return {
            'name': entry['organization_name'],
            'locations': [
                {
                    'name': entry['program_name'],
                    'contacts_attributes': [
                        {
                            'name': contact_name,
                            # TODO: need to split out from name based on comma
                            'title': contact_title,
                        }
                    ],
                    'description': entry['description'],
                    'short_desc': short_description,
                    'address_attributes':{
                        'street': entry['address'],
                        # TODO: need to grab out cities other than SF
                        'city': city,
                        'state': state,
                        'zip': zipcode,
                    },
                    "hours": entry['hours'],
                    "accessibility": [
                        entry['accessibility'],
                    ],
                    "languages": languages,
                    "emails": emails,
                    "faxes_attributes": [
                        {
                            "number": newfaxbase,
                        }
                    ],
                    "phones_attributes": [
                        {
                            "number": newphonebase,
                            "extension": newext,
                        }
                    ],
                    "urls": [
                        entry['urls'],
                    ],
                    "services_attributes": [
                        {
                            "name": entry['program_name'],
                            "description": entry['description'],
                            "audience": entry['audience'],
                            "eligibility": entry['eligibility'],
                            "fees": entry['fees'],
                            "how_to_apply": entry['how_to_apply'],
                            # TODO: wrap items in double quotes.  I think...
                            "keywords": [entry['keywords']],
                        }
                    ],
                }
            ],
        }


if __name__ == '__main__':
    parser = ApdParser()
    print(parser.parse(open(sys.argv[1])))
