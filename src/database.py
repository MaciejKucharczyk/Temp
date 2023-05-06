import logging
import sys
import mysql.connector


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Database:
    """
    Allows to perform basic operations on the database.
    """

    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        print("Connecting...")
        self.connection = self.connect_to_database()
        print("Connected to database")

    def connect_to_database(self):
        """
        Connects to the database.
        """
        try:
            conn = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
        except mysql.connector.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        return conn

    def select_from_database(self, select_query):
        """
        Executes 'SELECT' query to database and returns cursor.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(select_query)
            return cursor

        except mysql.connector.Error as error:
            logger.error("Select query error: %s", error)
            sys.exit()

    def insert_into_database(self, insert_query, data):
        """
        Executes 'INSERT' query to database.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, data)
            self.connection.commit()

        except mysql.connector.Error as error:
            logger.error("Insert query error: %s", error)
            self.connection.rollback()

    def delete_from_database(self, delete_query: str, data: list = []):
        """
        Executes 'DELETE' query to database.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_query, data)
            self.connection.commit()

        except mysql.connector.Error as error:
            logger.error("Insert query error: %s", error)
            self.connection.rollback()


    def close_connection(self):
        """
        Closes the connection to the database.
        """
        try:
            self.connection.close()
            logger.debug("Connection closed")

        except mysql.connector.Error as error:
            logger.info("Connection does not exist: %s", error)

    def __del__(self):
        self.close_connection()


if __name__ == "__main__":
    pass
