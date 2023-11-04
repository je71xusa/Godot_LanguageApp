"""
To DO:
1. Entfernen von HTML code resten
2. Entfernen von Duplikaten mit gleichen Übersetzungen (Kontrolle: Pronunciation mizu; English water)
3. Kombinieren von japanischen Duplikaten mit unterschiedlichen Übersetzungen
    3.1 Audiofile path immer vom ersten
4. Update Index
"""

import sqlite3
import pandas as pd
import numpy as np
import re
import shutil
import os

def create_database_copy(original_db, new_db):
    shutil.copy2(original_db, new_db)
def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def clean_db_columns(database_file):
    # Connect to the database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    # Fetch all rows from the database
    cursor.execute("SELECT ID, Japanese, English, Pronunciation FROM Words")
    rows = cursor.fetchall()

    # Iterate over the rows and update them after removing HTML tags
    for row in rows:
        id_, japanese, english, pronunciation = row

        japanese_cleaned = remove_html_tags(japanese)
        english_cleaned = remove_html_tags(english)
        pronunciation_cleaned = remove_html_tags(pronunciation)

        # Update the database with the cleaned strings
        cursor.execute("UPDATE Words SET Japanese=?, English=?, Pronunciation=? WHERE ID=?",
                       (japanese_cleaned, english_cleaned, pronunciation_cleaned, id_))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database cleaned successfully!")


def remove_duplicates(database_file):
    # Connect to the database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Fetch all rows
    cursor.execute("SELECT ID, Japanese, English, Pronunciation FROM Words")
    rows = cursor.fetchall()

    seen = set()
    duplicates = []

    for row in rows:
        id_, japanese, english, pronunciation = row
        # We'll use a tuple of the columns' values to identify duplicates
        key = (japanese, english, pronunciation)

        if key in seen:
            duplicates.append(id_)
        else:
            seen.add(key)

    # Deleting duplicates from the database based on ID
    for duplicate_id in duplicates:
        cursor.execute("DELETE FROM Words WHERE ID=?", (duplicate_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"{len(duplicates)} duplicate rows removed!")


def combine_english_translations(database_file):
    # Connect to the database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Fetch all rows
    cursor.execute("SELECT ID, Japanese, English, Pronunciation FROM Words")
    rows = cursor.fetchall()

    # Dictionary to store combinations of Japanese and Pronunciation as keys and a list of English translations as values
    mapping = {}

    # Dictionary to store combinations of Japanese and Pronunciation as keys and a list of IDs as values
    id_mapping = {}

    for row in rows:
        id_, japanese, english, pronunciation = row
        key = (japanese, pronunciation)

        # Split the Englisch values by comma to get individual words
        english_values = [word.strip() for word in english.split(',')]

        if key not in mapping:
            mapping[key] = set(english_values)
            id_mapping[key] = [id_]
        else:
            mapping[key].update(english_values)
            id_mapping[key].append(id_)

    # Filter out duplicates where one form starts with 'to'
    def filter_infinitive_verbs(english_set):
        for verb in list(english_set):
            if "to " + verb in english_set:
                english_set.remove("to " + verb)
        return english_set

    # Update rows with combined and filtered English translations
    for key, english_set in mapping.items():
        japanese, pronunciation = key
        filtered_english_set = filter_infinitive_verbs(english_set)
        combined_english = ', '.join(filtered_english_set)

        # Update the first ID with the combined English value
        first_id = id_mapping[key][0]
        cursor.execute("UPDATE Words SET English=? WHERE ID=?", (combined_english, first_id))

        # Delete other rows
        for duplicate_id in id_mapping[key][1:]:
            cursor.execute("DELETE FROM Words WHERE ID=?", (duplicate_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("English translations combined and refined successfully!")

def reindex_rows(database_file):
    # Connect to the database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Fetch all rows (without ordering by original ID to maintain the existing order)
    cursor.execute("SELECT ID FROM Words")
    ids = [item[0] for item in cursor.fetchall()]

    # Update each row with a new ID
    for new_id, old_id in enumerate(ids, start=1):
        cursor.execute("UPDATE Words SET ID=? WHERE ID=?", (new_id, old_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Rows reindexed successfully!")

# Save it as a new database
def save_as_new_db(original_db, new_db):
    with open(original_db, 'rb') as source, open(new_db, 'wb') as target:
        target.write(source.read())
    print(f"Database saved as {new_db}!")


if __name__ == "__main__":
    # Create a copy before performing operations
    create_database_copy("JapaneseLearning.db", "JapaneseLearningCopy.db")
    database_file = "JapaneseLearningCopy.db"
    clean_db_columns(database_file)
    remove_duplicates(database_file)
    combine_english_translations(database_file)
    reindex_rows(database_file)


