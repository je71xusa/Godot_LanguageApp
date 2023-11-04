import sqlite3
import html
import re

# List of Anki databases
anki_dbs = ['japaneseSQL/Japanese_Core_2000_2k_-_Sorted_w_Audio/collection.anki2',
            'japaneseSQL/Japanese_Core_2000_Step_02_Listening_Sentence_Vocab__Images/collection.anki2',
            'japaneseSQL/Japanese_Visual_Novel_Anime_Manga_LN_Vocab_-_V2K/collection.anki2']

anki_media = ['japaneseSQL/2k_media',
              'japaneseSQL/2kStep_media',
              'japaneseSQL/VN_media']

# Connect to the Words SQLite database
words_conn = sqlite3.connect('JapaneseLearning.db')
words_c = words_conn.cursor()

# Initialize the database by creating the Words table
words_c.execute('''
    CREATE TABLE IF NOT EXISTS Words (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Japanese TEXT,
        English TEXT,
        Pronunciation TEXT,
        Audio TEXT
    )
''')

for idx, anki_db in enumerate(anki_dbs):
    # Connect to the SQLite database
    anki_conn = sqlite3.connect(anki_db)
    anki_c = anki_conn.cursor()

    # Query the notes table
    anki_c.execute('SELECT flds FROM notes')
    rows = anki_c.fetchall()

    # Initialize indices
    japanese_index = 1
    english_index = 4
    audio_index = 5

    # For each row, split the flds column and extract the relevant parts
    for i, row in enumerate(rows, start=1):
        flds = row[0].split('\x1f')
        japanese_word = flds[japanese_index]
        pronunciation = "TBD"
        english_translation = flds[english_index]
        audio = flds[audio_index]

        # Adjust the audio path to point to the correct media folder
        audio = audio.replace("[sound:", "").replace("]", "")
        audio_path = f"{anki_media[idx]}/{audio}"

        print(f"Processing row {i}: Japanese: {japanese_word}, English: {english_translation}, Audio: {audio_path}")

        # Ask for user confirmation before inserting the first row
        if i == 1:
            while True:
                user_input = input("Do you want to insert this row into the Words table? (y/n): ")
                if user_input.lower() in ['n', 'no']:
                    print(flds)
                    indices = input("Enter the indices for Japanese, English, and Audio, separated by commas: ")
                    japanese_index, english_index, audio_index = map(int, indices.split(','))
                    japanese_word = flds[japanese_index]
                    english_translation = flds[english_index]
                    audio = flds[audio_index]
                    print(f"New values: Japanese: {japanese_word}, English: {english_translation}, Audio: {audio}")
                    user_input = input("Are these values correct? (y/n): ")
                    if user_input.lower() in ['y', 'yes']:
                        break
                elif user_input.lower() in ['y', 'yes']:
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

        # Insert the data into the Words table in the Words database
        words_c.execute('''
            INSERT OR IGNORE INTO Words (Japanese, English, Pronunciation, Audio)
            VALUES (?, ?, ?, ?)
        ''', (japanese_word, english_translation, pronunciation, audio_path))

    # Commit the changes and close the connections
    words_conn.commit()
    anki_conn.close()

print("Finished processing all rows.")
words_conn.close()
