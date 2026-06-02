# Movie Rating Database

## Overview

As a software engineer working to deepen my understanding of relational databases, I built a Movie Rating Database application in Python using SQLite. This project allowed me to explore how real world applications store, relate, and query structured data skills that are foundational to backend development, data engineering, and nearly every production software system.

The software is a command line Python program that manages two related database tables: one for movies and one for user ratings. When run, it provides an interactive menu that supports a full lifecycle of database operations — inserting movies and ratings, querying them with a JOIN across both tables, filtering results by date range, updating existing records, and deleting entries (with cascading deletes). The program connects to a local SQLite database file (`movies.db`), builds all SQL commands programmatically, submits them through Python's `sqlite3` library, retrieves the results, and formats them into readable output in the console.

To use the program, simply run:

```bash
python movie_ratings.py
```

No external dependencies are required. Python 3.6+ and the built in `sqlite3` module are all you need. The program will create the `movies.db` file automatically if it does not exist and initialize the schema on first run.

My purpose in writing this software was to move beyond surface level SQL syntax and actually build a system that constructs and executes SQL dynamically, handles relational data across multiple tables, and uses query results meaningfully within application logic. The project also gave me hands on experience with foreign keys, aggregate functions, date filtering, and the practical tradeoffs of using an embedded database like SQLite.

[Software Demo Video](http://youtube.link.goes.here)

---

## Relational Database

This project uses **SQLite**, a lightweight, file based relational database engine built into Python's standard library. All data is stored in a single file (`movies.db`) that is created automatically when the program runs. SQLite is ideal for this type of project because it requires no server setup and is fully self contained, making the application easy to run anywhere.

### Table Structure

**`movies`** — Stores metadata about each film.

| Column     | Type    | Description                          |
|------------|---------|--------------------------------------|
| `id`       | INTEGER | Primary key, auto incremented        |
| `title`    | TEXT    | Movie title (required)               |
| `genre`    | TEXT    | Genre category (required)            |
| `year`     | INTEGER | Release year (required)              |
| `director` | TEXT    | Director name (optional)             |

**`ratings`** — Stores individual user ratings, linked to movies by foreign key.

| Column       | Type    | Description                                        |
|--------------|---------|----------------------------------------------------|
| `id`         | INTEGER | Primary key, auto incremented                      |
| `movie_id`   | INTEGER | Foreign key referencing `movies.id`                |
| `score`      | REAL    | Rating from 1.0 to 10.0 (enforced by CHECK)        |
| `review`     | TEXT    | Optional written review                             |
| `watched_on` | TEXT    | Date watched, stored as ISO format (YYYY-MM-DD)    |

The two tables are related through the `movie_id` foreign key with `ON DELETE CASCADE`, meaning that when a movie is deleted, all of its associated ratings are automatically removed as well.

---

## Development Environment

- **Editor:** Visual Studio Code
- **Language:** Python 3.12
- **Database:** SQLite (via Python's built in `sqlite3` standard library module — no installation required)
- **Operating System:** Windows / macOS / Linux (cross platform compatible)
- **Version Control:** Git / GitHub

No third party libraries or package installation is needed.

---

## Useful Websites

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite Official Documentation](https://www.sqlite.org/docs.html)
- [W3Schools SQL Tutorial](https://www.w3schools.com/sql/)
- [SQLite Tutorial (sqlitetutorial.net)](https://www.sqlitetutorial.net/)
- [Real Python — SQLite and Python](https://realpython.com/python-sqlite-sqlalchemy/)

---

## Future Work

- Add a `users` table to support multiple people tracking their own ratings independently.
- Implement genre based filtering so users can query "show me all my Sci-Fi ratings above 8.0."
- Export query results to a CSV or HTML report for sharing or archiving.
- Build a simple web front end using Flask to replace the command line interface with a browser based UI.