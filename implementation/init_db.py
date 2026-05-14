import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'lab.db')

SCHEMA_SQL = """
  CREATE TABLE IF NOT EXISTS students (
      id      INTEGER PRIMARY KEY AUTOINCREMENT,
      name    TEXT    NOT NULL,
      cohort  TEXT    NOT NULL,
      score   REAL    DEFAULT 0.0
  );

  CREATE TABLE IF NOT EXISTS courses (
      id    INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      code  TEXT NOT NULL UNIQUE
  );

  CREATE TABLE IF NOT EXISTS enrollments (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL REFERENCES students(id),
      course_id  INTEGER NOT NULL REFERENCES courses(id),
      grade      REAL
  );
  """
  
SEED_SQL = """
  INSERT OR IGNORE INTO students (name, cohort, score) VALUES
    ('Alice',   'A1', 92.5),
    ('Bob',     'A1', 78.0),
    ('Charlie', 'B2', 85.0),
    ('Diana',   'B2', 91.0),
    ('Eve',     'A1', 88.5);

  INSERT OR IGNORE INTO courses (title, code) VALUES
    ('Python Basics',    'PY101'),
    ('Data Structures',  'DS201'),
    ('Machine Learning', 'ML301');

  INSERT OR IGNORE INTO enrollments (student_id, course_id, grade) VALUES
    (1, 1, 95.0), (1, 2, 90.0),
    (2, 1, 75.0), (2, 3, 80.0),
    (3, 2, 88.0), (4, 1, 93.0),
    (5, 3, 87.0);
"""

def create_database():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.commit()
    conn.close()
    print(f"Database created at {DB_PATH}")
    return DB_PATH

if __name__ == "__main__":
    create_database()

  
