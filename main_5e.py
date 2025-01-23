from typing import Final
import os
from dotenv import load_dotenv
from discord import Client, Intents, Message
from response import get_response
import random
import json
import aiofiles

# LOAD TOKEN FROM .ENV FILE
load_dotenv()
TOKEN: Final = os.getenv('DISCORD_TOKEN')

# BOT SETUP - ACTIVATE INTENTS
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

# - - - - - - - - - - - - - 
# global variables
skills = ["athletics", "acrobatics", "sleight of hand", "stealth", "arcana", "history", "investigation", "nature", "religion", "animal handling", "insight", "medicine", "perception", "survival", "deception", "intimidation", "performance", "persuasion"]
invocations = {}
character_names = ['Sahar', 'Myst', "Lucy"]

# - - - - - - - - - - - - - 

# - - - - Messages - - - - - - - - -
help_message: Final = "hello - greet the bot\n!help - display this message\n!day - get the current day\n!names - get all existing character names\n!partystats - get the current hp, maxhp and ac of the party\n!money [character name] - get the total funds for a character\n!partymoney - get the total funds for the party and who has how much\n"

# - - - - - - - - - - - - -

# JSON DATA

# ------- INVOCATION FUNCTIONS -------

max_invocations = 8

# read the invocations.json file
def read_invocations():
    global invocations
    if os.path.exists('invocations.json'):
        with open('invocations.json', 'r') as f:
            try:
                invocations = json.load(f)
            except json.JSONDecodeError:
                print("Error reading JSON file. Using default values.")
    else:
        print("JSON file does not exist. Using default values.")

# add a new invocation to invocations.json
def add_invocation(invocation_name, invocation_description):
    invocations[invocation_name] = invocation_description
    data = json.dumps(invocations, indent=4)
    with open('invocations.json', 'w') as f:
        f.write(data)

# -------------------------------------

# ------- CHARACTER DATA FUNCTIONS -------

def get_character_names():
    return character_names

# ------ Message Logic ------
# MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    # Check if the message is empty
    if user_message == '': 
        response = "empty message detected"

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        # Correctly await the get_response coroutine
        response: str = await get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# ---------------------------- RESPONSES LOGIC ----------------------------
async def get_response(user_input: str) -> str:

    lowered: str = user_input.lower().strip()

    if lowered == '':
        return "empty input detected"
    
    elif lowered == 'hello' or lowered == 'hi' or lowered == 'hey' or lowered == 'hello!':
        return 'Hello! How can I help? If you need a list of commands, type: *!help*'
    
    elif lowered == '!help':
        return help_message
    
    # ---- INFO COMMANDS ----

    # ---- CHARACTER COMMANDS ----

    elif lowered == '!names':
        character_names = get_character_names()
        if character_names:
            return f"Existing characters: *{', '.join(character_names)}*"
        else:
            return "Error: No characters found. Check the json file for proper formatting."


# COMMIT COLD BLOODED MURDER YOU HEARDLESS MONSTER HOW COULD YOU SHE HAD A FAMILY
async def kill() -> None:
    await client.close()

# MAIN ENTRY POINT
def main() -> None:
    read_invocations()
    print("just read character_data")
    client.run(TOKEN)

if __name__ == '__main__':
    main()
    