import main
import discord
import datetime
from discord.ext import commands

# Importarea fisierelor
import lessons_config as conf


# Initierea clasului
class Lessons(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.database = main.vesela_lib

	# //////////////////////
	@staticmethod
	def calcularea_timpului(valoare: str, arg: int = 3) -> [int, [int, int]]:
		inceput, sfarsit = valoare.split(' - ')
		ora_i, min_i = inceput.split(':')
		ora_i = int(ora_i)
		min_i = int(min_i)
		ora_s, min_s = sfarsit.split(':')
		ora_s = int(ora_s)
		min_s = int(min_s)
		timp_i = ora_i * 60 + min_i
		timp_s = ora_s * 60 + min_s
		if arg == 1:
			return timp_i
		elif arg == 2:
			return timp_s
		else:
			return timp_i, timp_s

	def multifunctional(self, arg: int) -> [int, int, str]:
		lectia = 0
		ramas = 0
		verify = 'pauza'
		for i in range(4):
			timp_x, timp_y = self.calcularea_timpului(conf.orarul[arg][i])
			if (main.timpul >= timp_x) and (main.timpul <= timp_y):
				lectia = i
				ramas = timp_y - main.timpul
				verify = 'lectie'

			elif timp_y <= main.timpul <= timp_y + 10:
				lectia = i
				ramas = timp_y - main.timpul
				verify = 'pauza'
				return lectia, ramas, verify
		return lectia, ramas, verify

	def printable(self, saptamana, ziua, lectia, verify, ramas) -> str:
		signature = ''
		message = f'Saptamana: {saptamana} | ziua: {ziua}\n'

		for element in conf.time_table[main.saptamana][main.ziua_saptamanii]:
			object_index = conf.time_table[main.saptamana][main.ziua_saptamanii].index(element)
			valoare = conf.orarul[0][object_index]
			inceput, sfarsit = valoare.split(' - ')
			if verify == 'lectie':
				signature = f'Lectie, a ramas *{ramas // 60}:{ramas % 60}*'
			elif verify == 'pauza':
				timp_x, timp_y = self.calcularea_timpului(
					conf.orarul[0][lectia + 1 if lectia < 3 else 3])
				signature = f'Pauza, a ramas *{timp_x - main.timpul} minute*'

			if object_index == lectia:
				message += f'**{object_index + 1}. {element}** - {signature}\n **{inceput} - {sfarsit}**\n'
			else:
				message += f'{object_index + 1}. {element}\n{inceput} - {sfarsit}\n'
		return message

	@staticmethod
	def schedule_format(saptamana: str, ziua: str) -> str:
		message = f'Saptamana: {saptamana} | ziua: {ziua}\n'
		for element in conf.time_table[saptamana][ziua]:
			message += f'{conf.time_table[saptamana][ziua].index(element) + 1}. {element}\n'
		return message

	# //////////////////////

	# Paritatea saptamanii
	@commands.command()
	async def week(self, ctx, arg: str = 'now'):
		await ctx.channel.purge(limit=1)

		if arg == 'now':
			saptamana = main.saptamana
			text = 'actuala'

		elif arg == 'next':
			saptamana = main.saptamana_v
			text = 'viitoare'

		else:
			return

		message = f'Saptamana: {saptamana}'

		# Embed
		embed = main.embeded(ctx, f"Saptamana {text}", message, discord.Colour.blue())
		await ctx.send(embed=embed)

	# Orarul lectiilor
	@commands.command()
	async def orar(self, ctx):
		await ctx.channel.purge(limit=1)

		# Componente
		components = [[
			main.Button(style=main.ButtonStyle.green, label="Lun", id='Luni'),
			main.Button(style=main.ButtonStyle.green, label="Mar", id='Marti'),
			main.Button(style=main.ButtonStyle.green, label="Mie", id='Miercuri'),
			main.Button(style=main.ButtonStyle.green, label="Joi", id='Joi'),
			main.Button(style=main.ButtonStyle.green, label="Vin", id='Vineri'),
		], [
			main.Button(style=main.ButtonStyle.gray, label="Impar", id='Impara'),
			main.Button(style=main.ButtonStyle.gray, label="Par", id='Para')
		]]

		# Valorile default
		saptamana = 'Impara'
		ziua = conf.zilele[0]

		message = self.schedule_format(saptamana, ziua)

		embed = main.embeded(ctx, 'Orar', message, discord.Colour.teal())
		msg = await ctx.channel.send(embed=embed, components=components)

		def check(the_interacted_ctx):
			return the_interacted_ctx.message.id == msg.id

		# Ciclu de schimbare a continutului
		while True:
			try:
				response = await self.client.wait_for('button_click', timeout=10, check=check)
				await response.respond(type=6)
			except main.asyncio.TimeoutError:
				await msg.edit(embed=embed, components=[])
				break
			else:
				if response.component.id == 'Impara' or response.component.id == 'Para':
					saptamana = response.component.id
				elif response.component.id in conf.zilele:
					ziua = response.component.id

				message = self.schedule_format(saptamana, ziua)

				embed = main.embeded(ctx, 'Orar', message, discord.Colour.teal())
				await msg.edit(embed=embed, components=components)

	# Lectia curenta
	@commands.command()
	async def lesson(self, ctx):

		numarul_orelor = len(conf.time_table[main.saptamana][main.ziua_saptamanii])
		before_begin = self.calcularea_timpului(conf.orarul[0][0], 1)
		first_half = self.calcularea_timpului(conf.orarul[0][numarul_orelor - 1], 2)
		second_half = self.calcularea_timpului(conf.orarul[1][-1], 2)

		timpul = main.timpul
		current_date = main.current_date
		day = main.day

		# Embed
		await ctx.channel.purge(limit=1)
		message = ":x: If you see this message, it's probably from an error\nPlease report it!!"
		embed = main.embeded(ctx, "Auto respond", message, discord.Colour.red())
		msg = await ctx.send(embed=embed)

		i = 0
		anima = 0
		first_lesson = None
		if 0 <= main.current_date <= 4:
			for i in range(4):
				if conf.time_table[main.saptamana][main.ziua_saptamanii][i] != 'N/A':
					first_lesson = conf.time_table[main.saptamana][main.ziua_saptamanii][i]
					break

		# definirea variabilelor necesare
		if 0 <= timpul <= first_half:
			anima = 0
		elif first_half <= timpul <= second_half:
			anima = 1
		lectia, ramas, verify = self.multifunctional(anima)

		# Text inainte de inceputul orelor
		if 0 <= current_date <= 4 and timpul <= before_begin:

			# Embed
			message = f'La ora {day.ctime()} nu sunt lectii\nLectia {first_lesson} se va incepe peste {self.calcularea_timpului(conf.orarul[0][i], 1) - timpul} minute'
			embed = main.embeded(ctx, "Inceputul orelor", message, 0xFFFF00)
			await msg.edit(embed=embed)

		# Text in decursul orelor
		elif 0 <= current_date <= 4 and timpul <= first_half:

			message = self.printable(main.saptamana, main.ziua_saptamanii, lectia, verify, ramas)
			# Embed
			embed = main.embeded(ctx, "In decursul orelor", message, discord.Colour.green())
			await msg.edit(embed=embed)

		# Text dupa sfarsitul orelor
		elif 0 <= current_date < 4 and timpul >= first_half:
			ziua_saptamanii_v = conf.zilele[(current_date + 1 if current_date != 4 else current_date)]

			message = self.schedule_format(main.saptamana, ziua_saptamanii_v)

			# Embed
			embed = main.embeded(ctx, "Sfarsitul orelor", message, 0x00FFFF)
			await msg.edit(embed=embed)

		# Text in zilele de odihna
		elif (5 <= current_date <= 6) or (current_date == 4 and timpul >= first_half):

			message = self.schedule_format(main.saptamana_v, conf.zilele[0])

			# Embed
			embed = main.embeded(ctx, "Zi de odihna", message, discord.Colour.light_grey())
			await msg.edit(embed=embed)

	# Schimbarea orarului
	@commands.command(aliases=['edo'])
	@commands.has_role('Admin')
	async def editare_date_orar(self, ctx, args: str = ''):
		await ctx.channel.purge(limit=1)
		durata_lectiei = 0
		durata_pauzei = 0
		durata_pauzei_mare = 0
		overwrite = ''
		de_la = datetime.date.today()
		pana_la = datetime.date.today()
		starea = 'custom'
		settings = args.split(';')

		name = ''
		value = ''
		for setting in settings:
			if setting != '':
				name, value = setting.split(':')

			if name == 'l':
				durata_lectiei = int(value)
			elif name == 'p':
				durata_pauzei = int(value)
			elif name == 'pm':
				durata_pauzei_mare = int(value)
			elif name == 'ov':
				pause_index, pause_value = value.split('!')
				overwrite += f'{pause_index}:{pause_value};'
			elif name == 'dl':
				dd, mm, yy = value.split('.')
				de_la = datetime.date(day=int(dd), month=int(mm), year=int(yy))
			elif name == 'pl':
				dd, mm, yy = value.split('.')
				pana_la = datetime.date(day=int(dd), month=int(mm), year=int(yy))
			elif name == 'st':
				starea = value

		if starea == 'default':
			setting_id = 1
		else:
			setting_id = 2

		# Updating
		keys = ['DurataLectiei', 'DurataPauzei', 'DurataPauzeiMare', 'overwrite', 'DeLa', 'PanaLa', 'Starea']
		values = [durata_lectiei, durata_pauzei, durata_pauzei_mare, overwrite, de_la, pana_la, starea]

		self.database.connect()
		self.database.multiple_update('OrarulSunetelor', setting_id, keys, values)

		message = f'''Orarul a fost adaugat, incurand se vor actualiza datele\n
			El va fi aplicat in functiune de pe data de *{de_la}*, modul de functionare *{starea}*'''
		# Embed
		embed = main.embeded(ctx, "Success", message, discord.Colour.green())
		await ctx.channel.send(embed=embed)


def setup(client):
	client.add_cog(Lessons(client))
