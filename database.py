import sqlite3


class DataBase():
    def __init__(self, db_file):
        self.db_file = db_file
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS files
                  (filename TEXT PRIMARY KEY,
                  mtime REAL, offset INTEGER(8))""")
        conn.commit()
        conn.close()

    def insert_ignore_file(self, filename, mtime):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute(
            """INSERT OR IGNORE INTO files VALUES(?,?,0)""", (filename, mtime))
        conn.commit()
        conn.close()

    def get_file(self, filename):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""SELECT * FROM files where filename=?""", (filename,))
        result = c.fetchone()
        conn.close()
        return result

    def update_file(self, filename, offset, mtime):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""UPDATE files
                  SET offset=?, mtime=?
                  WHERE filename=?""", (offset, mtime, filename))
        conn.commit()
        conn.close()

    # def update_offset_handler(self, dbqueue):
    #     conn = sqlite3.connect(self.db_file)
    #     c = conn.cursor()
    #     print("ready to get from queue")
    #     while True:
    #
    #         # filename, offset = dbqueue.get()
    #         # c.execute(
    #         #     """UPDATE files SET offset=? where filename=?""",
    #         #     (offset, filename))
    #         #
    #         # conn.commit()
    #         sleep(1)
    #         print("1")
    #         # print("got from queue", (filename, offset))
    #         # dbqueue.task_done()
    #
    #     conn.close()


if __name__ == "__main__":
    db = DataBase("test.db")
