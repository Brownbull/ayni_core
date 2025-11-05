on archiecture.md:
- Database Schema (Core Tables): Not sure if these tables will cover all the data we want to store, an example of all datasets created i at "data\context_states\test_client_20251022_150907\datasets" and there are many aggegation levels.
- Data Flow: once a user is logged, and selected a company, then he will e allowed to upload a file for that company. That file can have any number of columns, under different names, some might be required and some might be optional. This was defined in "src\core\constants.py" under COLUMN_SCHEMA. User must be allowed to specify column mapping names, format and default format.
- Data Flow: after 6. Results committed to PostgreSQL we will know how man rows were finally saved in the database, this is important, a user might be updating data for a given month and we need to be able to provide information about how much information was actually updated. we can overwrite everything on upload, but if data is already there for a time period we need to be able to inform how many rows were before and after the changes.

Consider for frontend
- Presentation Layer (Frontend): I copied tailwind resources to use on tailwind_templates folder. These come from premium subscription to tailwind, use them wisely.

Consider for any port being used, endpoint or url.
- file "C:\Projects\play\ayni_core\ai-state\knowledge\endpoints.txt" was created to be updated EVERY time a port/url/endpoint is in use, in any environment during development THIS IS MANDATORY, WE NEED TO KNOW WHERE ARE WE WORKING.

Admin
- create admin users with credentials user: admin@ayni.cl password gabe123123