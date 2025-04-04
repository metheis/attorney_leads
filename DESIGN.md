## Design Document

This document contains some high level design decisions about this solution.

### Database

This implementation uses an SQLite database to store users and attorneys. This is one of the simplest SQL databases, and negates the requirements of setting up a separate DB server such as would be needed for Postgres, MariaDB, etc.


### SQLModel & The API

SQLModel is a fast and simple object relational mapper that enables interfacing from the python classes (models in this repo) that correspond to tables & data in the database. It is written by the same maintainer of FastAPI, so the two go well hand in hand.

The implementation / integration of SQLModel to the API abstracts models as basic data classes, which are then consumed by a database interaction wrapper to read and write to the database. The API (main.py) calls into the database with the python objects it creates based on the API calls.

### Security

This implementation uses a very simple security authentication implementation that relies on FastAPI's OAuth2PasswordBearer and OAuth2PasswordBearer. It uses a basic token authentication mechanism that once an attorney logs in, he or she may interact with the API calls that require attorney authentication. These tokens are just the attorneys' usernames. It has a password "hash" that serves as a template for how passwords would be more securely stored in the database.

The current state is unacceptable for a real system / API. You would need to incorporate an actual password hashing + salt scheme when storing the passwords in the database. Moreover, you would want to pass real tokens to authenticate users.


Also, the admin attorney is defined in the main code. This should be changed to a more secure solution.

### Email

Email sending requires access to an SMTP server for sending. This is currently disabled in the implementation, but all dependencies and relevant support code to send an email is present in `simple_mail.py`.

### Other thoughts.

Current assumptions about desired behavior are as follows:

* Users are identified by their email address. While they may update their full name and resume, they cannot change their email once submitted.
* Currently, the email sending upon user submission only sends to the administrative attorney.

These considerations can be changed based on desired functionality for users and attorneys.

One more piece to add, implementation wise, there are methods to clean up the actual code implementation. The largest is that currently, all functions are global in their respective files, and the main file and directly imports each dependency / data type it needs. In a full fleshed implementation, I would prefer to stick these into respective classes, which simplifies the global namespace.

