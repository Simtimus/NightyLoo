# Importarea librariilor
import os
import pytz
import discord
import asyncio
import datetime
from datetime import date
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption

# Importarea fisierelor
import database
import lessons_config as l_conf
import config_handler as conf_h

if conf_h.is_local_run is False:
	import keep_alive

# Initializarea discord
intents = discord.Intents.all()
client = commands.Bot(command_prefix=conf_h.prefix, case_insensitive=True, intents=intents)

# Variabile principale
global saptamana
global saptamana_v
global current_date
global ziua_saptamanii
global day
global timpul
global timpul_exact

vesela_lib = database.DBlib(host=conf_h.vesela_host, user=conf_h.vesela_user, password=conf_h.vesela_password, database=conf_h.vesela_database)
school_lib = database.DBlib(host=conf_h.school_host, user=conf_h.school_user, password=conf_h.school_password, database=conf_h.school_database)


# Functii utilizate in program
# //////////////////////////////////
def embeded(ctx, title, description, colour=discord.Colour.blue(), fields=None):
	embed = discord.Embed(
		title=title,
		description=description,
		colour=colour
	)
	embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
	if fields is not None:
		index = 0
		while index < len(fields):
			embed.add_field(name=fields[index][0], value=fields[index][1], inline=fields[index][2])
			index += 1

	return embed


# //////////////////////////////////
async def lessons_config_update():
	pass

# //////////////////////////////////


# Initializarea proceselor
@client.event
async def on_ready():
	print('Logged in as {0} (ID:{1}) | Connected to {2} users'.format(client.user.name, client.user.id, len(set(client.get_all_members()))))
	global saptamana
	global saptamana_v
	global ziua_saptamanii
	global current_date
	global day
	global timpul
	global timpul_exact

	current_date = 0

	DiscordComponents(client)
	# Calculating exact time
	while True:
		date_today = datetime.datetime.now(pytz.timezone("Europe/Chisinau"))
		num_of_weeks = date_today.isocalendar()[1]
		if num_of_weeks % 2 == 0:
			saptamana = 'Para'
		else:
			saptamana = 'Impara'

		saptamana_v = 'Para'
		if saptamana == 'Para':
			saptamana_v = 'Impara'

		day = datetime.datetime.utcnow()
		day += datetime.timedelta(hours=3)
		timpul = day.hour * 60 + day.minute
		timpul_exact = day.hour * 3600 + day.minute * 60 + day.second
		current_date = day.weekday()
		timpul = 540
		current_date = 2
		ziua_saptamanii = l_conf.zilele[current_date]
		await asyncio.sleep(10)


for filename in os.listdir('cog'):
	if filename.endswith('.py'):
		client.load_extension(f'cog.{filename[:-3]}')

if conf_h.is_local_run is False:
	keep_alive.keep_alive()
client.run(conf_h.TOKEN)
