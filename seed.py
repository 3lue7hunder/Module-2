import sqlite3

conn = sqlite3.connect("movies.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

movies = [
    ("The Shawshank Redemption", "Drama",      1994, "Frank Darabont"),
    ("The Dark Knight",          "Action",     2008, "Christopher Nolan"),
    ("Inception",                "Sci-Fi",     2010, "Christopher Nolan"),
    ("Parasite",                 "Thriller",   2019, "Bong Joon-ho"),
    ("The Lion King",            "Animation",  1994, "Roger Allers & Rob Minkoff"),
    ("Forrest Gump",             "Comedy",     1994, "Robert Zemeckis"),
    ("Interstellar",             "Sci-Fi",     2014, "Christopher Nolan"),
    ("The Godfather",            "Crime",      1972, "Francis Ford Coppola"),
    ("Titanic",                  "Romance",    1997, "James Cameron"),
    ("Gladiator",                "Action",     2000, "Ridley Scott"),
]

cursor.executemany("""
    INSERT INTO movies (title, genre, year, director) VALUES (?, ?, ?, ?)
""", movies)

ratings = [
    (1,  9.5, "A timeless masterpiece.",               "2024-01-10"),
    (2,  9.3, "Ledger's Joker is unforgettable.",      "2024-04-22"),
    (3,  8.5, "Mind-bending from start to finish.",    "2024-07-13"),
    (4,  9.0, "Deserved every Oscar it won.",          "2024-09-05"),
    (5,  8.8, "Still hits hard after all these years.","2024-11-30"),
    (6,  9.1, "Life is like a box of chocolates.",     "2025-02-14"),
    (7,  9.2, "Emotionally overwhelming.",             "2025-05-20"),
    (8,  9.7, "The greatest crime film ever made.",    "2025-08-08"),
    (9,  8.6, "I never cry at movies. I cried.",       "2025-11-11"),
    (10, 8.9, "Are you not entertained?",              "2026-03-15"),
]

cursor.executemany("""
    INSERT INTO ratings (movie_id, score, review, watched_on) VALUES (?, ?, ?, ?)
""", ratings)

conn.commit()
conn.close()
print("Database seeded successfully!")