import psycopg2
from psycopg2.extras import DictCursor
from urllib.parse import urlparse, parse_qs


def get_psycopg2_conn(database_url):
    # Parse the database URL
    url = urlparse(database_url)

    # Extract the components
    dbname = url.path[1:]  # Remove leading '/'
    user = url.username
    password = url.password
    host = url.hostname
    port = url.port

    # Connection parameters dictionary
    conn_params = {
        'dbname': dbname,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }

    # Connect to the database
    conn = psycopg2.connect(**conn_params)

    return conn


class PostgresManager:
    def __init__(self, database_url):
        self.connection = get_psycopg2_conn(
                database_url
       )

    def __del__(self):
        self.connection.close()

    def execute(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()
        return cursor.rowcount

    def select(self, sql):
        cursor = self.connection.cursor(
            cursor_factory=DictCursor
        )
        cursor.execute(sql)
        return cursor.fetchall()

    def update(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()
        return cursor.rowcount
    
    def insert(self, table, data):
        cursor = self.connection.cursor()
        columns = data[0].keys()
        columns = ['"' + x + '"' for x in columns]
        column_str = ', '.join(columns)
        value_str = ', '.join(['%s' for _ in columns])
        query = f"""
                    INSERT INTO {table} ({column_str})
                    VALUES ({value_str})
                """
        cursor.executemany(query, [tuple(x.values())
                                   for x in data])
        self.connection.commit()
        return cursor.rowcount

    def close(self):
        self.connection.close()

