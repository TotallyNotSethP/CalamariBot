import discord, datetime, asyncio, pytz, os

client = discord.Client()
bot    = discord.ext.commands.Bot(command_prefix="$")

async def remindercmdusage(message, e):
	await message.channel.send("""Usage: `$reminder [01-12]:[00-59][am|pm] [01-12]-[01-31]-[00-99] <Message>`
Example: `$reminder 08:00am 12-25-20 Christmas!` outputs `@everyone Christmas!` at 8am on December 25, 2020.
(Message is optional - defaults to `Here's a reminder set on [date] at [time]!`)
This message appeared because of this alert: `{exception}`""".format(exception = e))

@client.event
async def on_ready():
	print("Login successful for bot: {0.user}".format(client))

@bot.command()
async def reminder(ctx, time_, date_, *, message):
	print(f"$reminder invoked with time: \"{time_}\", date: \"{date_}\", message: \"{message}\"")

	try:
		time = datetime.datetime.strptime(time_, "%I:%M%p").time()
	except (IndexError, ValueError) as e:
		await remindercmdusage(message, e)
	else:
		try:
			date = datetime.datetime.strptime(date_, "%m-%d-%y").date()
		except (IndexError, ValueError) as e:
			await remindercmdusage(message, e)
		else:
			if message == "":
				message  = "Here's a reminder set on {date} at {time}!".format(
					date = datetime.datetime.now().strftime("%m-%d-%y"), 
					time = datetime.datetime.now().strftime("%I:%M%p")
				)
				
			dateandtime = pytz.timezone("America/Los_Angeles").localize(
				datetime.datetime.combine(date, time).replace(second = 0, microsecond = 0)
			)

			debug_msg   = "Reminder with message \"{message}\" set for {date} at {time}!".format(
				message = message,
				date    = date.strftime("%m-%d-%y"),
				time    = time.strftime("%I:%M%p")
			)
			sentmessage = await ctx.send(debug_msg)
			print(debug_msg)

			await asyncio.sleep(10)
			await ctx.message.delete()
			await sentmessage.delete()

			while True:
				currentdateandtime = pytz.utc.localize(
					datetime.datetime.now().replace(second = 0, microsecond = 0)
				)
				if currentdateandtime == dateandtime:
					break
				await asyncio.sleep(10)

			await message.channel.send("@everyone " + message)
			print("Sent reminder with message \"{message}\" to @everyone!")

client.run(os.getenv('BOT_TOKEN'))
