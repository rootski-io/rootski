from rootski_api.services.sql_client import SqlClient

# this is a helper file that we can use for logic
# that retrieves database credentials
ENV = {
    "local": {
        "rootski_db": {
            "sql_dialect": "postgresql",
            "host": "localhost",
            "username": "rootski",
            "password": "pass",
            "database": "rootski_db",
            "port": 5432,
        },
    },
    "dev": {"rootski_db": {}},
    "staging": {"rootski_db": {}},
    "prod": {"rootski_db": {}},
}


def get_conn_string(env="local", db="rootski_db", confirm_url_with_user=True):
    """
    Retrieves the connection string for the desired environment and region

    Args:
        env                  (str) : local, dev, staging, prod
        db                   (str) : rootski_db
        confirm_url_with_use (bool):
            Makes the user acknowledge the connection string before returning.
            This can be used to halt a migration before it goes through.
    """

    # retrieve the formatted connection string
    conn_params = ENV[env][db]
    sql_client = SqlClient(**conn_params)
    conn_string = sql_client.connection_string

    # confirm with the user before returning
    if confirm_url_with_user:
        answer = input(f"Using connection string: {conn_string}. Do you want to continue? (y/n)")
        if answer != "y":
            exit(1)

    return conn_string


def get_x_arguments(context):
    """
    Helper function for env.py scripts

    It extracts a dictionary of key value arguments passed to alembic
    like this:

    Example:
    $ alembic -x env=local -x db=russian_db ... upgrade ae9813df

    Args:
        context (alembic.EnvironmentContext): the context variable created
            in the env.py script. It has information inside of it about the
            arguments passed into the "alembic" CLI tool.

    Returns:
        (dict): dictionary of all the key-value x argument pairs
    """
    return context.get_x_argument(as_dictionary=True)


def get_environment(context):
    """
    Halts the migration and prints a helpful error message if "env"
    is not provided as an x argument.
    """

    # get x arguments from "alembic -x key=value upgrade ..."
    x_arguments = get_x_arguments(context)
    environment = x_arguments.get("env")
    if not environment:
        print("[rootski] missing required argument 'env'.")
        print("[rootski] Should be 'local', 'dev', 'staging', or 'prod'")
        print("[rootski] Example: alembic -x env=local upgrade abc12345")
        exit(0)

    print("[rootski] Got the following arguments:", x_arguments)

    return environment


if __name__ == "__main__":

    # example connection string from argument
    conn_string = get_conn_string(env="local", db="rootski_db")
    print(conn_string)
