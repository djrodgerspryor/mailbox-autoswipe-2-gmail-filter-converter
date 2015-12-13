#!/usr/bin/env python3
import argparse
from enum import Enum

class Actions(Enum):
    ARCHIVE = 0
    DELETE = 1

class SelectorTypes(Enum):
    FROM = 0
    TO = 1
    SUBJECT_CONTAINS = 2

CSV_ACTIONS_2_ENUM_VALUE = {
    "deleted": Actions.ARCHIVE,
    "archive": Actions.DELETE,
}

CSV_SELECTOR_TYPES_2_ENUM_VALUE = {
    "from": SelectorTypes.FROM,
    "to": SelectorTypes.TO,
    "subject": SelectorTypes.SUBJECT_CONTAINS,
}

# Turn csv columns into a 'rule' dict
def csv_row_2_rule(action, _, selector_type, *args):
    # The last value is the usage count, all others are part of the selector
    *selector_values, usage_count = args

    selector = {
        "type": CSV_SELECTOR_TYPES_2_ENUM_VALUE[selector_type]
    }

    if selector['type'] in [SelectorTypes.FROM, SelectorTypes.TO]:
        selector['email_address'] = selector_values[0]

    elif selector['type'] == SelectorTypes.SUBJECT_CONTAINS:
        selector['subject_substrings'] = selector_values

    else:
        raise Error("Unknown selector type: '%s'/%s" % (selector_type, selector['type']))

    return {
        "action": CSV_ACTIONS_2_ENUM_VALUE[action],
        "selector": selector,
        "usage_count": int(usage_count),
    }

# Open and parse a mailbox CSV file and produce an array of 'rule' dicts
def parse_mailbox_csv(input_filename):
    print("Opening '%s'..." % input_filename)
    with open(input_filename) as f:
        print("Parsing '%s'..." % input_filename)
        return [csv_row_2_rule(*(value.strip().strip('"') for value in line.split(','))) for line in f]

# Accepts an array of rule-dicts (like the ones produced by csv_row_2_rule)
def rule_2_gmail_xml_node(rule):
    from lxml import etree

    rule_node = etree.Element('entry')

    rule_node.append(etree.Element('category', { 'term': 'filter' }))
    rule_node.append(etree.Element('title', { 'text': 'Mail Filter' }))
    rule_node.append(etree.Element('content'))


    # Selector #

    if rule['selector']['type'] == SelectorTypes.TO:
        rule_node.append(etree.Element('{http://schemas.google.com/apps/2006}property', { 'name': 'to', 'value': rule['selector']['email_address'] }))

    elif rule['selector']['type'] == SelectorTypes.FROM:
        rule_node.append(etree.Element('{http://schemas.google.com/apps/2006}property', { 'name': 'from', 'value': rule['selector']['email_address'] }))

    elif rule['selector']['type'] == SelectorTypes.SUBJECT_CONTAINS:
        # Build a selector string which google will parse
        subject_selector = "(%s)" % ' AND '.join(('"%s"' % subject_substring) for subject_substring in rule['selector']['subject_substrings'])

        rule_node.append(etree.Element('{http://schemas.google.com/apps/2006}property', { 'name': 'subject', 'value': subject_selector }))


    # Action #

    if rule['action'] == Actions.ARCHIVE:
        rule_node.append(etree.Element('{http://schemas.google.com/apps/2006}property', { 'name': 'shouldArchive', 'value': 'true' }))

    elif rule['action'] == Actions.DELETE:
        rule_node.append(etree.Element('{http://schemas.google.com/apps/2006}property', { 'name': 'shouldTrash', 'value': 'true' }))

    return rule_node

# Accepts an array of rule-dicts (like the ones produced by csv_row_2_rule)
def dump_gmail_xml(rules, output_filename):
    from lxml import etree

    print("Exporting to '%s'..." % output_filename)

    root = etree.Element('feed', nsmap= { 'apps': 'http://schemas.google.com/apps/2006' })
    root.append(etree.Element('title', { 'text': 'Mail Filters' }))

    for rule in rules:
        root.append(
            rule_2_gmail_xml_node(rule)
        )

    with open(output_filename, 'wb') as f:
        f.write(
            etree.tostring(root, encoding="utf8", xml_declaration=True)
        )

if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description='Convert an exported CSV of mailbox autoswipe patterns to a gmail-compatible CSV file.')
    parser.add_argument('input_filename', nargs='?', default='./autoswipe_rules.csv', help='path to the Mailbox CSV file')
    parser.add_argument('--output-filename', '-o', dest='output_filename', default='./filters.xml', help='output path for Gmail XML filters file')
    args = parser.parse_args()

    # Do it
    dump_gmail_xml(
        parse_mailbox_csv(input_filename=args.input_filename),
        output_filename=args.output_filename,
    )

    print("done!")
