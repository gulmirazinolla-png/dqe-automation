
import psycopg2
import pandas as pd

class PostgresConnectorContextManager:
    def __init__(
        self,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
    ):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

    def __enter__(self):
        # Open the PostgreSQL connection.
        self.connection = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Close the connection when leaving the context.
        self.connection.close()

    def get_data_sql(self, sql):
        # Use cursor metadata to preserve the query's column names.
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

        return pd.DataFrame(rows, columns=columns)

