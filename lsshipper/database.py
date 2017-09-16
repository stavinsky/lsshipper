import sqlite3


class DataBase():
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.c = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        self.c.execute("""CREATE TABLE IF NOT EXISTS files
                  (filename TEXT PRIMARY KEY,
                  mtime REAL, offset INTEGER(8))""")
        self.conn.commit()

    def insert_ignore_file(self, filename, mtime):
        self.c.execute(
            """INSERT OR IGNORE INTO files VALUES(?,?,0)""",
            (filename, mtime))
        self.conn.commit()

    def get_file(self, filename):
        self.c.execute("""SELECT * FROM files where filename=?""", (filename,))
        result = self.c.fetchone()

        return result

    def sync_from_db(self, f):
        self.insert_ignore_file(f['name'], 0)
        r = self.get_file(f['name'])
        f['last_mtime'] = r[1]
        f['offset'] = r[2]
        return f

    def update_file(self, filename, offset, mtime):
        self.c.execute("""UPDATE files
                  SET offset=?, mtime=?
                  WHERE filename=?""", (offset, mtime, filename))

        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
