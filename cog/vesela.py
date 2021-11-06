import discord
import main
from discord.ext import commands


class Vesela(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.mylib = main.vesela_lib

	# Visualizarea tuturor
	@commands.command()
	@commands.has_role('Admin')
	async def tabs(self, ctx):
		self.mylib.connect()

		await ctx.channel.purge(limit=1)
		tabs = self.mylib.table_names()
		message = '|'
		for tab in tabs:
			message += f' {tab} |'

		# Embed
		embed = discord.Embed(title='Tabelele existente in baza de date', description=message, colour=discord.Colour.blurple())
		await ctx.send(embed=embed)

	# Adaugarea in baza de date vesela spalata
	@commands.command(aliases=['ve', 'v'])
	@commands.has_role('Admin')
	async def vesela(self, ctx, comment=None, status=None):
		self.mylib.connect()

		await ctx.channel.purge(limit=1)
		name = f'{ctx.author.name}#{ctx.author.discriminator}'
		table = 'Vesela'
		date_time = main.datetime.datetime.now(main.pytz.timezone("Europe/Chisinau"))

		stats = self.mylib.read_rows('TipuriDeStari', self.mylib.last_row_id('TipuriDeStari'))
		statuses = []
		for stat in stats:
			statuses.append(stat[1])

		# Getting the right values
		if status is None:
			status = statuses[0]

		if status == 'run':
			status = statuses[0]

		elif status == 'end':
			status = statuses[1]

		elif status is None:
			status = statuses[0]

		if comment == 'run':
			status = statuses[0]
			comment = None

		elif comment == 'end':
			status = statuses[1]
			comment = None

		# Cannot do
		if status not in statuses:
			# Embed
			embed = main.embeded(ctx, 'Nu poate fi executat!', 'Statutul introdus este incorect', discord.Colour.red())
			await ctx.send(embed=embed)

		# Cannot do
		if self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0][4] == statuses[0] and name != \
			self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0][1]:

			# Embed
			embed = main.embeded(ctx, 'Nu poate fi executat!', f'Salut {ctx.author.mention}, ultima cerere la baza de date este `{statuses[0]}`', discord.Colour.red())
			await ctx.send(embed=embed)

		# Update information
		elif self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0][4] == statuses[0] and name == \
			self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0][1]:

			# Last row information
			row = self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0]

			# No comment in data base and no comment from user
			if row[3] is None and (comment == '' or comment is None):

				# Embed
				embed = main.embeded(ctx, 'Nu poate fi executat!', f'Comentariul trebuie sa contina informatie', discord.Colour.red())
				await ctx.send(embed=embed)

			# Existing comment in data base but no comment from user
			elif row[3] is not None and comment is None:
				self.mylib.update(table, self.mylib.last_row_id(table), ['Statutul', status])

			# Everything fine
			else:
				self.mylib.update(table, self.mylib.last_row_id(table), ['Comentariul', comment])
				self.mylib.update(table, self.mylib.last_row_id(table), ['Statutul', status])

			# Getting latest information about last row
			row = self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0]

			# Embed
			value_list = [['Id', row[0], False], ['Numele', row[1], True], ['DataSiOra', row[2], True], ['Comentariul', row[3], True], ['Statutul', row[4], True]]
			embed = main.embeded(ctx, 'Success', f'Salut {ctx.author.mention}, informatia a fost actualizata', discord.Colour.green(), value_list)
			await ctx.send(embed=embed)

		# Can do
		elif self.mylib.read_rows(table, self.mylib.last_row_id(table), self.mylib.last_row_id(table))[0][4] == statuses[1] and name in self.mylib.get_users():
			self.mylib.insert(table, name, ['Numele', 'DataSiOra', 'Comentariul', 'Statutul'], [name, date_time, comment, status])

			# Embed
			value_list = [['Id', self.mylib.last_row_id('Vesela'), False], ['Numele', name, True], ['DataSiOra', date_time, True], ['Comentariul', comment, True],
				['Statutul', status, True]]
			embed = main.embeded(ctx, 'Success', f'Salut {ctx.author.mention}, a fost adaugat un rand nou', discord.Colour.green(), value_list)
			await ctx.send(embed=embed)

		# Unknown error
		else:
			# Embed
			embed = main.embeded(ctx, 'Erroare', 'Erroare necunoscuta in legatura cu inserarea datelor', discord.Colour.red())
			await ctx.send(embed=embed)

	# Get all rows from a table
	@commands.command(aliases=['rt'])
	@commands.has_role('Admin')
	async def read_table(self, ctx, table):
		self.mylib.connect()

		await ctx.channel.purge(limit=1)
		rows = self.mylib.read_rows(table, self.mylib.last_row_id(table))
		message = []

		for row in rows:
			message.append([f'{row[0]}', f'{row[1]} | {row[2]} | {row[3]} | {row[4]}', False])

		# Embed
		embed = main.embeded(ctx, f'{table}', 'Datele din tabel', discord.Colour.blue(), message)
		await ctx.send(embed=embed)

	# Nexts turn
	@commands.command(aliases=['vu'])
	@commands.has_role('Admin')
	async def vesela_urmatorul(self, ctx, table='Vesela'):
		self.mylib.connect()
		await ctx.channel.purge(limit=1)

		rows = self.mylib.read_rows(table, self.mylib.last_row_id(table))
		users = []
		users_count = []

		# Calcularea parametrilor principali
		for row in rows:
			if row[1] not in users:
				users.append(row[1])

		for user in users:
			users_count.append(self.mylib.count_times(table, user))

		# Sortarea datelor
		sorted_count = []
		sorted_data = []
		for user in users:
			index = users.index(user)
			if len(sorted_count) == 0:
				sorted_count.append(users_count[index])
				sorted_data.append([user])

			elif users_count[index] < sorted_count[0]:
				sorted_count.insert(0, users_count[index])
				sorted_data.insert(0, [user])

			elif users_count[index] > sorted_count[-1]:
				sorted_count.append(users_count[index])
				sorted_data.append([user])

			elif users_count[index] in sorted_count:
				sorted_data[sorted_count.index(users_count[index])].append(user)

			else:
				i = 0
				while i < len(sorted_count):
					if users_count[index] < sorted_count[i]:
						sorted_data.insert(i, [user])
						sorted_count.insert(i, users_count[index])
						break
					i += 1

		listed = []
		index = 0
		while index < len(users):
			listed.append([users[index], users_count[index], True])
			index += 1
		# Returnarea datelor

		# Embed
		embed = main.embeded(ctx, f'Urmatoarea persoana', f'Urmatorul este {sorted_data}\n{sorted_count}', discord.Colour.blue(), listed)
		await ctx.send(embed=embed)


def setup(client):
	client.add_cog(Vesela(client))
