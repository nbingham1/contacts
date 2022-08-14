#!/usr/bin/python3

import csv
import json
import re
import itertools

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

class Email:
	def __init__(self):
		self.email = ""
		self.type = ""

	def isEqualTo(self, email):
		return self.email == email.email

	def isValid(self):
		if self.email:
			return True
		return False

	def merge(self, email):
		if email.email:
			self.email = email.email
		if email.type:
			self.type = email.type

	def unwind(self):
		result = []
		for item in itertools.zip_longest(self.email, self.type):
			e = Email()
			e.email = item[0]
			e.type = item[1]
			result.append(e)
		return result

	def normalize(email):
		return email.lower()

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Phone:
	def __init__(self):
		self.phone = ""
		self.type = ""

	def isEqualTo(self, phone):
		return self.phone == phone.phone

	def isValid(self):
		if self.phone:
			return True
		return False

	def merge(self, phone):
		if phone.phone:
			self.phone = phone.phone
		if phone.type:
			self.type = phone.type

	def unwind(self):
		result = []
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
			phone[0] = phone[0][0] + " " + phone[0][1:4] + " " + phone[0][4:7] + " " + phone[0][7:]
		elif len(phone[0]) >= 11 and phone[0][0:2] == '91':
			phone[0] = "+" + phone[0][0:2] + " " + phone[0][2:7] + " " + phone[0][7:]
		else:
			print("warning, unrecognized phone number format", phone)

		return ", ".join(phone)

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
		return self.street == address.street

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

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Relation:
	def __init__(self):
		self.value = ""
		self.type = ""

	def isEqualTo(self, relation):
		return self.value == relation.value

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
		for item in itertools.zip_longest(self.value, self.type):
			r = Relation()
			r.value = item[0]
			r.type = item[1]
			result.append(r)
		return result

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Website:
	def __init__(self):
		self.value = ""
		self.type = ""

	def isEqualTo(self, website):
		return self.value == website.value

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
		for item in itertools.zip_longest(self.value, self.type):
			w = Website()
			w.value = item[0]
			w.type = item[1]
			result.append(w)
		return result

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
		return self.name == org.name and (self.title == "" or self.title == org.title)

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

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

class Contact:
	def __init__(self):
		self.first = ""
		self.last = ""
		self.names = []
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

		self.interests = []
		self.hobbies = []
		self.preferences = []

		self.goals = []
		self.deliverables = []
		self.log = []

		# NEVER UPLOAD TO GOOGLE
		self.strengths = []
		self.weaknesses = []
		self.aspirations = []
		self.personality = []

	def isEqualTo(self, contact):
		if (self.first == contact.first or not self.first or not contact.first) and (self.last == contact.last or not self.last or not contact.last) and (self.first or self.last) and (contact.first or contact.last):
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
		if contact.preferred:
			self.preferred = contact.preferred
		if contact.birthday:
			self.birthday = contact.birthday
		if contact.gender:
			self.gender = contact.gender
		if contact.photo:
			self.photo = contact.photo
		for label in contact.labels:
			if label not in self.labels:
				self.labels.append(label)
		merge(self.emails, contact.emails)
		merge(self.phones, contact.phones)
		merge(self.addresses, contact.addresses)
		merge(self.orgs, contact.orgs)
		merge(self.relations, contact.relations)
		merge(self.sites, contact.sites)
		
	def sanitise(self):
		self.emails = sanitiseList(self.emails)
		self.phones = sanitiseList(self.phones)
		self.addresses = sanitiseList(self.addresses)
		self.orgs = sanitiseList(self.orgs)
		self.relations = sanitiseList(self.relations)
		self.sites = sanitiseList(self.sites)
		self.sites = [site for site in self.sites if "plus.google.com" not in site.value and "google.com/profiles" not in site.value]

	def readContacts(filename):
		result = []
		with open('contacts.json', newline='') as fptr:
			fields = json.loads(fptr.read())
			for contactJSON in fields:
				contact = Contact()
				contact.__dict__ = contactJSON
				result.append(contact)
		return result

	def writeContacts(filename, contacts):
		with open('contacts.json', 'w') as fptr:
			fptr.write("[" + ",\n".join(contact.toJson() for contact in contacts) + "]") 

	def readLinkedInCSV(filename):
		result = []

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
								email.value = Email.normalize(row[j])
								email.type = "work"
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

					names = contact.first.split(" ") + contact.last.split(" ")
					names = [name for name in names if name and not (name[0] == "(" and name[-1] == ")")]
				
					if len(names) > 0:	
						contact.first = names[0]
					if len(names) > 2:
						contact.names = names[1:-1]
					if len(names) > 1:
						contact.last = names[-1]
					
					result.append(contact)
		return result

	def readGoogleCSV(filename):
		result = []
		hdr = []
		with open(filename, newline='') as fptr:
			reader = csv.reader(fptr, delimiter=',', quotechar='"')
			for i, row in enumerate(reader):
				if i == 0:
					hdr = row
				if i > 0:
					contact = Contact()
					ims = []
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
							elif col == "Birthday":
								contact.birthday = row[j]
							elif col == "Gender":
								contact.gender = row[j]
							elif col == "Photo":
								contact.photo = row[j]
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
					
					ims = sanitiseList(ims)
					ims = [im for im in ims if "public.talk.google.com" not in im.email]
					contact.sanitise()
					merge(contact.emails, ims)
					result.append(contact)
		return result

	def writeGoogleCSV(filename, contacts):
		hdr = ["Name","Given Name","Additional Name","Family Name","Yomi Name","Given Name Yomi","Additional Name Yomi","Family Name Yomi","Name Prefix","Name Suffix","Initials","Nickname","Short Name","Maiden Name","Birthday","Gender","Location","Billing Information","Directory Server","Mileage","Occupation","Hobby","Sensitivity","Priority","Subject","Notes","Language","Photo","Group Membership","E-mail 1 - Type","E-mail 1 - Value","E-mail 2 - Type","E-mail 2 - Value","E-mail 3 - Type","E-mail 3 - Value","IM 1 - Type","IM 1 - Service","IM 1 - Value","Phone 1 - Type","Phone 1 - Value","Phone 2 - Type","Phone 2 - Value","Phone 3 - Type","Phone 3 - Value","Address 1 - Type","Address 1 - Formatted","Address 1 - Street","Address 1 - City","Address 1 - PO Box","Address 1 - Region","Address 1 - Postal Code","Address 1 - Country","Address 1 - Extended Address","Organization 1 - Type","Organization 1 - Name","Organization 1 - Yomi Name","Organization 1 - Title","Organization 1 - Department","Organization 1 - Symbol","Organization 1 - Location","Organization 1 - Job Description","Relation 1 - Type","Relation 1 - Value","Relation 2 - Type","Relation 2 - Value","Relation 3 - Type","Relation 3 - Value","Relation 4 - Type","Relation 4 - Value","Website 1 - Type","Website 1 - Value","Website 2 - Type","Website 2 - Value","Website 3 - Type","Website 3 - Value"]
		with open(filename, "w") as fptr:
			writer = csv.writer(fptr, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(hdr)
			
			for contact in contacts:
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
					elif col == "Birthday":
						row.append(contact.birthday)
					elif col == "Gender":
						row.append(contact.gender)
					elif col == "Photo":
						row.append(contact.photo)
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
					else:
						row.append("")
				writer.writerow(row)	

	def toJson(self):
		return json.dumps(self, default=lambda o: cleanDict(o.__dict__), indent=2)

contacts = []

merge(contacts, Contact.readGoogleCSV("contacts.csv"))
merge(contacts, Contact.readLinkedInCSV("Connections.csv"))

Contact.writeContacts("contacts.json", contacts)

Contact.writeGoogleCSV("contacts_updated.csv", contacts)
