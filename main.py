import discord, datetime, asyncio, pytz, os, psycopg2, threading, psycopg2.extras

client = discord.Client()

def start_await(func, *args, **kwargs):
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	# Blocking call which returns when the display_date() coroutine is done
	loop.run_until_complete(func(*args, **kwargs))
	loop.close()

async def remindercmdusage(message, e):
	if e:
		await message.channel.send("""Usage: `$reminder [01-12]:[00-59][am|pm] [01-12]-[01-31]-[00-99] <Reminder Message>`
Example: `$reminder 08:00am 12-25-20 Christmas!` outputs `@everyone Christmas!` at 8am on December 25, 2020.
(Reminder Name is optional - defaults to `Here's a reminder set on [date] at [time]!`)
This message appeared because of this exception: `{exception}`""".format(exception = e))
	else:
		await message.channel.send("""Usage: `$reminder [01-12]:[00-59][am|pm] [01-12]-[01-31]-[00-99] <Reminder Message>`
Example: `$reminder 08:00am 12-25-20 Christmas!` outputs `@everyone Christmas!` at 8am on December 25, 2020.
(Reminder Name is optional - defaults to `Here's a reminder set on [date] at [time]!`)""")

@client.event
async def on_ready():
	global sql, sql_io
	print("Login successful for bot: {0.user}".format(client))
	sql = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require')
	sql.autocommit = True
	sql_io = sql.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	sql_io.execute("SELECT * FROM reminders")
	for reminder in sql_io:
		print("Found pending reminder on {date} at {time} with message \"{message}\"".format(date = reminder["dateandtime"].strftime("%m-%d-%y"), time = reminder["dateandtime"].strftime("%I:%M%p"), message = reminder["message"]))
		threading.Thread(target=start_await, args=(on_message, "$reminder {time} {date} {message}".format(date = reminder["dateandtime"].strftime("%m-%d-%y"), time = reminder["dateandtime"].strftime("%I:%M%p"), message = reminder["message"])), kwargs={"from_on_ready": True, "channel_id": reminder["channel_id"]}).start()

@client.event
async def on_message(message, from_on_ready=False, channel_id=None):
	global sql, sql_io, client
	if not from_on_ready:
		if message.author == client.user:
			return
	
	if not from_on_ready:
		args = message.content.split(" ")
	else:
		args = message.split(" ")

	if args[0] == "$reminder":
		try:
			time = datetime.datetime.strptime(args[1], "%I:%M%p").time()
		except (IndexError, ValueError) as e:
			await remindercmdusage(message, e)
		else:
			try:
				date = datetime.datetime.strptime(args[2], "%m-%d-%y").date()
			except (IndexError, ValueError) as e:
				await remindercmdusage(message, e)
			else:
				if len(args) > 3:
					reminder_message = " ".join(args[3:])
				else:
					reminder_message = "Here's a reminder set on {date} at {time}!".format(date = datetime.datetime.now().strftime("%m-%d-%y"), time = datetime.datetime.now().strftime("%I:%M%p"))
					
				dateandtime = datetime.datetime.combine(date, time).replace(second = 0, microsecond = 0).astimezone(pytz.timezone("America/Los_Angeles"))
				
				if not from_on_ready:
					sentmessage = await message.channel.send("Reminder set for {date} at {time}!".format(date = date.strftime("%m-%d-%y"), time = time.strftime("%I:%M%p")))
					sql_io.execute("INSERT INTO reminders (message, dateandtime, channel_id) VALUES (%s, %s, %s)", (reminder_message, dateandtime, message.channel.id))
					
				print("Reminder set for {date} at {time}!".format(date = date.strftime("%m-%d-%y"), time = time.strftime("%I:%M%p")))
				await asyncio.sleep(10)
				if not from_on_ready:
					await message.delete()
					await sentmessage.delete()

				while True:
					currentdateandtime = pytz.utc.localize(datetime.datetime.now().replace(second = 0, microsecond = 0))
					print("Checking if {current} == {set}...".format(current = currentdateandtime, set = dateandtime))
					if currentdateandtime == dateandtime:
						print("Check succeeded!")
						break
					await asyncio.sleep(10)
				if not from_on_ready:
					await message.channel.send("@everyone " + reminder_message)
					print("Reminder sent!")
				else:
					await client.channels.get(str(channel_id)).send("@everyone " + reminder_message)
				sql_io.execute("DELETE FROM reminders WHERE dateandtime <= %s", (dateandtime,))

	elif args[0] == "$help":
		await remindercmdusage(message, None)

client.run(os.getenv('BOT_TOKEN'))
