import os
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Database:
    def __init__(self):
        self.db_path = os.getenv('DB_PATH', '/data/db/calls.db')
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Ensure database and tables exist"""
        logger.info(f"Checking if database exists at {self.db_path}")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self.get_connection() as conn:
            with open('db_init.sql', 'r') as f:
                conn.executescript(f.read())

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def insert_calls(self, calls_data):
        """Insert multiple call records"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany("""
                    INSERT OR REPLACE INTO calls (
                        id, call_end, from_name, from_number,
                        dialed, to_number, duration, download_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    (
                        call['id'],
                        call['date'],
                        call['from_name'],
                        call.get('from', ''),  # Using get() as 'from' is a reserved word
                        call['dialed'],
                        call.get('to', ''),
                        call['duration'],
                        call['download_url']
                    )
                    for call in calls_data
                ])
                conn.commit()
                logger.info(f"Successfully inserted {len(calls_data)} records")
            except Exception as e:
                logger.error(f"Error inserting records: {str(e)}")
                conn.rollback()
                raise

    def get_latest_calls(self, limit=100):
        """Retrieve the latest calls"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT * FROM calls
                           ORDER BY call_time DESC
                               LIMIT ?
                           """, (limit,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
