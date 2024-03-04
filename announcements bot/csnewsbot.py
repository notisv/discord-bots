# made by github.com/notisv
# discord bot that posts the latest announcements from www.cs.uoi.gr/nea/

import requests
from bs4 import BeautifulSoup
import pyshorteners
import time
import pickle
import discord
from discord.ext import tasks

#################################################
#                   BOT BRAIN                   #
#################################################

url = 'https://www.cs.uoi.gr/nea/'

# initialize previous announcements
previous_announcements = []

# save the bots previous messages
previous_announcement_messages = []

# we want to keep the previous announcements and messages in persistent storage
# and be able to load them if the program crashes or stops

# try to load from persistent storage
try:
    with open('previous_announcements', 'rb') as previous_announcements_file:
        print('previous_announcements file found! Loading previous announcements...')
        previous_announcements = pickle.load(previous_announcements_file)            

# this exception should only be raised the first time the python program is ran
except FileNotFoundError as e:
    print('previous_announcements file not found. Creating one.')
    with open('previous_announcements', 'wb') as previous_announcements_file:
        pickle.dump(previous_announcements, previous_announcements_file)

try:
    with open('previous_announcement_messages', 'rb') as previous_announcement_messages_file:
        print('previous_announcement_messages file found! Loading previous messages...')
        previous_announcement_messages = pickle.load(previous_announcement_messages_file)

# this exception should only be raised the first time the python program is ran
except FileNotFoundError as e:
    print('previous_announcement_messages file not found. Creating one.')
    with open('previous_announcement_messages', 'wb') as previous_announcement_messages_file:
        pickle.dump(previous_announcement_messages, previous_announcement_messages_file)

# grab the latest announcements
def getLatestAnnouncements(url):
    # exception handler in case the webpage does not respond or there is a network issue
    try:
        # open webpage with get method
        page = requests.get(url)

        # http_response between 200-400 means OK status
        if (page.status_code == 200):
            #print('Successfully opened: ' + url)

            # we need a parser, Python built-in HTML parser is enough
            soup = BeautifulSoup(page.text, 'html.parser')

            # exception handler in case there is an IndexError
            # if there is an IndexError this means the page changed the way it displays the announcements
            try:
                # each announcement has a date
                date_soup = soup.find_all("time", {"datetime": "2008-02-14 20:00"})
                date_list = []
                for dateElement in date_soup:
                    date = str(dateElement.get_text().replace('\r', '').replace('\n', '').replace('\t', '').replace(',', ', ')).strip()
                    #print(date)
                    date_list.append(date)
                #print(date_list)
                
                # each announcement has the h6 tag
                announcement_soup = soup.find_all('h6')

                # put the announcements in a list
                announcementElementList = []
                for announcementElement in announcement_soup:
                    announcementElementList.append(announcementElement.find('a'))
                #print(elementList)

                announcementList = []
                '''
                for announcementElement in announcementElementList[1:]:
                    announcement = (str(announcementElement.get_text()), str(announcementElement['href']))
                    announcementList.append(announcement)
                '''

                for announcementElement, dateElement in zip (announcementElementList[1:], date_list):
                    announcement = (dateElement, str(announcementElement.get_text()), str(announcementElement['href']))
                    announcementList.append(announcement)

                #print('Printing announcementList'); print(announcementList)
                return announcementList

            except IndexError as e:
                #print('Index Error...')
                return 'error'

        else:
            #print('Webpage unreachable...')
            return 'error'

    except requests.exceptions.RequestException as e:
        #print('Webpage unreachable...')
        return 'error'

#################################################
#                  DISCORD BOT                  #
#################################################

bot_version = 'v3.0'

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents = intents)
TOKEN = '<insert-token-here>' # secret token

bot_moderator_id = 760974440229634050 # janitor ID
admin_id = 988013663812190238 # steward id
uptime_before = time.monotonic()

# channel to post the announcements on
def get_anakoinwseis_channel():
    anakoinwseis_channel = client.get_channel(993483840158973992) # anakoinwseis text channel
    #anakoinwseis_channel = client.get_channel(988092694242947112) # admin_only text channel
    return anakoinwseis_channel

@client.event
async def on_connect():
    print('Successfully logged in as {0.user}.'.format(client))

@client.event
async def on_disconnect():
    print('CS Announcements bot disconnected.')

@client.event
async def on_ready():
    print('CS Announcements bot ready.')
    # set 'Watching' status
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "cs.uoi.gr/nea"))

@tasks.loop(minutes = 60)
async def postAnnouncements():

    # get the latest announcements
    latest_announcements = getLatestAnnouncements(url)
    #print(latest_announcements)

    # load previous announcements from persistent storage
    with open('previous_announcements', 'rb') as previous_announcements_file:
        previous_announcements = pickle.load(previous_announcements_file)

    # load previous messages from persistent storage
    with open('previous_announcement_messages', 'rb') as previous_announcement_messages_file:
        previous_announcement_messages = pickle.load(previous_announcement_messages_file)

    if not(latest_announcements == 'error'):
        temp_announcements = []
        # we want to print the announcements in reverse order (latest announcement is posted last)
        for announcement in reversed(latest_announcements):
            if announcement not in previous_announcements:
                announcement_date = announcement[0]
                announcement_text = announcement[1]
                announcement_link = announcement[2]

                #print(previous_announcements + '\n')
                #print(latest_announcements + '\n')
                #print(announcement + '\n')
                announcement = (announcement_date, announcement_text, announcement_link)
                temp_announcements.append(announcement)
                #print('Printing temp_announcements'); print(temp_announcements)

                # shorten the long url using tinyURL
                url_shortener = pyshorteners.Shortener() 
                short_announcement_link = url_shortener.tinyurl.short(announcement_link)

                announcement_date_in_bold = '**' + announcement_date + '**'

                discord_message = announcement_date_in_bold + ' - ' + announcement_text + ' ' + short_announcement_link 

                # make the bot post the announcement only if the message is NOT in previous_messages
                if discord_message in previous_announcement_messages:
                    print ('Diplotipi anakoinwsi detected. Not posting...')
                else:
                    await get_anakoinwseis_channel().send(discord_message)
                    print ('New announcement: ' + discord_message)
                    previous_announcement_messages.append(discord_message)

            else:
                print('Announcement already in memory')

        #print('Printing previous announcements before adding new ones'); print(previous_announcements)
        # if there were any new announcements, meaning len(temp_announcements != 0) then add them to the previous ones
        if temp_announcements:
            previous_announcements = previous_announcements[len(temp_announcements):] + temp_announcements

            # keep the new announcements in persistent storage
            with open('previous_announcements', 'wb') as previous_announcements_file:
                pickle.dump(previous_announcements, previous_announcements_file)

            # keep the new messages in persistent storage
            with open('previous_announcement_messages', 'wb') as previous_announcement_messages_file:
                pickle.dump(previous_announcement_messages, previous_announcement_messages_file)

        #print('Printing previous announcements after adding new ones'); print(previous_announcements)

    else:
        print('Error getting the latest announcements.')

@postAnnouncements.before_loop
async def before():
    #print('Waiting...')
    await client.wait_until_ready()

@client.event
async def on_message(message):
    
    # dont respond to the bots own messages
    if message.author == client.user:
        return

    # commands accepted only from bot moderators and admins
    moderator_admin_issued_command = False
    if bot_moderator_id in [y.id for y in message.author.roles] or admin_id in [y.id for y in message.author.roles]:
        moderator_admin_issued_command = True

    if moderator_admin_issued_command:
        # help command
        if message.content == '$help':
            print('Executing $help')
            await message.delete()
            output_message = ''
            output_message += '`CS Announcements Bot ' + bot_version + '`\n'
            output_message += '`Commands:`\n'
            output_message += '`$status - Shows bot status`\n'
            output_message += '`$ping - Pings the bot`\n'
            output_message += '`$start - Starts the announcement posting`\n'
            output_message += '`$stop - Stops the announcement posting`\n'
            output_message += '`$restart - Restarts the bot`\n'
            output_message += '`$turnoff - Makes the bot turn off and log out`\n'
            output_message += '`$showmem - Shows the announcements on memory`\n'
            output_message += '`$updatemem - Updates the announcements on memory`\n'
            output_message += '`$uptime - Displays the bot uptime`\n'      
            await message.channel.send(output_message)

        # status command
        if message.content == '$status':
            print('Executing $status')
            await message.delete()
            if postAnnouncements.is_running():
                await message.channel.send('Announcement posting is ON')
            else:
                await message.channel.send('Announcement posting is OFF')

        # ping command
        if message.content == '$ping':
            print('Executing $ping')
            await message.delete()
            before = time.monotonic()
            message = await message.channel.send(':ping_pong: Pong! Latency:')
            ping = (time.monotonic() - before) * 1000
            await message.edit(content = f':ping_pong: Pong! Latency: `{int(ping)}ms`')

        # start command
        if message.content == '$start':
            print('Executing $start')
            await message.delete()
            if postAnnouncements.is_running():
                await message.channel.send('Announcement posting is already ON')
            else:
                await message.channel.send('I will start posting announcements.')
                postAnnouncements.start()

        # stop command
        if message.content == '$stop':
            print('Executing $stop')
            await message.delete()
            if not(postAnnouncements.is_running()):
                await message.channel.send('Announcement posting is already OFF')
            else:
                await message.channel.send('I will stop posting announcements.')
                postAnnouncements.cancel()

        # restart command
        if message.content == '$restart':
            print('Executing $restart')
            await message.delete()
            if postAnnouncements.is_running():
                print('Restarting...')
                await message.channel.send('Restarting...')
                postAnnouncements.restart()
                print('Restarted successfully.')
                await message.channel.send('Restarted successfully.')
            else:
                print('Executing $start')
                await message.channel.send('I will start posting announcements.')

        # trunoff command
        if message.content == '$turnoff':
            print('Executing $turn off')
            await message.delete()
            await message.channel.send('Turning off and logging out.')
            await client.close()
        
        # showmem command
        if message.content == '$showmem':
            print('Executing $showmem')
            await message.delete()
            output_message = ''

            # load previous announcements from persistent storage
            with open('previous_announcements', 'rb') as announcements_memory_file:
                announcements_memory = pickle.load(announcements_memory_file)

            if not(announcements_memory == 'error'):
                for announcement in announcements_memory:
                    announcement_date = announcement[0]
                    announcement_text = announcement[1]
                    announcement_link = announcement[2]
                    
                    # shorten the long url using tinyURL
                    url_shortener = pyshorteners.Shortener() 
                    short_announcement_link = url_shortener.tinyurl.short(announcement_link)
                    
                    # add the announcement to the message that we print
                    output_message += announcement_date
                    output_message += ' - '
                    output_message += announcement_text
                    output_message += ' '
                    output_message += '<' + short_announcement_link + '>'
                    output_message += '\n'
            else:
                output_message += 'Something went wrong.'
            
            await message.channel.send(output_message)

        # updatemem command
        if message.content == '$updatemem':
            print('Executing $updatemem')
            await message.delete()
            await message.channel.send('Updating internal announcements memory.')

            most_recent_announcements = getLatestAnnouncements(url)
            # load previous announcements from persistent storage
            with open('previous_announcements', 'rb') as previous_announcements_file:
                previous_announcements = pickle.load(previous_announcements_file)

            # load previous messages from persistent storage
            with open('previous_announcement_messages', 'rb') as previous_announcement_messages_file:
                previous_announcement_messages = pickle.load(previous_announcement_messages_file)

            if not(most_recent_announcements == 'error'):
                temp_announcements = []
                for announcement in reversed(most_recent_announcements):
                    if announcement not in previous_announcements:
                        announcement_date = announcement[0]
                        announcement_text = announcement[1]
                        announcement_link = announcement[2]

                        announcement = (announcement_date, announcement_text, announcement_link)
                        temp_announcements.append(announcement)

                        # shorten the long url using tinyURL
                        url_shortener = pyshorteners.Shortener() 
                        short_announcement_link = url_shortener.tinyurl.short(announcement_link)

                        announcement_date_in_bold = '**' + announcement_date + '**'

                        discord_message = announcement_date_in_bold + ' - ' + announcement_text + ' ' + short_announcement_link

                        # make the bot post the announcement only if the message is NOT in previous_messages
                        if discord_message in previous_announcement_messages:
                            print ('Diplotipi anakoinwsi detected. Not posting...')
                        else:
                            await get_anakoinwseis_channel().send(discord_message)
                            print ('New announcement: ' + discord_message)
                            previous_announcement_messages.append(discord_message)
                    
                    else:
                        print('Event already in memory')

                # if there were any new announcements, meaning len(temp_announcements != 0) then add them to the previous ones
                if temp_announcements:
                    previous_announcements = previous_announcements[len(temp_announcements):] + temp_announcements

                    # keep the new announcements in persistent storage
                    with open('previous_announcements', 'wb') as previous_announcements_file:
                        pickle.dump(previous_announcements, previous_announcements_file)
                    
                    # keep the new messages in persistent storage
                    with open('previous_announcement_messages', 'wb') as previous_announcement_messages_file:
                        pickle.dump(previous_announcement_messages, previous_announcement_messages_file)

                output_message = ''
                if len(temp_announcements) == 1: output_message += str(len(temp_announcements)) + ' new announcement added.'
                else: output_message += str(len(temp_announcements)) + ' new announcements added.'
                await message.channel.send(output_message)

            else:
                await message.channel.send('Ιnternal announcements memory update failed.')

        # accept command only from bot moderators
        if message.content == '$uptime':
            print('Executing $uptime')
            await message.delete()
            output_message = ''
            output_message += 'Uptime: '

            uptime = time.monotonic() - uptime_before
            if uptime <= 60: uptime_str = "{:.0f}".format(uptime) + ' seconds'
            if uptime > 60: uptime_str = "{:.0f}".format(uptime/60) + ' minutes'
            if uptime >= 3600: uptime_str = "{:.0f}".format(uptime/3600) + ' hours'

            output_message += uptime_str
            print(output_message)
            await message.channel.send(output_message)

postAnnouncements.start() # start posting announcements as soon as the bot is ready
client.run(TOKEN)