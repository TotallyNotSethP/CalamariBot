import psycopg2, pytz, psycopg2.extras, datetime, os

sql = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
sql.autocommit = True
sql_io = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

dateandtime = pytz.timezone("America/Los_Angeles").localize(
              datetime.datetime.now().replace(
              second = 0, microsecond = 0))

print(dateandtime)

sql_io.execute("INSERT INTO test (dateandtime) VALUES (%s)",
              (dateandtime,))

sql_io.execute("SELECT * FROM test")

for row in sql_io:
    print(pytz.timezone("America/Los_Angeles").localize(
          row["dateandtime"].replace(
          second = 0, microsecond = 0)))