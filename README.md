# Task Tracker

## Overview

This Python + Firestore terminal application allows you to keep track of tasks and by when you need to complete them.

To use this software, run the `main.py` Python script from the terminal and you will be put into the program's
command-line interface in the current terminal. You will be able to:

1. List all tasks currently in the Firestore cloud database
1. Add a task to the database
1. Complete a task (move it from the `uncompleted` collection to the `completed` collection)
1. Remove a task from the `completed` collection
1. Quit the program

My purpose for creating this software was to learn about NoSQL database structure by using it in a simple and relatively
easy-to-implement program such as this one. Google Firebase's Firestore database API uses NoSQL collection and document
structure, so it was perfect for gaining a little bit of experience with NoSQL syntax.

[Task Tracker Using Firestore - Demo](https://youtu.be/5ToeDJayhyM)

## Cloud Database

Google Firebase offers a free cloud database service called Firestore which is what I used for this project.

The structure of my NoSQL Firestore database is as follows:

- Top-level Collections:

  - Uncompleted
  - Completed

- `Task` Document Fields:

  - id: `int`
  - type: `str`
  - text: `str`
  - deadling: `str` | `null`

## Development Environment

#### Dependencies

- `Python` 3.11
- `firebase-admin` 6.2.0
- `google-cloud-firestore` 2.13.1

To use the Firestore API within Python, I used pip to install the `firebase-admin` module with this command:

```powershell
python -m pip install --upgrade "firebase-admin"
```

I then needed to create a Firestore database from the Google Cloud Firebase website and generate an API
Service Account Key to access the database from within my program.

## Useful Websites

Websites that I found helpful for this project:

- [Firestore Official Documentation](https://firebase.google.com/docs/firestore)
- [Example - Setting up a firestore project in Python](https://www.analyticsvidhya.com/blog/2022/07/introduction-to-google-firebase-firestore-using-python/)

## Future Work

- Allow for modifications to a task without deleting any documents.
- Create feature to query tasks by `type`.
- Refactor into gui or web application.
