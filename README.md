# Contacts

Goal: Scripts that allow for importing contact information from LinkedIN and Google Contacts and then exporting them to google contacts, tools for keeping notes and keeping track of whether a contact will remember me. Need to trim contacts that wouldn't remember me. They are no longer functional.

### Requirements
 - Keep track of hundreds of contacts
 - Facilitate development of those relationships
 - Stay top of mind

### Constraints
 - Limited memory
 - Limited access to notes when talking to someone
 - poor interfaces in contact management tools

### Design
 - Use Google Contacts as front-end UI
   - Simple
   - Already on phone
   - no permissions required
   - searchable
   - labels for networks
 - Use LinkedIN to get most up-to-date employment information occational run script to bring this information in
 - Use LinkedIN to grab contact information for contacts I haven't added to Google Contacts
 - Keep track of other knowledge in notes

### Need to know
 - Will this contact remember me?
 - What are my goals for this contact?
 - When did I last contact this person?
 - What did we talk about then?
 - What do I know about this person?
   - Strengths, weaknesses, interests, aspirations, things they like, how they think

### TODO
 - parse LinkedIn CSV or integrate with LinkedIN API
 - parse Google Contacts CSV or integrate with Google API
   - will need to integrate with API to upload updated information

