# made by github.com/notisv
# discord bot that manages welcome messages, creates polls, and handles various !commands

import time
import discord

#################################################
#                  DISCORD BOT                  #
#################################################

bot_version = 'v3.0'

intents = discord.Intents.default()
intents.members = True
intents.messages = True
client = discord.Client(intents = intents)
TOKEN = '<insert-token-here>' # secret token

bot_moderator_id = 760974440229634050 # janitor ID
admin_id = 988013663812190238 # steward id
uptime_before = time.monotonic()

@client.event
async def on_connect():
    print('Successfully logged in as {0.user}.'.format(client))

@client.event
async def on_disconnect():
    print('Shadowfax disconnected.')

@client.event
async def on_ready():
    print('Shadowfax ready.')
    # set 'listening' status
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "!drive | !poll | !help"))

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

        # janitor help command
        if message.content == '!help':
            print('Executing !help - @janitors/admins')
            await message.delete()
            output_message = ''
            output_message += '`Shadowfax ' + bot_version + '`\n'
            output_message += '`Commands:`\n'
            output_message += '`!ping - Pings the bot.`\n'
            output_message += '`!uptime - Displays the bot uptime.`\n'
            output_message += '`!turnoff - Makes the bot turn off and log out.`\n'
            output_message += '`!drive - Sends a dm containing containing instructions on how to connect to the shared Google Drive.`\n'
            output_message += '`!poll - Creates a poll (usage: !poll \"yes/no/idk poll\" or !poll \"multi option poll\" \"option 0\" ... \"option 9\" - max 10 options)`'
            await message.channel.send(output_message)
    
        # ping command
        if message.content == '!ping':
            print('Executing !ping')
            await message.delete()
            before = time.monotonic()
            message = await message.channel.send(':ping_pong: Pong! Latency:')
            ping = (time.monotonic() - before) * 1000
            await message.edit(content = f':ping_pong: Pong! Latency: `{int(ping)}ms`')

        # turnoff command
        if message.content == '!turnoff':
            print('Executing !turn off')
            await message.delete()
            await message.channel.send('Turning off and logging out.')
            await client.close()

        # uptime command
        if message.content == '!uptime':
            print('Executing !uptime')
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

    # commands accepted from bot moderators and @everyone alike

    # everyone help command
    if message.content == '!help' and moderator_admin_issued_command == False:
        print('Executing !help - @everyone')
        await message.delete()
        output_message = ''
        output_message += 'Για να δημιουργήσεις μια ψηφοφορία ναι/όχι/δεν ξέρω πληκτρολόγησε: !poll \"η ερωτησή σου μπαίνει εδώ\"\n'
        output_message += 'Για να δημιουργήσεις μια ψηφοφορία πολλαπλής επιλογής πληκτρολόγησε: !poll \"η ερωτησή σου μπαίνει εδώ\" \"επιλογή 0\" ... \"επιλογή 9\" (max 10 επιλογές)\n'
        await message.author.send(output_message)

    # drive command
    if message.content == '!drive':
        print('Executing !drive')
        await message.delete()

        output_message = discord.Embed(color = 0x74ADF9)
        output_message.set_author(name = 'CS Forces UOI Google Drive Instructions', icon_url = 'https://i.imgur.com/hbjRR5K.png')
        output_message.add_field(name = '\u200b\n:arrow_down: **Google Drive** :arrow_down:', value = 'Για να συνδεθείς στο κοινόχρηστο Google Drive πάτα εδώ: https://tinyurl.com/csforcesdrive\n\u200b', inline = False)
        output_message.add_field(name = ':sos: **ΠΡΟΣΟΧΗ** :sos:', value = 'To κοινόχρηστο Google Drive προσφέρεται **μόνο σε προπτυχιακούς φοιτητές - μέλη** του server. Για αυτό το λόγο, η πρόσβαση γίνεται **μόνο από email της μορφής cs0XXXX@uoi.gr αναφέροντας ολόκληρο το discord username σου** (%s) στο πεδίο μηνύματος.\n\u200b' % message.author, inline = False)
        output_message.add_field(name = ':arrow_down: **Rules** :arrow_down:', value = 'Παρακαλώ διάβασε τους κανόνες λειτουργίας: https://discord.com/channels/695303849443065947/761179743311495178/882952989252415498\n\u200b', inline = False)
        output_message.add_field(name = ':sos: **Reminder** :sos:', value = 'Η πρόσβασή σου θα εγκριθεί αυτοματοποιημένα εντός 48 ωρών.', inline = False)
        output_message.add_field(name = '\u200b', value = ':sos: :arrow_down: **Need help? Click me please** :arrow_down: :sos:', inline = False)
        output_message.set_image(url = 'https://i.imgur.com/F0dGDVm.png')

        await message.author.send(embed = output_message)

    # poll command
    poll_command_flag = '!poll'
    if message.content[:5] == poll_command_flag and message.content[-1] == '\"':
        print('Executing !poll')
        await message.delete()

        # command usage: !poll "poll question" "option 0" ... "option 9"
        # command usage: !poll "poll question"

        emojis = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':keycap_ten:']
        reaction_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        hand_emojis = ['👍', '👎', '🤷']

        message_string = message.content[5:]
        message_string = message_string[2:-1]
        arguments = message_string.split('\" \"')
        # arguments = ['poll question', 'option 0', 'option 1', ... , 'option 9']

        if len(arguments) == 1: # single argument poll
            # arguments = ['poll question']
            poll_question = arguments[0]

            output_message = ''
            output_message += '%s created a poll: ' % message.author.mention
            output_message += poll_question

            bot_message = await message.channel.send(output_message)
            await bot_message.add_reaction(hand_emojis[0])
            await bot_message.add_reaction(hand_emojis[1])
            await bot_message.add_reaction(hand_emojis[2])

        else: # multi argument poll  
            poll_question = arguments[0]
            arguments = arguments[1:]
            # arguments = ['option 0', 'option 1', ... , 'option 9']

            # prepare the options
            poll_options = ''
            i = 0
            while i < len(arguments):
                poll_options += '%s %s\n\n' % (emojis[i], arguments[i])
                i += 1

            output_message = discord.Embed(color = 0x74ADF9)
            output_message.add_field(name = '%s created a poll:' % message.author.name, value = poll_question, inline = False)
            output_message.add_field(name = 'React to vote', value = poll_options, inline = False)
            
            bot_message = await message.channel.send(embed = output_message)
            
            # add reactions
            j = 0
            while j < len(arguments):
                await bot_message.add_reaction(reaction_emojis[j])
                j += 1
        
@client.event
async def on_member_join(member):
    
    new_user_message = ''
    new_user_message += '> Γεια σου ' + member.name + '! Καλώς ήρθες στο CS Forces UOI, τον discord server του τμήματος Μηχανικών Η/Υ & Πληροφορικής του Πανεπιστημίου Ιωαννίνων!\n'
    new_user_message += '> \n'
    new_user_message += '> Εάν είσαι πρωτοετής επισκέψου το <#893637136287412255> και το <#993488690036887652>.\n'
    new_user_message += '> \n'
    new_user_message += '> Πριν ξεκινήσεις να στέλνεις μηνύματα διάβασε τους <#761179743311495178> μας.\n'
    new_user_message += '> Εάν έχεις απορίες για κάποιο μάθημα, ρώτησέ τες στο **αντίστοιχο** channel, αφού ρίξεις πρώτα μια ματιά στα pinned messages.\n'
    new_user_message += '> \n'
    new_user_message += '> Για να συνδεθείς στο κοινόχρηστο Google Drive χρησιμοποίησε την εντολή !drive.\n'
    new_user_message += '> \n'
    new_user_message += '> Tα invite links για να καλέσεις τους φίλους σου στο server είναι <https://dsc.gg/csforces> και https://discord.gg/2GWwRaZ3C7\n'
    new_user_message += '> Tο link για το facebook group της σχολής είναι αυτό: <https://www.facebook.com/groups/568750480454101>'

    print('\n%s#%s joined the server' % (member.name, str(member.discriminator)))

    try: 
        dm_channel = await member.create_dm()
        await dm_channel.send(new_user_message)
        print('Sent welcome message to %s#%s' % (member.name, str(member.discriminator)))
    except:
       print('Couldn\'t message %s#%s' % (member.name, str(member.discriminator)))

    # store each new member on file
    try:
        with open('members.txt', 'a') as members_file:
            members_file.write('%s    @%s#%s\n' % (member.id, member.name, str(member.discriminator)))
        print('Put %s#%s on members.txt\n' % (member.name, str(member.discriminator)))
        members_file.close()
    except:
        print('Error when opening members.txt\n')

client.run(TOKEN)