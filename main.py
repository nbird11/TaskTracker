import firebase_admin
from firebase_admin import firestore

# For type annotations:
from google.cloud.firestore import (
    Client,
    DocumentReference,
    DocumentSnapshot,
    FieldFilter,
)
from typing import Generator
from datetime import date

# Globals
CRED = firebase_admin.credentials.Certificate(
    "./ServiceAccountKey/todobase-ffbf6-firebase-adminsdk-sbidt-bbd1907f8b.json"
)
APP: firebase_admin.App = firebase_admin.initialize_app(CRED)
DB: Client = firestore.client(APP)

# <Database Structure>
# Collections
UNCOMPLETED = "uncompleted"
COMPLETED = "completed"

# Document fields
ID = "id"
TYPE = "type"
TEXT = "text"
DEADLINE = "deadline"
# </>

UNCOMP_ID = 0
COMP_ID = 0


def menu() -> int:
    """Display menu and return user command.

    Returns:
        `int` - The user's command choice.
    """

    print("Menu:")
    print("  1. List all tasks")
    print("  2. Add task")
    print("  3. Complete task")
    print("  4. Remove completed task")
    print("  0. Quit")
    return int(input("> "))


def update_ids() -> None:
    """
    Refresh the ids of all the documents in each collection. Used after
    deleting a task to make sure every task has a unique, sequential id.
    """

    global UNCOMP_ID
    global COMP_ID

    UNCOMP_ID = 0
    docs: Generator[DocumentReference] = DB.collection(UNCOMPLETED).list_documents()
    for doc_ref in docs:
        doc_ref.set({ID: UNCOMP_ID}, merge=True)
        UNCOMP_ID += 1

    COMP_ID = 0
    docs: Generator[DocumentReference] = DB.collection(COMPLETED).list_documents()
    for doc_ref in docs:
        doc_ref.set({ID: COMP_ID}, merge=True)
        COMP_ID += 1


def list_tasks(coll: str) -> None:
    """
    Print all the tasks from a collection.

    Params:
        `coll: str` - the name of the collection in the `tasks` firestore database.
    """

    print(f"\n{coll.capitalize()} Tasks:")
    docs: Generator[DocumentSnapshot] = DB.collection(coll).order_by("id").stream()
    print(f"| {'ID':<5} | {'Type':<15} | {'Text':<50} | {'Deadline':<25} |")
    print(f"+-{'':-<5}-+-{'':-<15}-+-{'':-<50}-+-{'':-<25}-+")
    for doc_snap in docs:
        doc_dict = doc_snap.to_dict()
        print(f"| {f'{{{doc_dict[ID]}}}':<5} ")
        print(f"| {doc_dict[TYPE]:<15} ")
        print(f"| {doc_dict[TEXT]:<50} ")
        print(f"| {doc_dict[DEADLINE] if doc_dict.get(DEADLINE) else '-':<25} |")
        print(f"+-{'':-<5}-+-{'':-<15}-+-{'':-<50}-+-{'':-<25}-+")
    print()


def complete_task(id: int) -> None:
    """
    Deletes a task document from the `uncompleted` collection and
    adds it to the `completed` collection.

    Params:
        `id: int` - The id of the task document to move from `uncompleted`
        to `completed`.
    """
    add_task(COMPLETED, delete_task(UNCOMPLETED, id))


def add_task(coll: str, task_dict: dict) -> None:
    """
    Adds a dictionary as a document to the specified collection.

    Params:
        `coll: str` - The collection of the `tasks` database.
        `task_dict: dict` - The dictionary of the task fields to add.
    """

    global COMP_ID
    global UNCOMP_ID

    new_task_ref: DocumentReference
    _, new_task_ref = DB.collection(coll).add(task_dict)
    new_task_ref.set(
        {ID: UNCOMP_ID if coll == UNCOMPLETED else COMP_ID},
        merge=True,
    )
    if coll == UNCOMPLETED:
        UNCOMP_ID += 1
    else:
        COMP_ID += 1


def delete_task(coll: str, id: int) -> dict:
    """
    Delete a task by it's id from the specified collection.

    Params:
        `coll: str` - The collection in the `tasks` firestore database.
        `id: int` - The id of the task document to delete.

    Returns:
        `dict` - A dictionary comprised of the removed document fields.
    """

    remove_dict: dict

    docs: Generator[DocumentSnapshot] = (
        DB.collection(coll).where(filter=FieldFilter(ID, "==", id)).stream()
    )
    for doc in docs:
        remove_dict = doc.to_dict()
        doc_ref: DocumentReference = doc.reference
        doc_ref.delete()
    update_ids()

    return remove_dict


def main() -> None:
    """Program main."""

    # First thing to do is update doc IDs
    update_ids()

    while True:
        command = menu()

        match command:
            # List all tasks.
            case 1:
                list_tasks(UNCOMPLETED)
                list_tasks(COMPLETED)

            # Add an uncompleted task.
            case 2:
                print("Enter task information.")
                t_type = input("Task type (Work, Personal, etc.):\n> ")
                t_text = input("Task:\n> ")
                try:
                    t_deadline_date = date(
                        *list(
                            map(
                                lambda x: int(x),
                                input(
                                    "Deadline date ('YYYY-MM-DD' | 'None'):\n> ",
                                ).split("-"),
                            )
                        )
                    )
                    t_deadline = t_deadline_date.strftime("%b %d, %Y")
                except ValueError as ve:
                    t_deadline = None

                add_task(
                    UNCOMPLETED,
                    {
                        TYPE: t_type,
                        TEXT: t_text,
                        DEADLINE: t_deadline,
                    },
                )

            # Move a task from uncompleted collection to completed collection.
            case 3:
                list_tasks(UNCOMPLETED)
                # If uncompleted collection has no documents, unable to complete a task.
                try:
                    DB.collection(UNCOMPLETED).stream().__next__()
                except StopIteration:
                    print("INFO:\tNo uncompleted tasks.")
                    continue

                complete_id: int
                while True:
                    complete_id = int(input("ID of task to complete:\n> "))
                    if 0 <= complete_id < UNCOMP_ID:
                        break
                    print("ERROR:\tInvalid task ID.")
                complete_task(complete_id)

            # Remove a completed task.
            case 4:
                list_tasks(COMPLETED)
                # If completed collection has no documents, unable to delete a task.
                try:
                    DB.collection(COMPLETED).stream().__next__()
                except StopIteration:
                    print("INFO:\tNo completed tasks to delete.")
                    continue

                delete_id: int
                while True:
                    delete_id = int(input("ID of task to delete:\n> "))
                    if 0 <= delete_id < COMP_ID:
                        break
                    print("ERROR:\tInvalid task ID.")
                delete_task(COMPLETED, delete_id)

            # Quit program.
            case 0:
                break

            # Default
            case _:
                print("ERROR:\tInvalid command.")


if __name__ == "__main__":
    main()
