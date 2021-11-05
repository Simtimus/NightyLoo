import discord
from discord.ext import commands
import asyncio

# Importarea fisierelor
import main


# Initierea clasului
class Common(commands.Cog):

	def __init__(self, client):
		self.client = client

	# Chat clear command
	@commands.command(aliases=['purge', 'clean', 'cls'])
	@commands.has_permissions(kick_members=True)
	async def clear(self, ctx, amount=2):
		await ctx.channel.purge(limit=amount)

	# Drop down select
	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def drop(self, ctx):
		so_listen = main.SelectOption(label='Asculta pe ', value='Aculta', description='Aici este ceea ce asculta')
		activity_select = main.Select(placeholder='Alegeti tipul de acivitate:', options=[so_listen])

		the_bot_msg = await ctx.channel.send(content='Hey yooo hello', components=[activity_select])

		def check(the_event):
			return the_event.message.id == the_bot_msg.id

		try:
			event = await self.client.wait_for('select_option', timeout=39, check=check)
			await event.respond(type=6)
			value = event.values[0]
		except asyncio.TimeoutError:
			await the_bot_msg.delete()
			await ctx.message.delete()
			return
		else:
			if value == so_listen.value:
				pass

	# Create a embed message
	@commands.command(aliases=['ann'])
	@commands.has_permissions(kick_members=True)
	async def announcement(self, ctx, arguments):
		await ctx.channel.purge(limit=1)

		# Sorts the input information into a dictionary
		options = {}

		for argument in arguments.split(';'):
			try:
				key, value = argument.split('::')
			except (IOError, TypeError, ValueError):
				continue
			options[key] = value

		exception_message = ''

		# Getting the embed options
		title = options.get('t')
		description = options.get('d')
		colour = options.get('c')

		embed_options = {}

		# If the title and description fields are missing
		if title is None and description is None:
			# Embed
			exception_message += 'Title and Description fields are missing\nYou must have at least one field in your embed!'
			exception_embed = main.embeded(ctx, ':x: Exception', exception_message, discord.Colour.red())
			await ctx.author.send(embed=exception_embed)
			return

		# If everything is ok
		else:
			if title is not None:
				embed_options['title'] = title

			if description is not None:
				embed_options['description'] = description

			if colour is not None:
				embed_options['colour'] = int(colour, 16)

			# Setting up the embed options
			embed = discord.Embed(**embed_options)

			# Getting the additional embed elements
			author = options.get('a')
			thumbnail = options.get('tn')
			image = options.get('i')
			footer = options.get('f')

			# Setting up the additional embed elements
			if author is not None:
				user = self.client.get_user(int(author))
				embed.set_author(name=user.name, icon_url=user.avatar_url)

			if thumbnail is not None:
				embed.set_thumbnail(url=thumbnail)

			if image is not None:
				embed.set_image(url=image)

			if footer is not None:
				embed.set_footer(text=footer)

			# Sending final embed
			await ctx.channel.send(embed=embed)

	# Embed example
	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def emb(self, ctx, member: discord.Member):
		await ctx.channel.purge(limit=1)
		embed = discord.Embed(
			title=member.name,
			description=member.mention,
			colour=discord.Colour.green()
		)
		embed.set_author(name=ctx.author.name, icon_url=member.avatar_url)
		embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author.name}")
		embed.set_image(url=member.avatar_url)
		embed.set_thumbnail(url=member.avatar_url)
		embed.add_field(name="Id", value=member.id, inline=False)
		embed.add_field(name="Id", value=member.id, inline=False)
		embed.add_field(name="Id", value=member.id, inline=True)
		embed.add_field(name="Id", value=member.id, inline=True)
		embed.add_field(name="Id", value=member.id, inline=False)
		embed.add_field(name="Id", value=member.id, inline=True)

		await ctx.send(embed=embed)


def setup(client):
	client.add_cog(Common(client))
