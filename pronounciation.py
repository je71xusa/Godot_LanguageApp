import sqlite3
from pykakasi import kakasi
import re
import html

# Initialize kakasi
kakasi = kakasi()
kakasi.setMode("H", "a")  # Hiragana to ascii
kakasi.setMode("K", "a")  # Katakana to ascii
kakasi.setMode("J", "a")  # Japanese to ascii (for kanji)
conv = kakasi.getConverter()

# Connect to the SQLite database
conn = sqlite3.connect('JapaneseLearning.db')
c = conn.cursor()

# Fetch all Japanese words from the database
c.execute('SELECT ID, Japanese FROM Words')
rows = c.fetchall()

for row in rows:
    id, japanese_word = row
    # Convert Japanese word to romaji
    romaji = conv.do(japanese_word)
    # Remove HTML tags and unescape HTML entities
    clean_romaji = html.unescape(re.sub(r'<.*?>', '', romaji))
    # Update the pronunciation in the database
    c.execute('UPDATE Words SET Pronunciation = ? WHERE ID = ?', (clean_romaji, id))

# Commit the changes
conn.commit()
conn.close()

print("Finished processing all rows!")