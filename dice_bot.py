import signal

import discord
import sys

from dice import parse_to_result_str # this is red in pycharm, but it works

if len(sys.argv) >= 2:
    BOT_TOKEN = sys.argv[1]
else:
    print("Enter Bot Token (you could have entered it as the first command line argument to this script):")
    BOT_TOKEN = input()

print("Thanks. All required data for login available. Here we go...")

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user: # disable self reply
        return

    accepted_help_commands = ['help']
    accepted_dice_roll_commands = ['', 'würfel!', 'würfel', 'roll-the-dice', 'roll', 'dice', 'dnd']

    split = message.content.split(" ",1)
    command = split[0].lower()
    args = split[1] if len(split) > 1 else ''

    if command.startswith('!'):
        command = command[1:]
        if command in accepted_dice_roll_commands:
            try:
                result_str = parse_to_result_str(args)
                await message.channel.send(result_str)
            except:
                await message.channel.send('Thanks for trying {0.author.mention}, but that is not is just nothing I can roll. Tried !help?'.format(message))
        elif command in accepted_help_commands:
            await message.channel.send('Hi {0.author.mention}, you can role a dice using \"!dice <dice list>\".\n'
                                       'Some possible dice are \"D6, D8, D10, D20\".\n'
                                       'You can also roll multiple of the same dice at once using \"3xD20\"\n'
                                       'Or different dice using \"D20, D2, D4\"\n'
                                       'Also possible is to add a constant to a dice roll using for example \"D6+4\"\n'
                                       'It is also possible to sum or prod the result of a dice roll: \"+3xD4\"'.format(message))
        elif command == 'hi':
            await message.channel.send('Hi {0.author.mention}, role a dice?'.format(message))
        else:
            await message.channel.send('Hi {0.author.mention}, I don\'t recognise your humble request. If you want help, try !help'.format(message))


@client.event
async def on_ready():
    print('Bot \"'+client.user.name+'\" logged into discord')
    print('Bot User Id: '+str(client.user.id))
    print('---beginning operations---')

client.run(BOT_TOKEN)




def signal_handler(sig, frame):
    print('You pressed Ctrl+C! :O')
    client.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
    print("Waiting for input (examples: help, exit):")
    entered_text = input()
    if entered_text == 'exit':
        client.close()
    elif entered_text == 'help':
        print("current, you can only use the commands 'exit' and 'help'")
