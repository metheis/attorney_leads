# Attorney Leads Form API

This repo contains a simple backend application that manages leads for an attorney. Candidates submit a publicly available form containing their first and last name, email address, and attached resume / CV. The application emails both the candidate and attorney. An internal auth guarded interface allows the attorney to see all candidates and fields, and manage their status (from default pending state to reached out).

## Running the application.

First, from inside this folder, create a python virtual environment:
```
python -m venv venv
```

Activate the environment (macos / linux)
```
source env/bin/activate
```
(Windows)
```
.\env\Scripts\Activate.ps1
```

Install python required dependencies:
```
pip install -r requirements.txt
```

Enter the app directory
```
cd app
```

Run Uvicorn
```
uvicorn main:app
```

Navigate to the api docs in your browser at:
```
http://127.0.0.1:8000/docs
```

After starting up, you will notice that the application will create a database to store data offline if not already present on the file system.

From there, you can see each of the APIs to interact with the backend.
* `/candidate/`: Create candidate.
* `POST /candidate/{email}`: Read candidate.
* `GET /candidate/{email}`: Read candidate.
* `PATCH /candidate/{email}`: Update candidate.
* `POST /uploadfile`: Create upload file.
* `POST /attorney/create`: Create an attorney. Must be logged in as another attorney.
* `POST /token`: Login authentication.
* `GET /attorney/leads`: Get all candidates.
* `PATCH /attorney/candidate/{email}`: Update candidate's status as an attorney.

There is a default admin user / attorney that is populated when creating the database.
```
user: admin
pass: secret
```

