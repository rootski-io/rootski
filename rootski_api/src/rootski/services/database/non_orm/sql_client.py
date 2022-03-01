from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker


class SqlClient:
    """
    This class is a convenience wrapper around SQLAlchemy that makes it easy
    to get an ``engine`` object to run queries against any SQL backend.

    The official SQLAlchemy documentation page on engines, connections, transactions,
    sessions, etc. is very good:
    https://docs.sqlalchemy.org/en/13/core/connections.html

    Using this class, you have 2 options for running queries:

    1. You can use the `run_query` method to execute queries like a typical client
    2. You can get an engine or session and do ORM style queries

    Usage:

    (1)

    SQLAlchemy requires underlying database drivers and python libraries to be installed.
    For example, to connect to MySQL, you would need to install the `PyMySQL` package and
    mysql driver binaries in the project that uses this class.

    .. code:: text

        # python dependencies
        postgres  : pip install psycopg2-binary
        mysql     : pip install pymysql
        snowflake : pip install snowflake-connector-python snowflake-sqlalchemy

    (2)

    One of the big advantages of SQLAlchemy is that it allows you to use SQLite for writing
    unit tests. Sadly, not all queries are testable in this way because of SQLite's limitations.
    The following are some of the bigger limitations:

    SQLite does not support

    1. ``RETURNING`` clauses on ``INSERT`` statements
    2. ``UPDATE`` statements with multiple-table criteria

    """

    def __init__(
        self,
        sql_dialect=None,
        driver_lib=None,
        username=None,
        password=None,
        host=None,
        port=None,
        database=None,
        engine_kwargs=dict(),
    ):
        """
        Note that the default sqlite connection string "sqlite://" is treated as
        "sqlite:///:memory:", so you can specify sql_dialect="sqlite" and leave
        all other parameters as default to interact with an in memory database for testing.

        Args:
            sql_dialect (str): "sqlite", "postgresql", "mysql", "snowflake", etc. The type of
                               SQL database being accessed
            driver_lib  (str): Optional - The python library used by SQLAlchemy to handle SQL queries
                               For example "psycopg2" or "pymysql"
            username    (str): database username
            password    (str): database password
            host        (str): database DNS name or IP address
            port        (int): port to on which to connect to the database e.g.
            database    (str): Optional - specific database/schema to connect to
            engine_kwargs (dict): Optional - additional configuration passed to the SQLAlchemy engine
                                  This includes dialect specific settings
        """

        # save init params
        self.sql_dialect = sql_dialect
        self.driver_lib = driver_lib
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        # select a default SQL library if driver_lib is unspecified
        if not driver_lib:
            self.driver_lib = {
                "sqlite": None,
                "postgresql": "psycopg2",  # pip install psycopg2-binary
                "mysql": "pymysql",  # pip install pymysql
                "snowflake": None,  # pip install snowflake-connector-python snowflake-sqlalchemy
            }.get(sql_dialect)

        # this can be of the form: "postgresql+psycopg2" or just "snowflake"
        drivername = f"{self.sql_dialect}+{self.driver_lib}" if self.driver_lib else self.sql_dialect
        url_params = {
            "drivername": drivername,
            "username": self.username,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "database": self.database,
        }
        self.connection_string = str(URL(**url_params))

        # SQLAlchemy best practice is to have 1 engine instance per application lifecycle
        self.engine = create_engine(self.connection_string, **engine_kwargs)

        # prepare a sessionmaker to make sessions available
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def run_query(self, query, *query_args, commit=True, fetch_all=False, return_raw_result=False):
        """
        Execute a SQL query.

        Args:
            query (str | sqlalchemy expression): a SQL expression expressed as a string or SQLAlchemy string object.
            query_args (object): any values that are to be inserted in some way into the query
            commit       (bool): whether or not to commit changes to the database
            fetch_all    (bool): returns a ResultProxy (array of ResultRowProxy) objects if True which can be treated as an array of Row results. Otherwise returns a single ResultRowProxy or None if no results are found.
            return_raw_results (bool): Set to True to skip fetching the query results. This is useful for non-select statements such as INSERT, UPDATE, CREATE, etc. which do not typically return anything.

        Returns:
            :py:class:`sqlalchemy.engine.result.ResultProxy`: This is a very useful object, with attributes like
                - ``is_insert`` for insert statements
                - ``rowcount`` for number of inserted/updated rows
                - ``lastrowid`` for the primary key of the last inserted row. See this link for the full API: https://www.kite.com/python/docs/sqlalchemy.engine.ResultProxy
        """

        to_return = None
        try:
            # the context manager automatically closes the connection and rolls back on exeptions
            with self.engine.connect() as connection:
                with connection.begin() as transaction:

                    # execute the query
                    result = connection.execute(query, query_args)
                    if return_raw_result:
                        # return the sqlalchemy.engine.result.ResultProxy object
                        to_return = result
                    else:
                        # default to fetching the results
                        to_return = result.fetchall() if fetch_all else result.fetchone()

                    # commit or rollback
                    if commit:
                        transaction.commit()
                    else:
                        transaction.rollback()

        except Exception as query_run_error:
            print(query_run_error)
            to_return = {"Error": "Failed to run query due to - {}".format(query_run_error)}

        return to_return


if __name__ == "__main__":

    # example init
    sql_client = SqlClient(
        sql_dialect="mysql",
        driver_lib="pymysql",
        username="root",
        password="password",
        host="localhost",
        port=3309,
        # database="bulk_scoring"
    )

    print(sql_client.connection_string)
