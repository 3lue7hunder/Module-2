"""
Movie Rating Database
A command line program to track movies you've watched and your ratings.
Uses SQLite with two related tables: movies and ratings.
"""

import sqlite3
from datetime import datetime


# ─────────────────────────────────────────────
# Database Setup
# ─────────────────────────────────────────────

def create_connection(db_file="movies.db"):
    """Create and return a database connection."""
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(conn):
    """Create tables if they don't already exist."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            genre       TEXT NOT NULL,
            year        INTEGER NOT NULL,
            director    TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id    INTEGER NOT NULL,
            score       REAL NOT NULL CHECK(score >= 1 AND score <= 10),
            review      TEXT,
            watched_on  TEXT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        )
    """)

    conn.commit()


# ─────────────────────────────────────────────
# INSERT Operations
# ─────────────────────────────────────────────

def add_movie(conn, title, genre, year, director=None):
    """Insert a new movie into the movies table."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movies (title, genre, year, director)
        VALUES (?, ?, ?, ?)
    """, (title, genre, year, director))
    conn.commit()
    movie_id = cursor.lastrowid
    print(f"\n  ✔ Movie added: '{title}' (ID: {movie_id})")
    return movie_id


def add_rating(conn, movie_id, score, review=None, watched_on=None):
    """Insert a rating for a given movie."""
    if watched_on is None:
        watched_on = datetime.today().strftime("%Y-%m-%d")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ratings (movie_id, score, review, watched_on)
        VALUES (?, ?, ?, ?)
    """, (movie_id, score, review, watched_on))
    conn.commit()
    print(f"  ✔ Rating added: {score}/10 on {watched_on}")


# ─────────────────────────────────────────────
# UPDATE Operations
# ─────────────────────────────────────────────

def update_rating(conn, rating_id, new_score, new_review=None):
    """Modify an existing rating's score and optional review."""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ratings SET score = ?, review = ? WHERE id = ?
    """, (new_score, new_review, rating_id))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"\n  ✘ No rating found with ID {rating_id}.")
    else:
        print(f"\n  ✔ Rating ID {rating_id} updated to {new_score}/10.")


def update_movie(conn, movie_id, title=None, genre=None, year=None, director=None):
    """Modify movie metadata."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    row = cursor.fetchone()
    if not row:
        print(f"\n  ✘ No movie found with ID {movie_id}.")
        return
    cursor.execute("""
        UPDATE movies SET title = ?, genre = ?, year = ?, director = ? WHERE id = ?
    """, (
        title    if title    is not None else row["title"],
        genre    if genre    is not None else row["genre"],
        year     if year     is not None else row["year"],
        director if director is not None else row["director"],
        movie_id
    ))
    conn.commit()
    print(f"\n  ✔ Movie ID {movie_id} updated.")


# ─────────────────────────────────────────────
# DELETE Operations
# ─────────────────────────────────────────────

def delete_movie(conn, movie_id):
    """Delete a movie and cascade-delete its ratings."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"\n  ✘ No movie found with ID {movie_id}.")
    else:
        print(f"\n  ✔ Movie ID {movie_id} and all its ratings deleted.")


def delete_rating(conn, rating_id):
    """Delete a single rating by ID."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ratings WHERE id = ?", (rating_id,))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"\n  ✘ No rating found with ID {rating_id}.")
    else:
        print(f"\n  ✔ Rating ID {rating_id} deleted.")


# ─────────────────────────────────────────────
# QUERY / RETRIEVE Operations
# ─────────────────────────────────────────────

def get_all_movies_with_ratings(conn):
    """JOIN query — all movies with average score and watch count."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            m.id,
            m.title,
            m.genre,
            m.year,
            m.director,
            COUNT(r.id)  AS times_watched,
            AVG(r.score) AS avg_score
        FROM movies m
        LEFT JOIN ratings r ON m.id = r.movie_id
        GROUP BY m.id
        ORDER BY m.id ASC
    """)
    return cursor.fetchall()


def get_ratings_for_movie(conn, movie_id):
    """Retrieve all ratings for a specific movie."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.score, r.review, r.watched_on, m.title
        FROM ratings r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.movie_id = ?
        ORDER BY r.watched_on DESC
    """, (movie_id,))
    return cursor.fetchall()


def get_ratings_in_date_range(conn, start_date, end_date):
    """Retrieve ratings watched between two dates."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, m.title, r.score, r.review, r.watched_on
        FROM ratings r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.watched_on BETWEEN ? AND ?
        ORDER BY r.watched_on
    """, (start_date, end_date))
    return cursor.fetchall()


def get_summary_stats(conn):
    """Aggregate summary of all ratings."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(r.id)  AS total_ratings,
            AVG(r.score) AS average_score,
            MAX(r.score) AS highest_score,
            MIN(r.score) AS lowest_score
        FROM ratings r
    """)
    return cursor.fetchone()


# ─────────────────────────────────────────────
# Display Helpers
# ─────────────────────────────────────────────

def print_divider():
    print("-" * 65)

def print_movie_table(rows):
    if not rows:
        print("  (no movies found)")
        return
    print(f"\n  {'ID':<4} {'Title':<38} {'Genre':<10} {'Year':<6} {'Score'}")
    print("  " + "-" * 63)
    for row in rows:
        avg = f"{row['avg_score']:.1f}/10" if row['avg_score'] is not None else "No ratings"
        print(f"  {row['id']:<4} {row['title']:<38} {row['genre']:<10} {row['year']:<6} {avg}")

def print_rating_rows(rows):
    if not rows:
        print("\n  (no ratings found)")
        return
    print(f"\n  {'ID':<4} {'Date':<12} {'Score':<8} Review")
    print("  " + "-" * 60)
    for row in rows:
        review_text = row['review'] if row['review'] else "-"
        print(f"  {row['id']:<4} {row['watched_on']:<12} {row['score']:<8} {review_text}")


# ─────────────────────────────────────────────
# Input Helpers
# ─────────────────────────────────────────────

def prompt(label, required=True):
    """Prompt the user for input, re-asking if required and blank."""
    while True:
        value = input(f"  {label}: ").strip()
        if value or not required:
            return value
        print("  This field is required. Please try again.")

def prompt_int(label, required=True):
    while True:
        value = prompt(label, required)
        if not value and not required:
            return None
        try:
            return int(value)
        except ValueError:
            print("  Please enter a whole number.")

def prompt_float(label, min_val=1.0, max_val=10.0):
    while True:
        value = prompt(label)
        try:
            f = float(value)
            if min_val <= f <= max_val:
                return f
            print(f"  Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("  Please enter a valid number (e.g. 8.5).")

def prompt_date(label):
    while True:
        value = prompt(f"{label} (YYYY-MM-DD, or press Enter for today)", required=False)
        if not value:
            return datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("  Invalid date format. Please use YYYY-MM-DD (e.g. 2024-06-15).")

def confirm(message):
    answer = input(f"\n  {message} (y/n): ").strip().lower()
    return answer == "y"


# ─────────────────────────────────────────────
# Menu Actions
# ─────────────────────────────────────────────

def menu_view_all_movies(conn):
    print("\n[ All Movies ]\n")
    rows = get_all_movies_with_ratings(conn)
    print_movie_table(rows)

def menu_add_movie(conn):
    print("\n[ Add a Movie ]\n")
    title    = prompt("Title")
    genre    = prompt("Genre (e.g. Action, Sci-Fi, Fantasy, Drama)")
    year     = prompt_int("Release Year")
    director = prompt("Director (optional, press Enter to skip)", required=False)
    add_movie(conn, title, genre, year, director or None)

def menu_add_rating(conn):
    print("\n[ Add a Rating ]\n")
    rows = get_all_movies_with_ratings(conn)
    if not rows:
        print("  No movies in the database yet. Add a movie first.")
        return
    print_movie_table(rows)
    movie_id = prompt_int("\n  Enter the Movie ID to rate")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM movies WHERE id = ?", (movie_id,))
    if not cursor.fetchone():
        print(f"\n  \u2718 No movie found with ID {movie_id}. Please choose a valid ID from the list.")
        return
    score      = prompt_float("Score (1.0 - 10.0)")
    review     = prompt("Short review (optional, press Enter to skip)", required=False)
    watched_on = prompt_date("Date watched")
    add_rating(conn, movie_id, score, review or None, watched_on)

def menu_update_rating(conn):
    print("\n[ Update a Rating ]\n")
    rows = get_all_movies_with_ratings(conn)
    if not rows:
        print("  No movies found.")
        return
    print_movie_table(rows)
    movie_id = prompt_int("\n  Enter the Movie ID to see its ratings")
    ratings  = get_ratings_for_movie(conn, movie_id)
    if not ratings:
        print("  No ratings found for that movie.")
        return
    print_rating_rows(ratings)
    rating_id  = prompt_int("\n  Enter the Rating ID to update")
    new_score  = prompt_float("New Score (1.0 - 10.0)")
    new_review = prompt("New review (optional, press Enter to skip)", required=False)
    update_rating(conn, rating_id, new_score, new_review or None)

def menu_update_movie(conn):
    print("\n[ Update a Movie ]\n")
    rows = get_all_movies_with_ratings(conn)
    if not rows:
        print("  No movies found.")
        return
    print_movie_table(rows)
    movie_id = prompt_int("\n  Enter the Movie ID to update")
    print("  (Press Enter to keep the current value)\n")
    title    = prompt("New Title    ", required=False)
    genre    = prompt("New Genre    ", required=False)
    year     = prompt_int("New Year     ", required=False)
    director = prompt("New Director ", required=False)
    update_movie(conn, movie_id,
                 title    or None,
                 genre    or None,
                 year     or None,
                 director or None)

def menu_delete_movie(conn):
    print("\n[ Delete a Movie ]\n")
    rows = get_all_movies_with_ratings(conn)
    if not rows:
        print("  No movies found.")
        return
    print_movie_table(rows)
    movie_id = prompt_int("\n  Enter the Movie ID to delete")
    if confirm(f"Delete movie ID {movie_id} and ALL its ratings? This cannot be undone."):
        delete_movie(conn, movie_id)
    else:
        print("\n  Cancelled.")

def menu_delete_rating(conn):
    print("\n[ Delete a Rating ]\n")
    rows = get_all_movies_with_ratings(conn)
    if not rows:
        print("  No movies found.")
        return
    print_movie_table(rows)
    movie_id = prompt_int("\n  Enter the Movie ID to see its ratings")
    ratings  = get_ratings_for_movie(conn, movie_id)
    if not ratings:
        print("  No ratings found for that movie.")
        return
    print_rating_rows(ratings)
    rating_id = prompt_int("\n  Enter the Rating ID to delete")
    if confirm(f"Delete rating ID {rating_id}?"):
        delete_rating(conn, rating_id)
    else:
        print("\n  Cancelled.")

def menu_view_ratings_by_date(conn):
    print("\n[ View Ratings by Date Range ]\n")
    start = prompt_date("Start date")
    end   = prompt_date("End date  ")
    rows  = get_ratings_in_date_range(conn, start, end)
    if not rows:
        print(f"\n  No ratings found between {start} and {end}.")
        return
    print(f"\n  Ratings watched between {start} and {end}:\n")
    print(f"  {'ID':<4} {'Title':<38} {'Score':<8} {'Date':<12} Review")
    print("  " + "-" * 75)
    for row in rows:
        review_text = row['review'] if row['review'] else "-"
        print(f"  {row['id']:<4} {row['title']:<38} {row['score']:<8} {row['watched_on']:<12} {review_text}")

def menu_summary_stats(conn):
    print("\n[ Overall Rating Statistics ]\n")
    stats = get_summary_stats(conn)
    if stats['total_ratings'] == 0:
        print("  No ratings yet. Add some ratings first.")
        return
    print(f"  Total ratings logged : {stats['total_ratings']}")
    print(f"  Average score        : {stats['average_score']:.2f} / 10")
    print(f"  Highest score        : {stats['highest_score']} / 10")
    print(f"  Lowest score         : {stats['lowest_score']} / 10")


# ─────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────

MENU_OPTIONS = {
    "1": ("View all movies",            menu_view_all_movies),
    "2": ("Add a movie",                menu_add_movie),
    "3": ("Add a rating",               menu_add_rating),
    "4": ("Update a rating",            menu_update_rating),
    "5": ("Update movie details",       menu_update_movie),
    "6": ("Delete a movie",             menu_delete_movie),
    "7": ("Delete a rating",            menu_delete_rating),
    "8": ("View ratings by date range", menu_view_ratings_by_date),
    "9": ("View summary statistics",    menu_summary_stats),
    "0": ("Exit",                       None),
}

def print_menu():
    print("\n" + "=" * 45)
    print("       🎬  Movie Rating Database")
    print("=" * 45)
    for key, (label, _) in MENU_OPTIONS.items():
        print(f"  {key}.  {label}")
    print("=" * 45)

def run():
    conn = create_connection()
    initialize_database(conn)
    print("\n  Welcome to your Movie Rating Database!")

    while True:
        print_menu()
        choice = input("  Enter your choice: ").strip()

        if choice == "0":
            print("\n  Goodbye! Your data has been saved to movies.db\n")
            break
        elif choice in MENU_OPTIONS:
            _, action = MENU_OPTIONS[choice]
            try:
                action(conn)
            except sqlite3.IntegrityError as e:
                print(f"\n  ✘ Database error: {e}")
            except Exception as e:
                print(f"\n  ✘ Unexpected error: {e}")
        else:
            print("\n  Invalid choice. Please enter a number from the menu.")

        input("\n  Press Enter to continue...")

    conn.close()


if __name__ == "__main__":
    run()