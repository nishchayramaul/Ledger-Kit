from sqlalchemy import values


def insert_entry(entry: Entry) -> Entry:
    statement = insert(entry)
