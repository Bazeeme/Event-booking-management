import os, time, psycopg2
from psycopg2.extras import RealDictCursor
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eventapp:basi1516@localhost:5432/eventbooking")
def connect():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
def wait_db():
    for _ in range(30):
        try:
            c=connect(); c.close(); return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("PostgreSQL did not become available")
