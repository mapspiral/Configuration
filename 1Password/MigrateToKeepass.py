import csv
import xml.etree.ElementTree as xml

DEFAULT_GROUP_NAME = "Migrated from 1Password"

INPUT_FILE = "/Users/robertvd/Desktop/1PasswordTextExport.txt"

OUTPUT_FILE = "/tmp/migrated_file.xml"

XML_DOCTYPE = "<!DOCTYPE KEEPASSX_DATABASE>"


def migrate_line(p_csv_data, p_attributes, p_group_element):
    """Create a new KeePassX XML entry element for the specified CSV data"""
    entry_element = xml.SubElement(p_group_element, "entry")

    print "Migrate {0}".format(p_csv_data[p_attributes.index("title")])

    xml.SubElement(entry_element, "title").text = p_csv_data[p_attributes.index("title")]

    xml.SubElement(entry_element, "username").text = p_csv_data[p_attributes.index("username")]

    xml.SubElement(entry_element, "password").text = p_csv_data[p_attributes.index("password")]

    xml.SubElement(entry_element, "url").text = p_csv_data[p_attributes.index("URL/Location")]

    xml.SubElement(entry_element, "comment").text = p_csv_data[p_attributes.index("notes")]


def has_duplicate(p_entry_data, p_attributes, p_parent_element):
    """Check if data has a duplicate in the element tree"""

    # too bad etree cannot handle multiple xpath predicates
    possible_duplicates = p_parent_element.findall(
        ".//entry[title='{0}']".format(
            p_entry_data[p_attributes.index("title")]))

    is_duplicate = len(possible_duplicates) > 0

    if is_duplicate:
        is_duplicate = possible_duplicates[0].find("password").text == p_entry_data[p_attributes.index("password")]

    if is_duplicate:
        is_duplicate = possible_duplicates[0].find("username").text == p_entry_data[p_attributes.index("username")]

    return is_duplicate


def migrate(p_filename, p_group_element):
    """Migrate entries in the specified CSV file to KeePassX XML elements"""
    print "-> Migrating file {0}\n".format(p_filename)
    with open(p_filename, "rU") as raw_csv_file:
        # correct NULL bytes
        corrected_csv_file = csv.reader(
            (line.replace('\0', '') for line in raw_csv_file),
            delimiter="\t")

        attributes = None

        for original_entry in corrected_csv_file:
            if corrected_csv_file.line_num == 1:
                attributes = original_entry
            else:
                if has_duplicate(original_entry, attributes, p_group_element):
                    print("Skipping duplicate <{0}> on line {1}".format(
                        original_entry[0],
                        corrected_csv_file.line_num))
                    continue

                migrate_line(original_entry, attributes, p_group_element)

        print "\n-> Found {0} entries".format(corrected_csv_file.line_num)


if __name__ == "__main__":
    root_element = xml.Element("database")

    group_element = xml.SubElement(root_element, "group")

    xml.SubElement(group_element, "title").text = DEFAULT_GROUP_NAME

    migrate(INPUT_FILE, group_element)

    migratedPasswordData = open(OUTPUT_FILE, "w+")

    migratedPasswordData.write(XML_DOCTYPE + "\n")

    xml.ElementTree(root_element).write(migratedPasswordData)

    migratedPasswordData.close()

    print "\n-> Exported migrated records to {0}\n".format(OUTPUT_FILE)