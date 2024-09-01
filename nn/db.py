from abc import ABC, abstractmethod
import datetime
from typing import List


class StoreError(RuntimeError):
    pass


class Store(ABC):
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_links(self, last: int = None, since: datetime.datetime = None):
        pass

    @abstractmethod
    def get_events(self, last: int = None, since: datetime.datetime = None):
        pass


import sqlite3
from urllib.parse import urlparse
from nn.events import Event


class SQLiteStoreError(StoreError):
    pass


class SQLiteStore(Store):
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
                txt TEXT,
                ctime DEFAULT CURRENT_TIMESTAMP,
                utime DEFAULT CURRENT_TIMESTAMP);
        """
        self.conn.execute(sql)
        sql = """
            create view if not exists view_latest
                (ts, url, title, preview)
            as
                select date(utime), url, title, preview
                from bookmarks
                order by utime desc
        """
        self.conn.execute(sql)
        sql = """
            create table if not exists events (
                id INTEGER PRIMARY KEY,
                key TEXT,
                title TEXT,
                description TEXT,
                start TEXT,
                end TEXT,
                venue TEXT,
                address TEXT,
                url TEXT UNIQUE,
                ctime DEFAULT CURRENT_TIMESTAMP,
                utime DEFAULT CURRENT_TIMESTAMP)
        """
        self.conn.execute(sql)

    def close(self):
        self.conn.close()

    def get_links(
        self, last: int = None, since: datetime.datetime = None, for_year: int = None
    ):
        if last:
            sql = f"select * from view_latest limit {last}"
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            return rows
        if for_year:
            sql = f"""
                select ts, url, title, preview from view_latest
                where ts >= date('{for_year}-01-01')
                      and ts <= date('{for_year}-12-31')
            """
            cur = self.conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            return rows
        return list()

    def get_links_with_incomplete_title(self):
        sql = """
            select ts, url, title, preview from view_latest
            where title is null or url = title
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    def add_links(self, links):
        sql = """
        insert into bookmarks (ctime, utime, url, title, preview) values (?,?,?,?,?)
            on conflict(url) do update set utime = EXCLUDED.ctime
        """
        cur = self.conn.cursor()
        cur.executemany(sql, links)
        self.conn.commit()

    def update_link_title(self, url, title):
        sql = """
            update bookmarks set title = ? where url = ?
        """
        cur = self.conn.cursor()
        cur.execute(sql, (title, url))
        self.conn.commit()

    def add_events(self, events: List[Event]):
        sql = """
        insert into events
            (key, title, description, start, end, venue, address, url)
        values
            (:key, :title, :description, :start, :end, :venue, :address, :ref)
        """
        cur = self.conn.cursor()
        dicts = [e.dict() for e in events]
        cur.executemany(sql, dicts)
        self.conn.commit()

    def get_events(self, last: int = None, since: datetime.datetime = None):
        sql = """
            select key, title, description, start, end, venue,
                   address, url
            from events
            where
                datetime(end) > datetime()
                and datetime(start) < datetime('now', '+3 months')
            order by datetime(start);
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = ['key', 'title', 'description', 'start', 'end',
                   'venue', 'address', 'ref']
        # this seems like a lot of wasteful conversion
        events = [Event(**dict(zip(columns, row))) for row in rows]
        return events


def create_store(url):
    # factory method with a single switch
    return SQLiteStore(url)
