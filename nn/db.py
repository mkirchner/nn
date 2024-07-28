from abc import ABC, abstractmethod
import datetime

class LinkStoreError(RuntimeError):
    pass

class LinkStore(ABC):
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_links(self, last: int = None, since: datetime.datetime = None):
        pass


import sqlite3
from urllib.parse import urlparse

class SQLiteLinkStoreError(LinkStoreError):
    pass

class SQLiteLinkStore(LinkStore):
    def __init__(self, url):
        # parse URL
        o = urlparse(url)
        if not o.scheme or o.scheme.lower() != "sqlite":
            raise SQLiteLinkStoreError("Invalid URL scheme for SQLite")
        if o.netloc:
            raise SQLiteLinkStoreError("Netloc must be empty for SQLite")
        # connect to DB
        self.conn = None
        try:
            self.conn = sqlite3.connect(o.path)
        except:
            raise SQLiteLinkStoreError("Could not connect to SQLite DB")
        # initialize tables if required
        self._init_db()

    def _init_db(self):
        # TODO: create proper indexes
        sql = """
            create table if not exists bookmarks (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT,
                preview TEXT,
                ctime DEFAULT CURRENT_TIMESTAMP,
                utime DEFAULT CURRENT_TIMESTAMP);
        """
        self.conn.execute(sql)
        sql = """
            create view if not exists view_latest
                (ts, url, title, preview)
            as
                select utime, url, title, preview
                from bookmarks
                order by utime desc
        """
        self.conn.execute(sql)

    def close(self):
        self.conn.close()

    def get_links(self, last: int = None, since: datetime.datetime = None):
        if last:
            sql = f"select * from view_latest limit {last}"
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            # FIXME: add conversion?
            return rows
        return list()

    def add_links(self, links):
        sql = """
        insert into bookmarks (ctime, utime, url, title, preview) values (?,?,?,?,?)
            on conflict(url) do update set utime = EXCLUDED.ctime
        """
        cur = self.conn.cursor()
        cur.executemany(sql, links)
        self.conn.commit()

def create_linkstore(url):
    # factory method with a single switch
    return SQLiteLinkStore(url)

