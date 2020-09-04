import psycopg2, pytz, psycopg2.extras, datetime, os

sql = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
sql.autocommit = True
sql_io = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

dateandtime = datetime.datetime.now().replace(
              second = 0, microsecond = 0).astimezone(pytz.timezone("America/Los_Angeles"))

print(dateandtime)

sql_io.execute("INSERT INTO test (dateandtime) VALUES (%s)",
              (dateandtime,))

sql_io.execute("SELECT * FROM test")

for row in sql_io:
    print(row["dateandtime"].replace(
          second = 0, microsecond = 0).astimezone(pytz.timezone("America/Los_Angeles")))