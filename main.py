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
def lessons_config_update():
	vesela_lib.connect()
	default = vesela_lib.read_rows('OrarulSunetelor')
	custom = vesela_lib.read_rows('OrarulSunetelor', 2, 2)
	time = 480

	if custom[0][4] <= datetime.date.today() <= custom[0][5]:
		lesson = int(custom[0][1])
		pause = int(custom[0][2])
		big_pause = int(custom[0][3])
	else:
		lesson = int(default[0][1])
		pause = int(default[0][2])
		big_pause = int(default[0][3])

	element = 0
	while element < len(l_conf.orarul[0]):
		ora_inceput = f'{time//60}:{(time%60 if len(str(time%60)) == 2 else "0" + str(time%60))}'
		time += lesson
		ora_sfarsit = f'{time//60}:{(time%60 if len(str(time%60)) == 2 else "0" + str(time%60))}'
		l_conf.orarul[0][element] = f'{ora_inceput} - {ora_sfarsit}'
		element += 1

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
	timpul = 0

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

		if timpul == 700 or timpul == 0:
			lessons_config_update()

		day = datetime.datetime.utcnow()
		day += datetime.timedelta(hours=3)
		timpul = day.hour * 60 + day.minute
		timpul_exact = day.hour * 3600 + day.minute * 60 + day.second
		current_date = day.weekday()
		ziua_saptamanii = l_conf.zilele[current_date]
		await asyncio.sleep(10)


for filename in os.listdir('cog'):
	if filename.endswith('.py'):
		client.load_extension(f'cog.{filename[:-3]}')

if conf_h.is_local_run is False:
	keep_alive.keep_alive()
client.run(conf_h.TOKEN)
