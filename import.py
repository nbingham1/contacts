#!/usr/bin/python3

from contacts import *
import sys

contacts = Contact.readContacts("contacts.json")

for arg in sys.argv[1:]:
	if arg == "Connections.csv":
		contacts += Contact.readLinkedInCSV(arg)
	elif arg.endswith(".html"):
		contacts += Contact.readLinkedInHTML(arg)
	else:
		contacts += Contact.readGoogleCSV(arg)
		
deduplicate(contacts)

labels = set()
for contact in contacts:
	for label in contact.labels:
		labels.add(label)

print(list(labels))
Contact.writeContacts("contacts.json", contacts)

