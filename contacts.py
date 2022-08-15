#!/usr/bin/python3

import csv
import json
import re
from lxml import etree
import itertools
import unicodedata
import pyhtml.parse as parse
import os
import copy

def merge(arr1, arr2):
	for toAdd in arr2:
		found = False
		for toComp in arr1:
			if toAdd.isEqualTo(toComp):
				toComp.merge(toAdd)
				found = True
				break
		if not found:
			arr1.append(toAdd)
	return arr1

def deduplicate(arr):
	for i in reversed(range(len(arr))):
		for j in reversed(range(i)):
			if arr[i].isEqualTo(arr[j]):
				arr[j].merge(arr[i])
				del arr[i]
				break

def cleanDict(d):
	result = {}
	for key, value in d.items():
		if value:
			result[key] = value
	return result

def parseRepeated(col):
	return col.split(" ::: ")

def sanitiseList(items):
	result = []
	for item in items:
		if item.isValid():
			result += item.unwind()
	
	return result

def normalizeName(fullname):
	while "(" in fullname:
		start = fullname.index('(')
		end = fullname.index(')')
		if len(fullname) > end+1:
			fullname = fullname[0:start] + fullname[end+1:]
		else:
			fullname = fullname[0:start]

	fullname = re.sub(r'[^-\.,a-zA-Z ]+', '', fullname)
	if "," in fullname:
		start = fullname.index(',')
		fullname = fullname[0:start]

	names = [name for name in fullname.split(" ") if name]

	first = ""
	other = []
	last = ""
		
	if len(names) > 0:
		first = names[0]
	if len(names) > 2:
		other = names[1:-1]
	if len(names) > 1:
		last = names[-1]
	
	return (first, other, last)

def normalizeDate(date):
	m = re.match(r"([0-9][0-9][0-9]+)-([0-9]+)-([0-9]+)", date)
	return m.group(2) + "/" + m.group(3) + "/" + m.group(1)

class Email:
	def __init__(self):
		self.email = ""
		self.type = ""

	def isEqualTo(self, other):
		return self.email and other.email and self.email == other.email

	def isValid(self):
		if self.email:
			return True
		return False

	def merge(self, other):
		if other.email:
			self.email = other.email
		if other.type:
			self.type = other.type

	def unwind(self):
		result = []
		
		arrLen = max(len(self.email), len(self.type))
		while self.email and len(self.email) < arrLen:
			self.email.append(copy.deepcopy(self.email[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))
		
		for item in itertools.zip_longest(self.email, self.type):
			e = Email()
			e.email = item[0]
			e.type = item[1]
			result.append(e)
		return result

	def normalize(email):
		return email.lower()

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Phone:
	def __init__(self):
		self.phone = ""
		self.type = ""

	def isEqualTo(self, other):
		return self.phone and other.phone and self.phone == other.phone

	def isValid(self):
		if self.phone:
			return True
		return False

	def merge(self, other):
		if other.phone:
			self.phone = other.phone
		if other.type:
			self.type = other.type

	def unwind(self):
		result = []

		arrLen = max(len(self.phone), len(self.type))
		while self.phone and len(self.phone) < arrLen:
			self.phone.append(copy.deepcopy(self.phone[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.phone, self.type):
			p = Phone()
			p.phone = item[0]
			p.type = item[1]
			result.append(p)
		return result

	def normalize(phone):
		phone = re.sub(r'[^0-9,]+', '', phone).split(',')
		if not phone:
			return ""

		if len(phone[0]) == 7:
			phone[0] = '812' + phone[0]
		if len(phone[0]) == 10:
			phone[0] = '1' + phone[0]
		if len(phone[0]) == 11 and phone[0][0] == '1':
			phone[0] = phone[0][0] + " (" + phone[0][1:4] + ") " + phone[0][4:7] + "-" + phone[0][7:]
		elif len(phone[0]) >= 11 and phone[0][0:2] == '91':
			phone[0] = "+" + phone[0][0:2] + " " + phone[0][2:7] + " " + phone[0][7:]
		else:
			print("warning, unrecognized phone number format", phone)

		return ", ".join(phone)

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Address:
	def __init__(self):
		self.street = ""
		self.city = ""
		self.poBox = ""
		self.region = ""
		self.postalCode = ""
		self.country = ""
		self.extended = ""
		self.type = ""

	def isEqualTo(self, address):
		return self.street and address.street and self.street == address.street

	def isValid(self):
		if self.street:
			return True
		return False

	def merge(self, address):
		if address.street:
			self.street = address.street
		if address.city:
			self.city = address.city
		if address.poBox:
			self.poBox = address.poBox
		if address.region:
			self.region = address.region
		if address.postalCode:
			self.postalCode = address.postalCode
		if address.country:
			self.country = address.country
		if address.extended:
			self.extended = address.extended
		if address.type:
			self.type = address.type

	def unwind(self):
		result = []

		arrLen = max(len(self.street), len(self.city), len(self.poBox), len(self.region), len(self.postalCode), len(self.country), len(self.extended), len(self.type))
		while self.street and len(self.street) < arrLen:
			self.street.append(copy.deepcopy(self.street[-1]))
		while self.city and len(self.city) < arrLen:
			self.city.append(copy.deepcopy(self.city[-1]))
		while self.poBox and len(self.poBox) < arrLen:
			self.poBox.append(copy.deepcopy(self.poBox[-1]))
		while self.region and len(self.region) < arrLen:
			self.region.append(copy.deepcopy(self.region[-1]))
		while self.postalCode and len(self.postalCode) < arrLen:
			self.postalCode.append(copy.deepcopy(self.postalCode[-1]))
		while self.country and len(self.country) < arrLen:
			self.country.append(copy.deepcopy(self.country[-1]))
		while self.extended and len(self.extended) < arrLen:
			self.extended.append(copy.deepcopy(self.extended[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.street, self.city, self.poBox, self.region, self.postalCode, self.country, self.extended, self.type):
			a = Address()
			a.street = item[0]
			a.city = item[1]
			a.poBox = item[2]
			a.region = item[3]
			a.postalCode = item[4]
			a.country = item[5]
			a.extended = item[6]
			a.type = item[7]
			result.append(a)
		return result

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Relation:
	def __init__(self):
		self.value = ""
		self.type = ""

	def isEqualTo(self, relation):
		return self.value and relation.value and self.value == relation.value

	def isValid(self):
		if self.value:
			return True
		return False

	def merge(self, relation):
		if relation.value:
			self.value = relation.value
		if relation.type:
			self.type = relation.type

	def unwind(self):
		result = []

		arrLen = max(len(self.value), len(self.type))
		while self.value and len(self.value) < arrLen:
			self.value.append(copy.deepcopy(self.value[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.value, self.type):
			r = Relation()
			r.value = item[0]
			r.type = item[1]
			result.append(r)
		return result

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Website:
	def __init__(self):
		self.value = ""
		self.type = ""

	def isEqualTo(self, website):
		return self.value and website.value and self.value == website.value

	def isValid(self):
		if self.value:
			return True
		return False

	def merge(self, website):
		if website.value:
			self.value = website.value
		if website.type:
			self.type = website.type

	def unwind(self):
		result = []

		arrLen = max(len(self.value), len(self.type))
		while self.value and len(self.value) < arrLen:
			self.value.append(copy.deepcopy(self.value[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.value, self.type):
			w = Website()
			w.value = item[0]
			w.type = item[1]
			result.append(w)
		return result

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Organization:
	def __init__(self):
		self.name = ""
		self.title = ""
		self.department = ""
		self.symbol = ""
		self.location = ""
		self.description = ""
		self.type = ""

	def isEqualTo(self, org):
		return self.name and org.name and self.name == org.name and (not self.title or not org.title or self.title == org.title)

	def isValid(self):
		if self.name:
			return True
		return False

	def merge(self, org):
		if org.name:
			self.name = org.name
		if org.title:
			self.title = org.title
		if org.department:
			self.department = org.department
		if org.symbol:
			self.symbol = org.symbol
		if org.location:
			self.location = org.location
		if org.description:
			self.description = org.description
		if org.type:
			self.type = org.type

	def unwind(self):
		result = []

		arrLen = max(len(self.name), len(self.title), len(self.department), len(self.symbol), len(self.location), len(self.description), len(self.type))
		while self.name and len(self.name) < arrLen:
			self.name.append(copy.deepcopy(self.name[-1]))
		while self.title and len(self.title) < arrLen:
			self.title.append(copy.deepcopy(self.title[-1]))
		while self.department and len(self.department) < arrLen:
			self.department.append(copy.deepcopy(self.department[-1]))
		while self.symbol and len(self.symbol) < arrLen:
			self.symbol.append(copy.deepcopy(self.symbol[-1]))
		while self.location and len(self.location) < arrLen:
			self.location.append(copy.deepcopy(self.location[-1]))
		while self.description and len(self.description) < arrLen:
			self.description.append(copy.deepcopy(self.description[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.name, self.title, self.department, self.symbol, self.location, self.description, self.type):
			o = Organization()
			o.name = item[0]
			o.title = item[1]
			o.department = item[2]
			o.symbol = item[3]
			o.location = item[4]
			o.description = item[5]
			o.type = item[6]
			result.append(o)
		return result

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Event:
	def __init__(self):
		self.value = ""
		self.type = ""

	def isEqualTo(self, event):
		return self.value and event.value and self.value == event.value

	def isValid(self):
		if self.value:
			return True
		return False

	def merge(self, event):
		if event.value:
			self.value = event.value
		if event.type:
			self.type = event.type

	def unwind(self):
		result = []

		arrLen = max(len(self.value), len(self.type))
		while self.value and len(self.value) < arrLen:
			self.value.append(copy.deepcopy(self.value[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.value, self.type):
			e = Event()
			e.value = item[0]
			e.type = item[1]
			result.append(e)
		return result

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Field:
	def __init__(self, ftype="", value=""):
		self.value = value
		self.type = ftype

	def isEqualTo(self, field):
		return self.value and field.value and self.value == field.value

	def isValid(self):
		if self.value:
			return True
		return False

	def merge(self, field):
		if field.value:
			self.value = field.value
		if field.type:
			self.type = field.type

	def unwind(self):
		result = []

		arrLen = max(len(self.value), len(self.type))
		while self.value and len(self.value) < arrLen:
			self.value.append(copy.deepcopy(self.value[-1]))
		while self.type and len(self.type) < arrLen:
			self.type.append(copy.deepcopy(self.type[-1]))

		for item in itertools.zip_longest(self.value, self.type):
			result.append(Field(item[1], item[0]))
		return result

	def fromJson(self, obj):
		for key, value in obj.items():
			self.__dict__[key] = value

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Contact:
	def __init__(self):
		self.first = ""
		self.last = ""
		self.names = []
		self.prefix = ""
		self.suffix = ""
		self.preferred = ""
		self.birthday = ""
		self.gender = ""
		self.photo = ""
		self.labels = []
		self.emails = [] # Email
		self.phones = [] # Phone
		self.addresses = [] # Address
		self.orgs = [] # Organization
		self.relations = [] # Relation
		self.sites = [] # Website
		self.events = [] # Event

		self.interests = []
		self.hobbies = []
		self.preferences = []

		self.goals = []
		self.deliverables = []
		self.log = []

		self.notes = ""

		# NEVER UPLOAD TO GOOGLE
		self.strengths = []
		self.weaknesses = []
		self.aspirations = []
		self.personality = []

	def isEqualTo(self, contact):
		if self.first == contact.first and self.last == contact.last and self.first and self.last:
			return True

		for myEmail in self.emails:
			for theirEmail in contact.emails:
				if myEmail.isEqualTo(theirEmail):
					return True

		for myPhone in self.phones:
			for theirPhone in contact.phones:
				if myPhone.isEqualTo(theirPhone):
					return True

		return False

	def merge(self, contact):
		if contact.first:
			self.first = contact.first
		if contact.last:
			self.last = contact.last
		if len(contact.names) > 0:
			self.names = contact.names
		if contact.prefix:
			self.prefix = contact.prefix
		if contact.suffix:
			self.suffix = contact.suffix
		if contact.preferred:
			self.preferred = contact.preferred
		if contact.birthday:
			self.birthday = contact.birthday
		if contact.gender:
			self.gender = contact.gender
		if contact.photo:
			self.photo = contact.photo
		if contact.notes:
			self.notes += "\n" + contact.notes
		for label in contact.labels:
			if label not in self.labels:
				self.labels.append(label)
		merge(self.emails, contact.emails)
		merge(self.phones, contact.phones)
		merge(self.addresses, contact.addresses)
		merge(self.orgs, contact.orgs)
		merge(self.relations, contact.relations)
		merge(self.sites, contact.sites)
		merge(self.events, contact.events)
		
	def sanitise(self):
		self.emails = sanitiseList(self.emails)
		self.phones = sanitiseList(self.phones)
		self.addresses = sanitiseList(self.addresses)
		self.orgs = sanitiseList(self.orgs)
		self.relations = sanitiseList(self.relations)
		self.sites = sanitiseList(self.sites)
		self.sites = [site for site in self.sites if "plus.google.com" not in site.value and "google.com/profiles" not in site.value]
		self.events = sanitiseList(self.events)

	def fromJson(self, obj):
		for key, values in obj.items():
			if key == "emails":
				for value in values:
					email = Email()
					email.fromJson(value)
					self.emails.append(email)
			elif key == "phones":
				for value in values:
					phone = Phone()
					phone.fromJson(value)
					self.phones.append(phone)
			elif key == "addresses":
				for value in values:
					address = Address()
					address.fromJson(value)
					self.addresses.append(address)
			elif key == "orgs":
				for value in values:
					org = Organization()
					org.fromJson(value)
					self.orgs.append(org)
			elif key == "relations":
				for value in values:
					relation = Relation()
					relation.fromJson(value)
					self.relations.append(relation)
			elif key == "sites":
				for value in values:
					site = Website()
					site.fromJson(value)
					self.sites.append(site)
			elif key == "events":
				for value in values:
					event = Event()
					event.fromJson(value)
					self.events.append(event)
			else:
				self.__dict__[key] = values

	def readContacts(filename):
		result = []
		if os.path.isfile(filename):
			with open(filename, newline='') as fptr:
				fields = json.loads(fptr.read())
				for obj in fields:
					contact = Contact()
					contact.fromJson(obj)
					result.append(contact)
		return result

	def writeContacts(filename, contacts):
		with open(filename, 'w') as fptr:
			fptr.write("[" + ",\n".join(contact.toJson() for contact in contacts) + "]") 

	def readLinkedInHTML(filename):
		result = []

		if os.path.isfile(filename):
			parser = etree.HTMLParser(target = parse.Parser())
			with open(filename, 'r') as fptr:
				data = fptr.read()
				parser.feed(data)
			p = parser.close()
			tags = p.syntax.get(Class="mn-connection-card__details")
			for tag in tags:
				contact = Contact()
				link = tag.get(Class="mn-connection-card__link")
				name = tag.get(Class="mn-connection-card__name")
				
				if len(link) > 0:
					site = Website()
					site.value = "https://www.linkedin.com" + link[0].attrs["href"]
					site.type = "Profile"
					contact.sites.append(site)
				if len(name) > 0:
					contact.first, contact.names, contact.last = normalizeName((" ".join([" ".join(item.content) for item in name]).strip()))
				result.append(contact)

		return result

	def readLinkedInCSV(filename):
		result = []

		if os.path.isfile(filename):
			hdr = []
			with open(filename, newline='') as fptr:
				reader = csv.reader(fptr, delimiter=',', quotechar='"')
				for i, row in enumerate(reader):
					if i == 0:
						hdr = row
					if i > 0:
						contact = Contact()
						for j, col in enumerate(hdr):
							if row[j]:
								if col == "First Name":
									contact.first = row[j]
								elif col == "Last Name":
									contact.last = row[j]
								elif col == "Email Address":
									email = Email()
									email.email = Email.normalize(row[j])
									email.type = "Work"
									contact.emails.append(email)
								elif col == "Company":
									org = Organization()
									org.name = row[j]
									if contact.orgs:
										contact.orgs[0].merge(org)
									else:
										contact.orgs.append(org)
								elif col == "Position":
									org = Organization()
									org.title = row[j]
									if contact.orgs:
										contact.orgs[0].merge(org)
									else:
										contact.orgs.append(org)

						contact.first, contact.names, contact.last = normalizeName(contact.first + " " + contact.last)
						
						result.append(contact)
		return result

	def readGoogleCSV(filename):
		result = []
		if os.path.isfile(filename):
			hdr = []
			with open(filename, newline='') as fptr:
				reader = csv.reader(fptr, delimiter=',', quotechar='"')
				for i, row in enumerate(reader):
					if i == 0:
						hdr = row
					if i > 0:
						contact = Contact()
						ims = []
						custom = []
						for j, col in enumerate(hdr):
							if row[j]:
								if col == "Name":
									pass
								elif col == "Given Name":	
									contact.first = row[j]
								elif col == "Additional Name":
									contact.names = row[j].split(' ')
								elif col == "Family Name":
									contact.last = row[j]
								elif col == "Nickname":
									contact.preferred = row[j]
								elif col == "Name Prefix":
									contact.prefix = row[j]
								elif col == "Name Suffix":
									contact.suffix = row[j]
								elif col == "Birthday":
									contact.birthday = normalizeDate(row[j])
								elif col == "Gender":
									contact.gender = row[j]
								elif col == "Photo":
									contact.photo = row[j]
								elif col == "Notes":
									contact.notes = row[j]
								elif col == "Group Membership":
									contact.labels += parseRepeated(row[j])
								elif m := re.match(r"E-mail ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.emails) <= index:
										contact.emails.append(Email())
									if fieldName == "Type":
										contact.emails[index].type = field
									elif fieldName == "Value":
										contact.emails[index].email = [Email.normalize(item) for item in field]
								elif m := re.match(r"IM ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(ims) <= index:
										ims.append(Email())
									if fieldName == "Type":
										ims[index].type = field
									elif fieldName == "Value":
										ims[index].email = [Email.normalize(item) for item in field]
								elif m := re.match(r"Phone ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.phones) <= index:
										contact.phones.append(Phone())
									if fieldName == "Type":
										contact.phones[index].type = field
									elif fieldName == "Value":
										contact.phones[index].phone = [Phone.normalize(item) for item in field]
								elif m := re.match(r"Address ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.addresses) <= index:
										contact.addresses.append(Address())
									if fieldName == "Type":
										contact.addresses[index].type = field
									elif fieldName == "Street":
										contact.addresses[index].street = field
									elif fieldName == "City":
										contact.addresses[index].city = field
									elif fieldName == "PO Box":
										contact.addresses[index].poBox = field
									elif fieldName == "Region":
										contact.addresses[index].region = field
									elif fieldName == "Postal Code":
										contact.addresses[index].postalCode = field
									elif fieldName == "Country":
										contact.addresses[index].country = field
									elif fieldName == "Extended Address":
										contact.addresses[index].extended = field
								elif m := re.match(r"Organization ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.orgs) <= index:
										contact.orgs.append(Organization())
									if fieldName == "Type":
										contact.orgs[index].type = field
									elif fieldName == "Name":
										contact.orgs[index].name = field
									elif fieldName == "Title":
										contact.orgs[index].title = field
									elif fieldName == "Department":
										contact.orgs[index].department = field
									elif fieldName == "Symbol":
										contact.orgs[index].symbol = field
									elif fieldName == "Location":
										contact.orgs[index].location = field
									elif fieldName == "Job Description":
										contact.orgs[index].description = field
								elif m := re.match(r"Relation ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.relations) <= index:
										contact.relations.append(Relation())
									if fieldName == "Type":
										contact.relations[index].type = field
									elif fieldName == "Value":
										contact.relations[index].value = field
								elif m := re.match(r"Website ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.sites) <= index:
										contact.sites.append(Website())
									if fieldName == "Type":
										contact.sites[index].type = field
									elif fieldName == "Value":
										contact.sites[index].value = field
								elif m := re.match(r"Custom Field ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(custom) <= index:
										custom.append(Field())
									if fieldName == "Type":
										custom[index].type = field
									elif fieldName == "Value":
										custom[index].value = field
								elif m := re.match(r"Event ([0-9]+) - ([a-zA-Z ]+)", col):
									index = int(m.group(1)) - 1
									fieldName = m.group(2)
									field = parseRepeated(row[j])
									
									while len(contact.events) <= index:
										contact.events.append(Event())
									if fieldName == "Type":
										contact.events[index].type = field
									elif fieldName == "Value":
										contact.events[index].value = [normalizeDate(value) for value in field]

						ims = sanitiseList(ims)
						ims = [im for im in ims if "public.talk.google.com" not in im.email]
						custom = sanitiseList(custom)
						contact.sanitise()
						merge(contact.emails, ims)
						for field in custom:
							if field.type == "Interest":
								contact.interests.append(field.value)
							elif field.type == "Hobby":
								contact.hobbies.append(field.value)
							elif field.type == "Preference":
								contact.preferences.append(field.value)
							elif field.type == "Goal":
								contact.goals.append(field.value)
							elif field.type == "Deliverable":
								contact.deliverables.append(field.value)
							elif field.type == "Log":
								contact.log.append(field.value)

						result.append(contact)
		return result

	def writeGoogleCSV(filename, contacts, labels=[]):
		hdr = ["Name","Given Name","Additional Name","Family Name","Yomi Name","Given Name Yomi","Additional Name Yomi","Family Name Yomi","Name Prefix","Name Suffix","Initials","Nickname","Short Name","Maiden Name","Birthday","Gender","Location","Billing Information","Directory Server","Mileage","Occupation","Hobby","Sensitivity","Priority","Subject","Notes","Language","Group Membership"]

		emailCount = max([len(contact.emails) for contact in contacts])
		phoneCount = max([len(contact.phones) for contact in contacts])
		addressCount = max([len(contact.addresses) for contact in contacts])
		orgCount = max([len(contact.orgs) for contact in contacts])
		relationCount = max([len(contact.relations) for contact in contacts])
		siteCount = max([len(contact.sites) for contact in contacts])
		eventCount = max([len(contact.events) for contact in contacts])
		customCount = max([len(contact.interests)+len(contact.hobbies)+len(contact.preferences)+len(contact.goals)+len(contact.deliverables)+len(contact.log) for contact in contacts])

		for i in range(emailCount):
			hdr += ["E-mail " + str(i+1) + " - Type","E-mail " + str(i+1) + " - Value"]
		for i in range(phoneCount):
			hdr += ["Phone " + str(i+1) + " - Type","Phone " + str(i+1) + " - Value"]
		for i in range(addressCount):
			hdr += ["Address " + str(i+1) + " - Type","Address " + str(i+1) + " - Street","Address " + str(i+1) + " - City","Address " + str(i+1) + " - PO Box","Address " + str(i+1) + " - Region","Address " + str(i+1) + " - Postal Code","Address " + str(i+1) + " - Country","Address " + str(i+1) + " - Extended Address","Organization " + str(i+1) + " - Type"]
		for i in range(orgCount):
			hdr += ["Organization " + str(i+1) + " - Name","Organization " + str(i+1) + " - Title","Organization " + str(i+1) + " - Department","Organization " + str(i+1) + " - Symbol","Organization " + str(i+1) + " - Location","Organization " + str(i+1) + " - Job Description"]
		for i in range(relationCount):
			hdr += ["Relation " + str(i+1) + " - Type","Relation " + str(i+1) + " - Value"]
		for i in range(siteCount):
			hdr += ["Website " + str(i+1) + " - Type","Website " + str(i+1) + " - Value"]
		for i in range(eventCount):
			hdr += ["Event " + str(i+1) + " - Type","Event " + str(i+1) + " - Value"]
		for i in range(customCount):
			hdr += ["Custom Field " + str(i+1) + " - Type","Custom Field " + str(i+1) + " - Value"]

		with open(filename, "w") as fptr:
			writer = csv.writer(fptr, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(hdr)
			
			for contact in contacts:
				if not labels or len(set(labels).intersection(contact.labels)) > 0:
					custom = []
					custom += [Field("Interest", value) for value in contact.interests]
					custom += [Field("Hobby", value) for value in contact.hobbies]
					custom += [Field("Preference", value) for value in contact.preferences]
					custom += [Field("Goal", value) for value in contact.goals]
					custom += [Field("Deliverable", value) for value in contact.deliverables]
					custom += [Field("Log", value) for value in contact.log]

					row = []
					for col in hdr:
						if col == "Name":
							names = []
							if contact.first:
								names.append(contact.first)
							names += contact.names
							if contact.last:
								names.append(contact.last)
							row.append(" ".join(names))
						elif col == "Given Name":
							row.append(contact.first)	
						elif col == "Additional Name":
							row.append(" ".join(contact.names))
						elif col == "Family Name":
							row.append(contact.last)
						elif col == "Nickname":
							row.append(contact.preferred)
						elif col == "Name Prefix":
							row.append(contact.prefix)	
						elif col == "Name Suffix":
							row.append(contact.suffix)
						elif col == "Birthday":
							row.append(contact.birthday)
						elif col == "Gender":
							row.append(contact.gender)
						elif col == "Notes":
							row.append(contact.notes)
						elif col == "Group Membership":
							row.append(" ::: ".join(contact.labels))
						elif m := re.match(r"E-mail ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.emails) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.emails[index].type)
							elif fieldName == "Value":
								row.append(contact.emails[index].email)
							else:
								row.append("")
						elif m := re.match(r"Phone ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.phones) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.phones[index].type)
							elif fieldName == "Value":
								row.append(contact.phones[index].phone)
							else:
								row.append("")
						elif m := re.match(r"Address ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.addresses) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.addresses[index].type)
							elif fieldName == "Street":
								row.append(contact.addresses[index].street)
							elif fieldName == "City":
								row.append(contact.addresses[index].city)
							elif fieldName == "PO Box":
								row.append(contact.addresses[index].poBox)
							elif fieldName == "Region":
								row.append(contact.addresses[index].region)
							elif fieldName == "Postal Code":
								row.append(contact.addresses[index].postalCode)
							elif fieldName == "Country":
								row.append(contact.addresses[index].country)
							elif fieldName == "Extended Address":
								row.append(contact.addresses[index].extended)
							else:
								row.append("")
						elif m := re.match(r"Organization ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.orgs) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.orgs[index].type)
							elif fieldName == "Name":
								row.append(contact.orgs[index].name)
							elif fieldName == "Title":
								row.append(contact.orgs[index].title)
							elif fieldName == "Department":
								row.append(contact.orgs[index].department)
							elif fieldName == "Symbol":
								row.append(contact.orgs[index].symbol)
							elif fieldName == "Location":
								row.append(contact.orgs[index].location)
							elif fieldName == "Job Description":
								row.append(contact.orgs[index].description)
							else:
								row.append("")
						elif m := re.match(r"Relation ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.relations) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.relations[index].type)
							elif fieldName == "Value":
								row.append(contact.relations[index].value)
							else:
								row.append("")
						elif m := re.match(r"Website ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.sites) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.sites[index].type)
							elif fieldName == "Value":
								row.append(contact.sites[index].value)
							else:
								row.append("")
						elif m := re.match(r"Event ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(contact.events) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(contact.events[index].type)
							elif fieldName == "Value":
								row.append(contact.events[index].value)
							else:
								row.append("")
						elif m := re.match(r"Custom Field ([0-9]+) - ([a-zA-Z ]+)", col):
							index = int(m.group(1)) - 1
							fieldName = m.group(2)
							if len(custom) <= index:
								row.append("")
							elif fieldName == "Type":
								row.append(custom[index].type)
							elif fieldName == "Value":
								row.append(custom[index].value)
							else:
								row.append("")
						else:
							row.append("")
					writer.writerow(row)	

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

