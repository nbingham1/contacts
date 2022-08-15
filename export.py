#!/usr/bin/python3

from contacts import *
import sys

if len(sys.argv) < 2:
	print("expected output file")
	print("usage: export.py <outfile> [label...]")
	exit

contacts = Contact.readContacts("contacts.json")

Contact.writeGoogleCSV(sys.argv[1], contacts, sys.argv[2:])
