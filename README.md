# mailbox-autoswipe-2-gmail-filter-converter
Migrate your mailbox autoswipe settings to gmail.

## Requirements
  * Python 3 (https://www.python.org/downloads/)
  * The lxml package

You can run `pip install -r requirements.txt` to install the lxml package. Note, you may need to use `pip3` rather than `pip` depending on how your system is configured.

## Usage
  * Export your autoswipe rules from mailbox (in Settings > Auto-swipe)
  * Download the CSV file from the email you will receive
  * Put it in the same folder as `mailbox_csv_2_gmail_xml.py`
  * Run `python3 mailbox_csv_2_gmail_xml.py`
  * Upload `filters.xml` to your gmail account (via the settings page: https://mail.google.com/mail/u/0/?hl=en#settings/filters)
  * Double-check that the filters make sense

If you find an autoswipe rule which doesn't convert properly, open an issue to let me know.

### Advanced command line usage:
`mailbox_csv_2_gmail_xml.py INPUT_FILENAME [-o OUTPUT_FILENAME]`

  * INPUT_FILENAME - The CSV file to get mailbox autoswipe rules from (default: "./autoswipe_rules.csv")
  * OUTPUT_FILENAME (-o or --output-filename) - The file to write the gmail XML filters to (default: "./filters.xml")
