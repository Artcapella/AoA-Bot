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
skills = ['acrobatics', 'arcana', 'athletics', 'crafting', 'deception', 'diplomacy', 'intimidation', 'medicine', 'nature', 'occultism', 'performance', 'religion', 'society', 'stealth', 'survival', 'thievery']
invocations = {}
character_data = {}

# - - - - - - - - - - - - - 

# - - - - Messages - - - - - - - - -
help_message: Final = "hello - greet the bot\n!help - display this message\n!day - get the current day\n!names - get all existing character names\n!partystats - get the current hp, maxhp and ac of the party\n!money [character name] - get the total funds for a character\n!partymoney - get the total funds for the party and who has how much\n"

# - - - - - - - - - - - - -

# JSON DATA

# ------- INVOCATION FUNCTIONS -------

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

# store current character data for all characters to character_data.json
def store_character_data():
    data = json.dumps(character_data, indent=4)
    with open('character_data.json', 'w') as f:
        f.write(data)

# read character_data.json
def read_character_data():
    global character_data
    if os.path.exists('character_data.json'):
        with open('character_data.json', 'r') as f:
            try:
                character_data = json.load(f)
            except json.JSONDecodeError:
                print("Error reading JSON file. Using default values.")
    else:
        print("JSON file does not exist. Using default values.")

# read duos_data.json
def read_duos():
    global dictionary
    if os.path.exists('duos_data.json'):
        with open('duos_data.json', 'r') as f:
            try:
                dictionary = json.load(f)
            except json.JSONDecodeError:
                print("Error reading JSON file. Using default values.")
    else:
        print("JSON file does not exist. Using default values.")

# -------------------------------------

# DICE METHODS
async def roll_dice(die_max, num_dice):
    total = 0
    for i in range(num_dice):
        total += random.randint(1, die_max)
    return total

async def roll_advantage(die_max):
    roll1 = random.randint(1, die_max)
    roll2 = random.randint(1, die_max)
    return max(roll1, roll2)

async def roll_disadvantage(die_max):
    roll1 = random.randint(1, die_max)
    roll2 = random.randint(1, die_max)
    return min(roll1, roll2)

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

    elif lowered == '!day':
        read_duos()
        return f"Hold on I need to ask Jason...\nThe current day is is *{dictionary['current_calendar_day']} of EoT 299*. The current phase is *{dictionary['current_phase']}*"
    
    # ---- CHARACTER COMMANDS ----

    elif lowered == '!names':
        character_names = get_character_names()
        if character_names:
            return f"Existing characters: *{', '.join(character_names)}*"
        else:
            return "Error: No characters found. Check the json file for proper formatting."
    
    elif lowered.__contains__('!skills'):
        # returns skill values for a character
        character_name = lowered.split(' ')[1]
        return get_proficiencies(character_name)

    elif lowered.__contains__('!statshelp'):
        #returns all stats in character_data.json
        character_name = lowered.split(' ')[1]
        stat_keys = get_stat_keys(character_name)
        if isinstance(stat_keys, list):
            return f"Stat keys for {character_name}: {', '.join(stat_keys)}"
        else:
            return stat_keys
            
    elif lowered.__contains__('!stats'):
        #reads character_data.json and returns the HP / maxHP, AC, and other relevant stats of the character
        
        return "!stats not implemented yet"
    
    elif lowered == '!money':
        #returns the total money for the character
        character_name = lowered.split(' ')[1]
        return get_money(character_name)
    
    elif lowered == '!partymoney':
        # returns the total money for the party and who has how much
        characters = get_character_names()
        if characters:
            party_money = "Party Funds:\n"
            for character in characters:
                #combines the returned string from get_money() for each character
                party_money += f"{get_money(character)}\n"
            return party_money
        else:
            return "Error: No characters found. Check the json file for proper formatting."
    
    elif lowered == '!partystats':
        #returns the current hp, maxhp and ac of the party
        '''
       
        '''
        return "feature not implemented yet"
    elif lowered == '!partyskills':
        #returns a list of who has the highest bonus in each skill
        
        return "feature not implemented yet"
    
    # ---- ADMIN COMMANDS ----

    elif lowered == '!firstnamebasis':
        await first_name_basis()
        return "Character names normalized successfully. You no longer have to type out those insanely long middle and last names you created."
    elif lowered == '!kill':
        print("heartless murder in progress...")
        kill()
        print("success!")
        return "*did not work*"
    else:
        return f"I'm sorry, I don't understand \'{user_input}\'"
    
# HANDLE STARTUP
@client.event
async def on_ready() -> None:
    print(f'{client.user} has connected to Discord!')

# HANDLE MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'{username} sent: {user_message} in {channel} ')

    # Check if there are any attachments
    if message.attachments:
        for attachment in message.attachments:
            # Check if the file is a .txt file
            if attachment.filename.endswith('.txt'):
                # Download the file
                file_path = f'./{attachment.filename}'
                await attachment.save(file_path)
                
                # Process the file (parse text to JSON)
                await process_txt_file(file_path, message)

    if await get_response(user_message) == "*dies*":
        await kill()
    if channel == 'azure' or channel == 'Direct Message with Unknown User':
        await send_message(message, user_message)

# PROCESS TXT FILES
async def process_txt_file(file_path: str, message: Message) -> None:
    # read the txt file
    async with aiofiles.open(file_path, mode='r') as f:
        text: str = await f.read()
    
    # attempt to convert to JSON
    try:
        new_character_data = json.loads(text)
        # get the character name and set to lowercase
        character_name = new_character_data['build']['name'].lower()

        # Load existing character data if the JSON file already exists
        json_file_path = 'character_data.json'

        if os.path.exists(json_file_path):
            async with aiofiles.open(json_file_path, 'r') as json_file:
                existing_data = await json_file.read()
                characters = json.loads(existing_data)
        else:
            characters = {}
        
        # Add/Update character data in the dictionary
        characters[character_name] = new_character_data

        # Save the updated character data back to the JSON file
        async with aiofiles.open(json_file_path, 'w') as json_file:
            await json_file.write(json.dumps(characters, indent=4))

        await message.channel.send(f"Character data for {character_name} saved in {json_file_path}")
        
    except json.JSONDecodeError:
        await message.channel.send("Failed to parse the txt file. Please ensure the file is in JSON format.")

# GET ALL STAT KEYS TO QUERY
def get_stat_keys(character_name: str) -> list:
    json_file_path = 'character_data.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            characters = json.load(json_file)
            character_name = character_name.lower()
            if character_name in characters:
                stat_keys = list(characters[character_name]['build']['proficiencies'].keys())
                # Collect keys from equipment
                for equipment in characters[character_name]['build']['equipment']:
                    if isinstance(equipment, dict):
                        stat_keys.extend(equipment.keys())
                return stat_keys
            else:
                return f"Character '{character_name}' not found."
    else:
        return "Character data file not found."

# GET ALL ITEMS IN INVENTORY
def get_inventory(character_name: str) -> list:
    json_file_path = 'character_data.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            characters = json.load(json_file)
            character_name = character_name.lower()
            if character_name in characters:
                inventory = characters[character_name]['build']['equipment']
                item_names = [item[0] for item in equipment if isinstance(item, list)]
                return ', '.join(item_names)
            else:
                return f"Character '{character_name}' not found."
    else:
        return "Character data file not found."
    
# GET ALL PROFICIENCIES (WITH CALCULATED BONUSES)
def get_proficiencies(character_name: str) -> list:
    json_file_path = 'character_data.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            characters = json.load(json_file)
            character_name = character_name.lower()
            if character_name in characters:
                # get the proficiencies: arcana, acrobatics, athletics, crafting, deception, diplomacy, intimidation, medicine, nature, occultism, performance, religion, society, stealth, survival, thievery
                # the values are the proficiency level: 0 = untrained, 2 = trained, 4 = expert, 6 = master, 8 = legendary
                # skill bonus = level + 2, 4, 6, or 8 + relevant stat (str, dex, con, int, wis, cha)
                character_level = characters[character_name]['build']['level']
                skills = {
                    'acrobatics': 0,
                    'arcana': 0,
                    'athletics': 0,
                    'crafting': 0,
                    'deception': 0,
                    'diplomacy': 0,
                    'intimidation': 0,
                    'medicine': 0,
                    'nature': 0,
                    'occultism': 0,
                    'performance': 0,
                    'religion': 0,
                    'society': 0,
                    'stealth': 0,
                    'survival': 0,
                    'thievery': 0
                }

                str_bonus = int((characters[character_name]['build']['abilities']['str'] - 10) / 2)
                dex_bonus = int((characters[character_name]['build']['abilities']['dex'] - 10) / 2)
                int_bonus = int((characters[character_name]['build']['abilities']['int'] - 10) / 2)
                wis_bonus = int((characters[character_name]['build']['abilities']['wis'] - 10) / 2)
                cha_bonus = int((characters[character_name]['build']['abilities']['cha'] - 10) / 2)
                
                # Update skill values based on proficiency and ability bonuses
                for skill in skills:
                    prof_lvl = characters[character_name]['build']['proficiencies'].get(skill, 0)
                    if prof_lvl > 0:
                        skills[skill] = prof_lvl + character_level
                    if skill in ['acrobatics', 'thievery', 'stealth']:
                        skills[skill] += dex_bonus
                    elif skill in ['arcana', 'nature', 'occultism', 'religion', 'crafting', 'society']:
                        skills[skill] += int_bonus
                    elif skill == 'athletics':
                        skills[skill] += str_bonus
                    elif skill in ['deception', 'diplomacy', 'intimidation', 'performance']:
                        skills[skill] += cha_bonus
                    elif skill in ['medicine', 'survival']:
                        skills[skill] += wis_bonus

                skill_summary = f"{character_name} Proficiencies:\n"
                for skill, value in skills.items():
                    skill_summary += f"{skill.capitalize()}: +{value}\n"
                return skill_summary
            else:
                return f"Character '{character_name}' not found."
    else:
        return "Character data file not found."

# GET TOTAL MONEY FROM CHARACTER DATA
def get_money(character_name: str) -> str:
    json_file_path = 'character_data.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            characters = json.load(json_file)
            character_name = character_name.lower()
            if character_name in characters:
                copper = characters[character_name]['build']['money']['cp']
                silver = characters[character_name]['build']['money']['sp']
                gold = characters[character_name]['build']['money']['gp']
                platinum = characters[character_name]['build']['money']['pp']
                return f"{character_name} Funds: {platinum} pp, {gold} gp, {silver} sp, {copper} cp"
            else:
                return f"Character '{character_name}' not found."
    else:
        return "Character data file not found."

# GET ALL CHARACTER NAMES
def get_character_names() -> list:
    json_file_path = 'character_data.json'
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            try:
                characters = json.load(json_file)
                return list(characters.keys())
            except json.JSONDecodeError:
                print("Error reading JSON file.")
                return []
    else:
        print("Character data file not found.")
        return []

# REMOVE LAST NAMES AND SPACES FROM CHARACTER NAMES
async def first_name_basis() -> None:
    json_file_path = 'character_data.json'
    
    if os.path.exists(json_file_path):
        async with aiofiles.open(json_file_path, 'r') as json_file:
            try:
                existing_data = await json_file.read()
                characters = json.loads(existing_data)
                
                normalized_characters = {}
                for full_name, data in characters.items():
                    first_name = full_name.split()[0].lower()
                    normalized_characters[first_name] = data
                
                async with aiofiles.open(json_file_path, 'w') as json_file:
                    await json_file.write(json.dumps(normalized_characters, indent=4))
                
                print("Character names normalized successfully.")
            except json.JSONDecodeError:
                print("Error reading JSON file.")
    else:
        print("Character data file not found.")

# COMMIT COLD BLOODED MURDER YOU HEARDLESS MONSTER HOW COULD YOU SHE HAD A FAMILY
async def kill() -> None:
    await client.close()

# MAIN ENTRY POINT
def main() -> None:
    read_character_data()
    print("just read character_data")
    client.run(TOKEN)

if __name__ == '__main__':
    main()
    