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
    """Display menu and return user command."""

    print("Menu:")
    print("  1. List all tasks")
    print("  2. Add task")
    print("  3. Complete task")
    print("  4. Remove completed task")
    print("  0. Quit")
    return int(input("> "))


def update_ids() -> None:
    """Refresh the ids of all the documents in each collection. Used after
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
    """"""

    print(f"\n{coll.capitalize()} Tasks:")
    docs: Generator[DocumentSnapshot] = DB.collection(coll).order_by("id").stream()
    print(f"| {'ID':<5} | {'Type':<15} | {'Text':<50} | {'Deadline':<25} |")
    print(f"+-{'':-<5}-+-{'':-<50}-+-{'':-<25}-+")
    for doc_snap in docs:
        doc_dict = doc_snap.to_dict()
        print(
            f"| {f'{{{doc_dict[ID]}}}':<5} | {doc_dict[TYPE]:<15} | {doc_dict[TEXT]:<50} | {doc_dict.get(DEADLINE, '-'):<25} |"
        )
        print(f"+-{'':-<5}-+-{'':<15}-+-{'':-<50}-+-{'':-<25}-+")
    print()


def complete_task(id: int) -> None:
    """"""
    add_task(COMPLETED, delete_task(UNCOMPLETED, id))


def add_task(coll: str, task_dict) -> None:
    """"""

    global COMP_ID
    global UNCOMP_ID

    new_task_ref: DocumentReference
    _, new_task_ref = DB.collection(coll).add(task_dict)
    new_task_ref.set({ID: UNCOMP_ID if coll == UNCOMPLETED else COMP_ID}, merge=True)
    if coll == UNCOMPLETED:
        UNCOMP_ID += 1
    else:
        COMP_ID += 1


def delete_task(coll: str, id: int) -> dict:
    """Delete a task by it's id from the specified collection."""

    remove_doc: dict

    docs: Generator[DocumentSnapshot] = (
        DB.collection(coll).where(filter=FieldFilter(ID, "==", id)).stream()
    )
    for doc in docs:
        remove_doc = doc.to_dict()
        doc_ref: DocumentReference = doc.reference
        doc_ref.delete()
    update_ids()

    return remove_doc


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
                add_dict: dict
                print("Enter task information:")
                t_type = input("Task type:")
                add_task()

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

    # docs: Generator[DocumentReference] = DB.collection(UNCOMPLETED).list_documents()
    # doc: DocumentReference
    # for doc in docs:
    #     doc.delete()
    # SERIALID = 0

    # Add task
    # add_task(
    #     coll=UNCOMPLETED,
    #     task_dict={
    #         "type": TODO,
    #         "text": "Wash laundry",
    #     },
    # )
    # add_task(
    #     coll=UNCOMPLETED,
    #     task_dict={
    #         "type": DEADLINE,
    #         "text": "Internship approval form",
    #         "do-by": "January",
    #     },
    # )

    # Query
    # query_ref: Query = DB.collection(TASKS).where(
    #     filter=FieldFilter("type", "==", "deadline")
    # )
    # docs: Generator[DocumentSnapshot] = query_ref.stream()
    # print("\nTODO:")
    # doc: DocumentSnapshot
    # for doc in docs:
    #     print(f"{doc.id} => {doc.to_dict()}")
    # print()

    # Delete
    # docs: Generator[DocumentSnapshot] = (
    #     DB.collection(TASKS).where(filter=FieldFilter("id", "==", 2)).stream()
    # )
    # for doc_snap in docs:
    #     doc_ref: DocumentReference = doc_snap.reference
    #     doc_ref.delete()
    # update_ids()

    # list_tasks()


if __name__ == "__main__":
    main()
