import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class Database:
    _conn = None

    @classmethod
    def get_connection(cls):
        try:
            if cls._conn is None or not cls._conn.is_connected():
                cls._conn = mysql.connector.connect(**DB_CONFIG)
        except Error as e:
            raise ConnectionError(f"Gagal koneksi ke database: {e}")
        return cls._conn

    @classmethod
    def cursor(cls, dictionary=True):
        return cls.get_connection().cursor(dictionary=dictionary)

    @classmethod
    def commit(cls):
        if cls._conn:
            cls._conn.commit()

    @classmethod
    def rollback(cls):
        if cls._conn:
            cls._conn.rollback()

    @classmethod
    def close(cls):
        if cls._conn and cls._conn.is_connected():
            cls._conn.close()
            cls._conn = None
