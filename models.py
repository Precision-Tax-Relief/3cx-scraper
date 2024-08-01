import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text

missing_environment_variables = []

def get_env_variable(var_name, default=None):
    value = os.getenv(var_name, default)
    if not value:
        missing_environment_variables.append(var_name)
    return value

DB_USERNAME = get_env_variable('DB_USERNAME')
DB_PASSWORD = get_env_variable('DB_PASSWORD')
DB_HOST = get_env_variable('DB_HOST')
DB_PORT = get_env_variable('DB_PORT')
DB_NAME = get_env_variable('DB_NAME')


def get_unmapped_appointments():
    connection_string = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print('Connecting to database...')
    engine = create_engine(connection_string)
    print('Connected to database')

    # Define your SQL query
    query = """
SELECT
    id, location, received_at
FROM
    booker_prod.appointments
WHERE
    order_number IS NULL
ORDER BY
    received_at DESC;
    """
    sql_query = text(query)

    locations = {}

    # Connect to the database and execute the query
    with engine.connect() as connection:
        result = connection.execute(sql_query)
        print(f'Found {result.rowcount} unmapped appointments')
        for row in result:
            if row[1] not in locations:
                locations[row[1]] = []
            locations[row[1]].append(row[0])

    return locations


if __name__ == "__main__":
    from pprint import pprint
    pprint(get_unmapped_appointments())