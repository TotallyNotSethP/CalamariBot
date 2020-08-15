import discord, datetime, asyncio, pytz

client = discord.Client()

async def remindercmdusage(message, e):
	await message.channel.send("""Usage: `$reminder [01-12]:[00-59][am|pm] [01-12]-[01-31]-[00-99] <Reminder Name>`
Example: `$reminder 08:00am 12-25-20 Christmas!` outputs `@everyone Christmas!` at 8am on December 25, 2020.
(Reminder Name is optional - defaults to `Here's a reminder set on [date] at [time]!`)
This message appeared because of this alert: `{exception}`""".format(exception = e))

@client.event
async def on_ready():
	print("Login successful for bot: {0.user}".format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	args = message.content.split(" ")

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
					reminder_name = " ".join(args[3:])
				else:
					reminder_name = "Here's a reminder set on {date} at {time}!".format(date = datetime.datetime.now().strftime("%m-%d-%y"), time = datetime.datetime.now().strftime("%I:%M%p"))
					
				dateandtime = pytz.timezone("America/Los_Angeles").localize(datetime.datetime.combine(date, time).replace(second = 0, microsecond = 0))
				sentmessage = await message.channel.send("Reminder set for {date} at {time}!".format(date = date.strftime("%m-%d-%y"), time = time.strftime("%I:%M%p")))
				await asyncio.sleep(10)
				await message.delete()
				await sentmessage.delete()

				while True:
					currentdateandtime = pytz.utc.localize(datetime.datetime.now().replace(second = 0, microsecond = 0))
					if currentdateandtime == dateandtime:
						break
					await asyncio.sleep(10)

				await message.channel.send("@everyone " + reminder_name)

	elif args[0] == "$help":
		await remindercmdusage(message, "$help was triggered")

client.run("NzQ0MjUxMTg4MjAzMDk0MDY5.Xzgf7g.oe-lpJwHcRq0XVDdaiCeKKkZGUU")
