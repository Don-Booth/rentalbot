import discord
import os, sys
import json, pickle
import time
from datetime import timedelta
from datetime import date
from discord.ext import commands

MAX_DURATION_S = 60 * 60 * 6  # Number of seconds in 6 hours, default
timer_list = {}
hiscore = None
token = None
shadow_timer = 0
client = commands.Bot(command_prefix='>', description='Custom Bot for OVR')
versiontype = 'Production'
versionnumber = '1.0'

class Timer:
	def __init__(self):
		self.start_time = time.time()
		self.pause_time = None
		self.resume_time = None
		self.stalled_time = 0

	def pause(self):
		self.pause_time = time.time()
		self.resume_time = None

	def resume(self):
		self.resume_time = time.time()
		self.stalled_time += self.resume_time - self.pause_time
		self.pause_time = None

	def get_elapsed_time(self):
		now = time.time()

		if self.pause_time is not None:
			elapsed_since_pause = now - self.pause_time
			elapsed_time = now - self.start_time - elapsed_since_pause - self.stalled_time
		elif self.resume_time is not None:
			elapsed_time = now - self.start_time - self.stalled_time
		else:
			elapsed_time = now - self.start_time

		return int(elapsed_time)

def read_config(config_path):
	global token
	try:
		with open(config_path, 'r') as jf:
			data = jf.read()
			config = json.loads(data)
	except FileNotFoundError:
		print('Couldn\'t open config file, working dir is', os.getcwd())
		print('List of files in working dir:\n\t', '\n\t'.join(os.listdir(os.getcwd())))
		exit(1)
	token = config['token']

def load_saved_timers():
	global timer_list
	try:
		with open('timers.json', 'rb') as tf:
			timer_list = pickle.load(tf)
			for key in timer_list.keys():
				if time.time() - timer_list[key].start_time > MAX_DURATION_S:
					del timer_list[key]
	except:
		pass

def save_timers():
	with open('timers.json', 'wb') as tf:
		pickle.dump(timer_list, tf)

def load_hiscore():
	global hiscore
	try:
		with open('hiscore.json', 'r') as jf:
			data = jf.read()
			hiscore = json.loads(data)
	except FileNotFoundError:
		print('Couldn\'t open hiscore file, working dir is', os.getcwd())
		print('List of files in working dir:\n\t', '\n\t'.join(os.listdir(os.getcwd())))
		exit(1)

def save_hiscore():
	global hiscore
	try:
		with open('hiscore.json', 'w') as jf:
			json.dump(hiscore, jf)
	except FileNotFoundError:
		print('Couldn\'t open hiscore file, working dir is', os.getcwd())
		print('List of files in working dir:\n\t', '\n\t'.join(os.listdir(os.getcwd())))
		exit(1)


@client.event
async def on_ready():
	print('~Logged in~')
	print(client.user.name)
	print(client.user.id)
	print('~~~~~~~~~~~')

@client.event
async def on_message(message):
	global shadow_timer
	global hiscore

	messageContent = message.content.strip()

	if (message.channel.name == "gen-pop" and len(messageContent) > 0):
		if (len(messageContent) == 32 and "<:WNUFShadow:" in messageContent and message.author.name != "RentalBot"):
			shadow_timer += 1
			print('Shadow Chain at {0}'.format(shadow_timer))
		else:
			if (shadow_timer > 0):
				shadow_temp = shadow_timer
				shadow_timer = 0
				if (shadow_temp > 1):
					print ('Shadow chain broken at {0} Shadows'.format(shadow_temp))
					await message.channel.send('Shadow chain **broken** at **{0} Shadows** by **{1}**'.format(shadow_temp, message.author.name))
					await message.channel.send('**THANKS A LOT {0}**'.format(message.author.name))
					await message.channel.send('<:WNUFShadow:767133320345157652>')
				if (shadow_temp > int(hiscore['hiscore'])):
					await message.channel.send('**A new Shadow chain hiscore has been registered**')
					hiscore['hiscore'] = shadow_temp
					hiscore['hiscore_date'] = str(date.today())
					save_hiscore()

	await client.process_commands(message)

@client.command(name='getemoji')
async def get_emoji(ctx, emoji: discord.Emoji): 
		embedVar = discord.Embed(title="Emoji Information", description="", color=0x00ff00)
		embedVar.set_image(url="{0}".format(emoji.url))
		embedVar.add_field(name="Name", value="{0}".format(emoji.name), inline=False)
		embedVar.add_field(name="ID", value="{0}".format(emoji.id), inline=False)
		embedVar.add_field(name="Available", value="{0}".format(emoji.available), inline=False)
		embedVar.add_field(name="Animated", value="{0}".format(emoji.animated), inline=False)
		embedVar.add_field(name="Created At", value="{0}".format(emoji.created_at), inline=False)
		await ctx.send(embed=embedVar)

@client.command(name='version')
async def version(ctx):
	global versiontype
	global versionnumber

	embedVar = discord.Embed(title="RentalBot Information", description="", color=0x00ff00)
	embedVar.add_field(name="Version Type", value="{0}".format(versiontype), inline=False)
	embedVar.add_field(name="Version Number", value="{0}".format(versionnumber), inline=False)
	await ctx.send(embed=embedVar)

@client.command()
async def avatar(ctx, *,  avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    await ctx.send(userAvatarUrl)

@client.command()
async def servericon(ctx):
	await ctx.send(ctx.guild.icon_url)

@client.command(name='start')
async def start_timer(ctx, name):
	if name:
		global timer_list
		if name in timer_list:
			await ctx.send('Timer already exists')
			return
		timer_list[name] = Timer()
		await ctx.send('Timer {} started'.format(name))
		save_timers()
	else:
		await ctx.send('Please supply a timer name eg ~start timer1')

@client.command(name='pause')
async def pause_timer(ctx, name):
	if name:
		global timer_list
		if name not in timer_list:
			await ctx.send('Timer not started - start a timer with the `start` command')
		elapsed_time = timer_list[name].get_elapsed_time()
		await ctx.send('Pausing timer {} at {}'.format(name, str(timedelta(seconds=elapsed_time))))
		timer_list[name].pause()
	else:
		await ctx.send('Please supply a timer name eg ~pause timer1')

@client.command(name='resume')
async def resume_timer(ctx, name):
	if name:
		global timer_list
		if name not in timer_list:
			await ctx.send('Timer not started - start a timer with the `start` command')
		elapsed_time = timer_list[name].get_elapsed_time()
		await ctx.send('Resuming timer {} at {}'.format(name, str(timedelta(seconds=elapsed_time))))
		timer_list[name].resume()
	else:
		await ctx.send('Please supply a timer name eg ~resume timer1')

@client.command(name='check')
async def check_timer(ctx, name):
	if name:
		global timer_list
		if name not in timer_list:
			await ctx.send('Timer not started - start a timer with the `start` command')
		else:
			
			elapsed_time = timer_list[name].get_elapsed_time()

			if elapsed_time >= MAX_DURATION_S:
				await ctx.send('Timer expired, start a new timer')
				del timer_list[name]
				return
			await ctx.send('Current elapsed for {}: {}'.format(name, str(timedelta(seconds=elapsed_time))))
	else:
		await ctx.send('Please supply a timer name eg ~check timer1')			

@client.command(name='stop')
async def end_timer(ctx, name):
	if name:
		global timer_list
		if name not in timer_list:
			await ctx.send('Timer cannot be stopped as it has not been started')
		else:

			elapsed_time = timer_list[name].get_elapsed_time()

			del timer_list[name]
			if elapsed_time >= MAX_DURATION_S:
				await ctx.send('Timer was open for longer than max duration')
				return
			await ctx.send('Timer {} stopped after {} elapsed'.format(name, str(timedelta(seconds=elapsed_time))))
	else:
		await ctx.send('Please supply a timer name eg ~stop timer1')		

@client.command(name='list')
async def list_timers(ctx):
	global timer_list
	await ctx.send('Timer list')
	for key in timer_list.keys():
		await ctx.send(key)


@client.command(name='max')
async def maxtime(ctx, *new_max):
	global MAX_DURATION_S
	new_max = eval(''.join(new_max))
	if new_max <= 60 or new_max > (60 * 60 * 24):
		await ctx.send('Sorry! Duration must be greater than 1 minute and less than 1 day')
		return
	MAX_DURATION_S = new_max
	await ctx.send('Got it! The new maximum duration for a timer is {}'.format(str(timedelta(seconds=new_max))))

@client.command(name='countdown')
async def countdown(ctx):
	# lock down the channel so nobody can type in it
	await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
	await ctx.send('Channel locked down - SHOW COUNTDOWN IMMINENT!')
	time.sleep(10)

	# count down
	await ctx.send('Countdown commencing in 5 seconds')
	time.sleep(5)

	for x in reversed(range(1,11)):
		await ctx.send(x)
		time.sleep(1)

	# start timer
	global timer_list
	name = 'timer'
	
	if name in timer_list:
		del timer_list[name]
	
	timer_list[name] = Timer()
	await ctx.send('Timer {} started - GO GO GO!'.format(name))
	save_timers()

	# release the channel after the fact
	await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
	await ctx.send('Channel unlocked')

@client.command(name='hiscore')
async def hiscore(ctx):
	global hiscore
	score = hiscore['hiscore']
	score_date = hiscore['hiscore_date']
	await ctx.send('Shadow chain hiscore was {} on {}'.format(score, score_date))

@client.command(name='info')
async def info(ctx):
	await ctx.send('This bot accepts the following commands:')
	await ctx.send('start stop pause resume check countdown hiscore')
	await ctx.send('each command must be supplied with a timer name or it won''t work.  eg - ~start timer1')

if __name__ == '__main__':
	if len(sys.argv) > 2:
		config_name = sys.argv[2]
	else:
		config_name = 'config.json'
	read_config(config_name)
	load_saved_timers()
	load_hiscore()
	client.run(token)
