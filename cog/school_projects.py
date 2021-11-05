import discord
from discord.ext import commands
import asyncio

# Importarea fisierelor
import main


# Initierea clasului
class SchoolProjects(commands.Cog):

	def __init__(self, client):
		self.client = client
		self.mylib = main.school_lib
		self.users = 'ListaElevilor'
		self.logs = 'JurnalulExecutarii'

	# Resetarea starii elevilor
	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def reset(self, ctx):
		await ctx.channel.purge(limit=1)
		self.mylib.connect()

		# Extragerea informatiei din baza de date
		last_user_id = self.mylib.last_row_id(self.users)
		elevi = self.mylib.read_rows(self.users, last_user_id)

		persoane_actualizate = 0
		embed = main.embeded(ctx, 'Actualizarea starii', f'{persoane_actualizate} persoane au fost actualizate', discord.Colour.purple())
		msg = await ctx.channel.send(embed=embed)

		# Actualizarea starii curente
		for elev in elevi:
			persoane_actualizate += 1
			embed = main.embeded(ctx, 'Actualizarea starii', f'{persoane_actualizate} persoane au fost actualizate', discord.Colour.purple())
			await msg.edit(embed=embed)

			id_elev = elev[0]
			change_list = ['Stare', 'N/A']
			self.mylib.update(self.users, id_elev, change_list)

		# Final embed message
		embed = main.embeded(ctx, 'Resetarea datelor', 'Resetarea starii elevilor a fost efectuata cu success!', discord.Colour.green())
		await msg.edit(embed=embed)

	# Randul de facut deserviciu
	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def verify(self, ctx):
		await ctx.channel.purge(limit=1)
		self.mylib.connect()
		time_error = False

		# Extragerea elevilor din baza de date
		last_user_id = self.mylib.last_row_id(self.users)

		elevi = self.mylib.read_rows(self.users, last_user_id)
		stari = []

		embed = main.embeded(ctx, 'Verificarea prezentei', '')

		msg = await ctx.channel.send(embed=embed)

		components = [[
			main.Button(style=main.ButtonStyle.green, label='Prezent'),
			main.Button(style=main.ButtonStyle.red, label='Plecat'),
			main.Button(style=main.ButtonStyle.gray, label='Absent')
		]]

		components_labels = ['Prezent', 'Plecat', 'Absent']

		# Executa un ciclu de verificarea prezentei la colegiu
		for elev in elevi:
			# Embed
			message = f'{elev[0]}. {elev[1]}'
			embed = main.embeded(ctx, 'Starea persoanei', message, discord.Colour.teal())
			await msg.edit(embed=embed, components=components)

			# Functie de verificare
			def check(the_interacted_ctx):
				return the_interacted_ctx.message.id == msg.id

			# Ciclu de schimbare a continutului
			try:
				response = await self.client.wait_for('button_click', timeout=10, check=check)
				await response.respond(type=6)
			except main.asyncio.TimeoutError:
				await msg.edit(embed=embed, components=[])
				time_error = True
				break
			else:
				if response.component.label in components_labels:
					stari.append(response.component.label)

		persoane_actualizate = 0

		# Verificare erorilor
		if time_error is False:
			# Actualizeaza datele din baza de date
			for elev in elevi:
				# Executarea printarii pe ecran a procesului
				persoane_actualizate += 1
				embed = main.embeded(ctx, 'Actualizarea starii', f'{persoane_actualizate} persoane au fost actualizate', discord.Colour.purple())
				await msg.edit(embed=embed, components=[])

				# Executarea actualizarii datelor
				id_elev = elev[0]
				change_list = ['Stare', stari[id_elev - 1]]
				self.mylib.update(self.users, id_elev, change_list)

			# Mesajul de success
			title = 'Success'
			message = 'Actualizarea datelor a fost finalizata'
			colour = discord.Colour.green()
		else:
			# Mesajul de error
			title = 'Error'
			message = 'Procesul a fost oprit din cauza inactivitatii utilizatoruliu'
			colour = discord.Colour.red()
		# Trimiterea mesajului
		embed = main.embeded(ctx, title, message, colour)
		await msg.edit(embed=embed, components=[])

	# Randul de facut deserviciu
	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def duty(self, ctx):
		await ctx.channel.purge(limit=1)
		self.mylib.connect()

		last_user_id = self.mylib.last_row_id(self.users)
		elevi = self.mylib.read_rows(self.users, last_user_id)

		finished = False
		running = True

		# Embed
		embed = main.embeded(ctx, 'Cautare', '. . .', discord.Colour.orange())
		msg = await ctx.channel.send(embed=embed)

		# Determinarea urmatoarei persoane
		for elev_t in elevi:
			elev = [elev_t[0], elev_t[1], elev_t[2], elev_t[3]]

			if elev[3] > 0:
				weight = 0
				title = ''
				message = ''
				components = ''
				log_message = ''
				while not finished:
					if running is True:
						# Persoana a fost la scoala si este prezent pentru executarea functiilor
						if elev[2] == 'Prezent':
							components = [[
								main.Button(style=main.ButtonStyle.green, label='Executare'),
								main.Button(style=main.ButtonStyle.red, label='Actualizare stare')
							]]
							weight = -1
							title = 'De serviciu'
							message = f'Persoana responsabila de ziua de azi este **{elev[1]}**'

						# Persoana a fost la scoala si a plecat fara executarea functiilor
						elif elev[2] == 'Plecat':
							components = [[
								main.Button(style=main.ButtonStyle.green, label='Executare'),
								main.Button(style=main.ButtonStyle.red, label='Actualizare stare')
							]]
							weight = 5
							title = 'De serviciu'
							message = f'Elevul **{elev[1]}** nu respecta obligatiile lui\n*I se va adauga **5p** de penalitate*\nIn total elevul a acumulat *{int(elev[3]) + weight}* puncte de penalitate'

						# Persoana nu a fost la scoala si nu este capabil de executarea functiilor
						elif elev[2] == 'Absent':
							components = [[
								main.Button(style=main.ButtonStyle.green, label='Urmatorul'),
								main.Button(style=main.ButtonStyle.red, label='Actualizare stare')
							]]
							weight = 5
							title = 'De serviciu'
							message = f'Elevul **{elev[1]}** este absent\n*Doriti sa treceti la urmatorul??*'

						# Daca persoana nu are starea acualizata
						else:
							components = [[
								main.Button(style=main.ButtonStyle.green, label='Actualizare stare'),
								main.Button(style=main.ButtonStyle.red, label='Iesire')
							]]
							weight = 5
							title = 'Caz exceptional'
							message = f'Elevul {elev[1]} nu are starea acctualizata\n Doriti sa o acctualizati?'

					# Embed
					embed = main.embeded(ctx, title, message, discord.Colour.blurple())
					await msg.edit(embed=embed, components=components)

					# Functie de verificare
					def check(the_interacted_ctx):
						return the_interacted_ctx.message.id == msg.id

					# Ciclu de schimbare a continutului
					try:
						response = await self.client.wait_for('button_click', timeout=10, check=check)
						await response.respond(type=6)
					except main.asyncio.TimeoutError:
						await msg.edit(embed=embed, components=[])
						finished = True
					else:
						# Executarea adaugarii greutatii si iesirea din program
						if response.component.label == 'Executare':
							# Drop Down
							in_process = main.SelectOption(label=f'{elev[1]}: ', value='A executat obligatiile', description='A executat obligatiile')
							off_process = main.SelectOption(label=f'{elev[1]}: ', value='Nu a executat obligatiile', description='Nu a executat obligatiile')
							activity_select = main.Select(placeholder='Alegeti starea actuala:', options=[in_process, off_process])

							await msg.edit(embed=embed, components=[activity_select])

							def check(the_event):
								return the_event.message.id == msg.id

							try:
								event = await self.client.wait_for('select_option', timeout=39, check=check)
								await event.respond(type=6)
								value = event.values[0]
							except asyncio.TimeoutError:
								finished = True
								break
							else:
								if value:
									log_message = value

							# Atribuirea datelor principale
							date_time = main.datetime.datetime.now(main.pytz.timezone("Europe/Chisinau"))
							finished = True
							value = int(elev[3]) + weight
							indexes = ['Data', 'Mesaj', 'Elevul']
							values = [date_time, log_message, elev[1]]

							# Actualizarea informatieie elevului
							self.mylib.update(self.users, elev[0], ['Rand', value])
							# Introducerea unui log in jurnal
							self.mylib.default_insert(self.logs, indexes, values)

						# Urmatoarea persoana
						elif response.component.label == 'Urmatorul':
							break

						# Utilizatorul doreste sa acctualizeze starea elevului
						elif response.component.label == 'Actualizare stare':
							running = False
							components = [[
								main.Button(style=main.ButtonStyle.green, label='Prezent'),
								main.Button(style=main.ButtonStyle.red, label='Plecat'),
								main.Button(style=main.ButtonStyle.gray, label='Absent'),
							]]
							title = 'Starea'
							message = f'Alegeti noua stare pentru persoana {elev[1]}'

						# Iesirea din program de utilizator
						elif response.component.label == 'Iesire':
							finished = True

						# Actualizarea starii elevului
						elif response.component.label == 'Prezent' or 'Plecat' or 'Absent':
							running = True
							elev[2] = response.component.label
							change_list = ['Stare', elev[2]]
							self.mylib.update(self.users, elev[0], change_list)

			# Sfarsitul ciclului
			if finished is True:
				embed = main.embeded(ctx, 'Bot respond', 'Program finalizat', discord.Colour.green())
				await msg.edit(embed=embed, components=[])
				break


def setup(client):
	client.add_cog(SchoolProjects(client))
