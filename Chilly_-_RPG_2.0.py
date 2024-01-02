import re
import string
import nextcord
from nextcord.ext import commands, tasks
from nextcord.ui import View

import os
import json
import asyncio
import time
import datetime
import functools
import random
import uuid

from typing import List, Optional
from dataclasses import dataclass, field
from decimal import *

TOKEN = "MTEwOTYzMzU5NzY0MTYwMTEyNg.GgWcD7.ggx5e-LP311uuQHO3aQ4eRW8z5H0JFdZI2106w"
pic_link = 'https://yt3.ggpht.com/k8l2-DSZPRrM0jFGkdh9icXdI_WN-Fc4Ic3LICmeplAklpv32ouQ4zCXoN66zmofNmMYqbYaDA=s88-c-k-c0x00ffffff-no-rj-mo'

profile_data = {}
market_items = {}
guilds = {}

intents = nextcord.Intents.all()
intents.typing = True
intents.presences = True
bot = commands.Bot(intents=intents)

file_path = "C:\\Users\\heypa\\rpg_botdata\\rpg_items.json"
DATA_FOLDER = "C:\\Users\\heypa\\rpg_botdata\\"
ACHIEVEMENTS_PATH = "C:\\Users\\heypa\\rpg_botdata\\rpg_achievements.json"
REPORTS_FILE = 'rpg_reportdata.json'
BLACKLIST_FILE = "rpg_cl_serversettings.json"

update_active = False
DEBUG_MODE = False

BUG_CHANNEL = 1173958042702848020
staff_role_id = 1106066036886867998
DEVELOPER_RANK_ID = 1148624320550158490
EVENT_CHANNEL_ID = 1160312211227553963
BOOSTERPING_ROLE_ID = 1187784267984556042
GUILD_ID = 1108128390030045237
DEBUG_CHANNEL_ID = 1147632992446054604
BANS_CHANNEL_ID = 1154684567563812874
log_channel_id = 1157373710215422063
UPDATE_CHANNEL_ID = 1114878899558567936
COOWNER_ID = 893792975761584139
OWNER_ID = 893759402832699392
ACTIVE_UPDATE_ROLE_ID = 1188241227485827252
UPDATE_PING_ROLE_ID = 1105649201578254358
JOIN_COMMAND_ID = 928875861036400721
OWNERS_CHANNEL_ID = 1121473246571798558

RPC_DEFAULT_STATE = '✅ | v0.6 | 🦅'
RPC_DEVELOPER_STATE = '⚠️ | DEV | 🦅'
RPC_UPDATE_STATE = '❌ | UPDATE | 🦅'

OWNERS_CHANNEL_NAME = '・Boys VC 🎤'

RECORDING_CHANNEL_NAME = '・vc-rec-logs'
DEVELOPER_RANK = '⚙️ Developer'
ACHIEVEMENTS_ROLENAME = '⊶▬▬⊶▬▬ 𝕮𝖍𝖎𝖑𝖑𝖞 𝕸𝖎𝖑𝖊𝖘𝖙𝖔𝖓𝖊𝖘 ▬▬⊷▬▬⊷'

xp_multiplier = 1
gold_multiplier = 1

def get_player_data_filename(player_name):
    data_folder = DATA_FOLDER
    os.makedirs(data_folder, exist_ok=True)
    return os.path.join(data_folder, f'{player_name}.json')

async def load_player_data(player_name):
    filename = get_player_data_filename(player_name)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    else:
        return None

async def save_player_data(player_name, data):
    filename = get_player_data_filename(player_name)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@bot.event
async def on_ready():   
    print(f'⚙️  Serving in {len(bot.guilds)} guild(s).')
    print(f'✅ Online as {bot.user.name} BOT')     
    await set_rich_presence(RPC_DEFAULT_STATE)
    print('---------------------------------------------------------') 
    await check_and_start_weekend_boost()

@bot.event
async def on_member_update(before, after):
    if str(before.status) == "online":
        if str(after.status) == "offline" or "idle":
            print(f"status changed")
            pass

async def set_rich_presence(state):
    activity = nextcord.Activity(type=nextcord.ActivityType.playing, name=state)
    await bot.change_presence(activity=activity)

async def get_all_player_names():
    players = []

    data_folder = "C:/Users/heypa/rpg_botdata/"

    for filename in os.listdir(data_folder):
        if filename.startswith("rpg_"):
            continue

        if filename.endswith(".json"):
            player_name = filename[:-5]
            players.append(player_name)

    return players

async def perform_tip(ctx, member, amount):
    sender_name = ctx.author.name
    receiver_name = member.name

    sender_data = await load_player_data(sender_name)
    receiver_data = await load_player_data(receiver_name)

    sender_data["gold"] -= amount
    receiver_data["gold"] += amount

    with open(get_player_data_filename(sender_name), "w") as file:
        json.dump(sender_data, file, indent=4)

    with open(get_player_data_filename(receiver_name), "w") as file:
        json.dump(receiver_data, file, indent=4)

    success_message = await ctx.send(f"🪙 {amount} gold successfully sent to {member.mention}.")
    await asyncio.sleep(10)
    await success_message.delete()

def format_gold(amount):
    abbreviations = [
        (1_000_000_000_000_000_000_000_000, "sp"),
        (1_000_000_000_000_000_000_000, "sx"),
        (1_000_000_000_000_000_000, "qt"),
        (1_000_000_000_000_000, "q"),
        (1_000_000_000_000, "t"),
        (1_000_000_000, "b"),
        (1_000_000, "m"),
        (100_000, "k"),
    ]

    for limit, abbreviation in abbreviations:
        if amount >= limit:
            return f"{amount // limit}{abbreviation}"

    return str(amount)

# ? Create New Player
def create_new_player(name):
    player_data = {
        'name': name,
        'game_started': True,    
        'xp_notification': True,   
        '1st_fish_gift': False,
        'profile_visibility': True,
        'level': 1,
        'mastery_points': 0,
        'xp': 0,
        'gold': 100,
        'last_daily_claim': 0,
        'last_weekly_claim': 0,
        'last_monthly_claim': 0,
        'last_fish_time': 0,
        'last_quiz_attempt': 0,
        'messages_sent': 0,
        'clicks': 0,
        'fights_won': 0,
        'fights_lost': 0,
        'completed_missions': 0,
        'pet_points': 0,
        'active_missions': {},
        'active_rod': {},
        'active_pets': {},
        'pets': {},
        'inventory': {},
        'masteries': {
        "More Clicks": {
            "name": "More Clicks",
            "description": "Allows you to get more Clicks in the Clicker Game.",
            "maxlevel": 10,
            "current_level": 0,
            "cost": 150
        },
        "Reduce Rewards Cooldown": {
            "name": "Reduce Rewards Cooldown",
            "description": "By Getting this Upgrade you can decrease the Time between the daily, weekly, monthly cooldown..",
            "maxlevel": 5,
            "current_level": 0,
            "cost": 200
        },
        "Reduce Fishing Cooldown": {
            "name": "Reduce Fishing Cooldown",
            "description": "Reduces the cooldown time between fishing attempts.",
            "maxlevel": 5,
            "current_level": 0,
            "cost": 100
        },            
        "Unlock /fish": {
            "name": "Unlock /fish",
            "description": "Get the /fish and Fish everyday hour an Item!",
            "maxlevel": 1,
            "current_level": 0,
            "cost": 550
        },        
        "Unlock /monthly": {
            "name": "Unlock /monthly",
            "description": "Unlock monthly rewards! Gain a random amount of XP and Gold to power up your medieval journey.",
            "maxlevel": 1,
            "current_level": 0,
            "cost": 1500
        },        
        "Unlock /weekly": {
            "name": "Unlock /weekly",
            "description": "Unlock weekly rewards! Gain a random amount of XP and Gold to power up your medieval journey.",
            "maxlevel": 1,
            "current_level": 0,
            "cost": 750
        }
    },
}

    return player_data

with open("rpg_achievements.json", "r", encoding="utf-8") as achievements_file:
    achievements = json.load(achievements_file)
achievements_earned = {}

def save_earnedachievements_data():
    with open("rpg_achievementsearned.json", "w") as file:
        json.dump(achievements_earned, file, indent=4)

def load_earnedachievements_data():
    try:
        with open("rpg_achievementsearned.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

achievements_earned = load_earnedachievements_data()

def load_achievements():
    with open('rpg.namesanddescachievements.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data.get('names', []), data.get('descriptions', {})

def load_market_data():
    try:
        with open('rpg_marketdata.json', 'r', encoding='utf-8') as file:
            market_data = json.load(file)
    except FileNotFoundError:
        market_data = {}
    return market_data

def save_market_data(market_data):
    with open('rpg_marketdata.json', 'w', encoding='utf-8') as file:
        json.dump(market_data, file, indent=4, ensure_ascii=False)

def get_user_clan_name(user_name):
    for clan_name, clan_info in clan_data.items():
        if user_name in clan_info['members']:
            return clan_name
    return None 

async def send_dm(user, embed):
    try:
        await user.send(embed=embed)
    except nextcord.HTTPException:
        pass

def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r") as file:
            data = json.load(file)
            return data.get("blacklisted_channels", [])
    except FileNotFoundError:
        return []

blacklisted_channels = load_blacklist()

async def log_to_channel(message, message_link):
    log_channel = bot.get_channel(log_channel_id)
    log_message = f"{message}\n**`Message:`** {message_link}"
    await log_channel.send(log_message)

def get_message_link(ctx):
    return f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}"

def log_command(command_name):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            try:
                user_name = ctx.user.name.lower()
                filename = f'{user_name}.json'
                player_data = await load_player_data(filename)

                if ctx.guild is None:
                    not_server_embed = nextcord.Embed(
                        title="⚠️ Hey! Click me to join The Server",
                        description="**`This command is only allowed in Chill Lounge approved servers. Visit the Chill Lounge for more Infomation!`**",
                        url="https://discord.gg/zcMXXGFwvB",
                        color=0xFF9900
                    )
                    not_server_embed.set_footer(text="🦅 | @prodbyeagle |", icon_url=pic_link)
                    await ctx.send(embed=not_server_embed, ephemeral=True)
                    return

                command_author = ctx.user.name
                timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                message_link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.id}"
                log_message = f"**`[{timestamp}]`**  |  **`{command_name}`**  |  **`{command_author}`**"
                await log_to_channel(log_message, message_link)

                return await func(ctx, *args, **kwargs)
            except Exception as e:
                embed = nextcord.Embed(
                    title="❌ Error Occurred",
                    description=f"**`{str(e)}`**",
                    color=0xFF0000
                )
                embed.set_footer(text="🦅 | @prodbyeagle | /bug", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)

        return wrapper
    return decorator
# -------------
# STANDARD COMMANDS:

# ✅ /start
@bot.slash_command(
    name="start",
    description="✅ Starts the game.",
)
@log_command('start')
async def start(ctx):
    player_name = ctx.user.name

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
    
    if player_name in profile_data:
        embed = nextcord.Embed(
            title="❌ Character Exists",
            description="You already have an existing character. Use `</rpgcommands:1178728993600589876>` to continue your adventure.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
    else:
        player_data = await load_player_data(player_name)

        if player_data is None:
            player_data = create_new_player(player_name)
            await save_player_data(player_name, player_data)

            welcome_messages = [
                f"🏰 Welcome, {player_name}! Your medieval adventure begins now.",
                f"🗡️ Greetings, {player_name}! Prepare to embark on a grand medieval journey.",
                f"🏰 Hail, {player_name}! Your medieval saga starts here.",
                f"🫅🏻 Welcome, {player_name}! Prepare for an epic journey through the medieval realm.",
                f"🏰 Hello, {player_name}! Your medieval adventure awaits.",
                f"⚔️ Greetings, {player_name}! Embark on your medieval quest now.",
                f"🛡️ Welcome, {player_name}! May your armor be strong and your sword swift in this medieval realm.",
                f"🏹 Hail, {player_name}! Archers at the ready, your medieval adventure begins!",
                f"🏰 Greetings, {player_name}! Prepare for medieval glory and honor.",
                f"⚔️ Salutations, {player_name}! Sharpen your blade and get ready for medieval battles.",
                f"🏰 Welcome, {player_name}! The medieval kingdom rejoices in your arrival.",
                f"🛡️ Greetings, {player_name}! Your medieval destiny awaits, brave warrior.",
                f"🏹 Huzzah, {player_name}! May your medieval journey be filled with triumph and valor.",
                f"⚔️ Welcome, {player_name}! Unleash your medieval prowess on the realm.",
                f"🏰 Greetings, {player_name}! Your presence graces the medieval lands with honor.",
                f"🛡️ Hail, {player_name}! Prepare to be legendary in this medieval saga.",
                f"🌟 Greetings, {player_name}! Embark on a magical journey through the medieval realm! 🏰",
                f"🚀 Welcome, {player_name}! Blast off into a medieval adventure filled with wonders and quests! 🌠",
                f"🌈 Huzzah, {player_name}! Your presence brings color to the medieval kingdom! 🎨",
                f"🌟 Greetings, {player_name}! May your medieval adventure be as bright as the stars! ✨",
                f"🚀 Welcome, {player_name}! Your journey through the medieval galaxy begins now! 🌌",
                f"🛡️ Hail, {player_name}! Dive into the colorful tapestry of the medieval world! 🎭",
                f"🌟 Salutations, {player_name}! Sparkle and shine in your medieval exploits! 💫",
                f"🚀 Greetings, {player_name}! Soar through the medieval skies with bravery and courage! 🦅",
                f"🌈 Welcome, {player_name}! Illuminate the medieval lands with your unique brilliance! 🌟",
                f"🌟 Hail, {player_name}! Your medieval saga is destined to be legendary! 🏆",
            ]
            random_welcome_message = random.choice(welcome_messages)
            embed = nextcord.Embed(
                title="⚔️ Medieval RPG",
                description=random_welcome_message,
                color=nextcord.Color.random()
            )
            embed.add_field(
                name="Getting Started",
                value="🎒 Use </inventory:1178728990459056138> to see your Inventory.\n⚙️ Use </rpgcommands:1178728993600589876> to view the availible Commands.",
                inline=False
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="⚠️ Warning!",
                description="You already have an existing character. Use </rpgcommands:1178728993600589876> to continue your adventure.",
                color=nextcord.Color.yellow()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)

# 🎒 /inventory
@bot.slash_command(
    name='inventory',
    description='🎒 Open your Inventory.'
)
@log_command('inventory')
async def inventory(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)

    if player_data is None or not player_data:
        embed = nextcord.Embed(
            title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    inventory = player_data['inventory']
    embed = nextcord.Embed(title="🎒 Inventory", color=nextcord.Color.blue())

    items_text = '\n'.join(
    f"**`x{item['amount']}`** **`{item['name']}`** Durability: **`{item.get('durability', 'N/A')}`**\nEnchantments: {', '.join([enchantment['name'] for enchantment in item.get('enchantments', None)])}\n"
    for item in inventory.values()
    )
    embed.add_field(name="Items", value=items_text, inline=False)

    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

    await save_player_data(player_name, player_data)

# 🪙 /tip
class TipConfirmationView(nextcord.ui.View):
    def __init__(self, ctx, member, amount):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.member = member
        self.amount = amount

    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.success, custom_id="confirm_button")
    async def confirm_button(self, button, interaction):
        if interaction.user == self.ctx.user:
            embed = nextcord.Embed(
                title="✅ Transfer Successful",
                description=f"🪙 {self.amount} gold has been successfully transferred to 🧑🏻 {self.member.mention}.",
                color=nextcord.Color.green()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await self.ctx.send(embed=embed)
            await self.perform_tip()
            self.stop()

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.red, custom_id="cancel_button")
    async def cancel_button(self, button, interaction):
        if interaction.user == self.ctx.user:
            embed = nextcord.Embed(
                title="❌ Transfer Canceled",
                description="Transfer got Canceled. No Tip was executed.",
                color=nextcord.Color.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await self.ctx.send(embed=embed, ephemeral=True)
            self.stop()

    async def perform_tip(self):
        sender_name = self.ctx.user.name
        receiver_name = self.member.name

        sender_data = await load_player_data(sender_name)
        receiver_data = await load_player_data(receiver_name)

        sender_data["gold"] -= self.amount
        receiver_data["gold"] += self.amount

        with open(get_player_data_filename(sender_name), "w") as file:
            json.dump(sender_data, file, indent=4)

        with open(get_player_data_filename(receiver_name), "w") as file:
            json.dump(receiver_data, file, indent=4)

@bot.slash_command(
    name='tip',
    description='🪙 Tip a user some gold!'
)
@log_command('tip')
async def tip(ctx, member: nextcord.Member, amount: int):
    sender_name = ctx.user.name
    receiver_name = member.name

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    if sender_name == receiver_name:
        embed = nextcord.Embed(
            title="❌ Invalid Transaction",
            description="You can't tip yourself.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    sender_data = await load_player_data(sender_name)
    receiver_data = await load_player_data(receiver_name)

    if not sender_data:
        embed = nextcord.Embed(
            title="❌ Error",
            description="**`You don't have an active profile!`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    if sender_data["gold"] < amount:
        embed = nextcord.Embed(
            title="❌ Insufficient Funds",
            description="You don't have enough Gold to send this amount.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    if not receiver_data:
        embed = nextcord.Embed(
            title="❌ Error",
            description="The specified recipient is not registered as a player.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    embed = nextcord.Embed(
        title="🪙 Gold Transfer Confirmation",
        description=f"Do you want to send 🪙 **`{amount}`** gold to 🧑🏻 {member.mention}?",
        color=nextcord.Color.orange()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)

    await ctx.send(embed=embed, view=TipConfirmationView(ctx, member, amount))

# 📊 /rank
def get_medal_emoji(position):
    if position == 1:
        return '🥇'
    elif position == 2:
        return '🥈'
    elif position == 3:
        return '🥉'
    else:
        return '🏅'

async def send_rankings_embed(ctx, title, rank_list):
    embed = nextcord.Embed(title=title, color=0xFFFFFF)
    for i, rank in enumerate(rank_list):
        medal_emoji = get_medal_emoji(i+1)
        embed.add_field(name=f'{medal_emoji} {rank}', value='\u200B', inline=False)
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

class Character:
    def __init__(self, name, level, gold):
        self.name = name
        self.level = level
        self.gold = gold

    def calculate_networth(self):
        return self.level * 1000 + self.gold

async def load_characters():
    global characters
    characters = {}
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith('.json'):
            player_name = filename[:-5]
            player_data = await load_player_data(player_name)
            if player_data is not None and 'name' in player_data and 'level' in player_data and 'gold' in player_data:
                character = Character(
                    name=player_data['name'],
                    level=player_data['level'],
                    gold=player_data['gold']
                )
                characters[player_name] = character

@bot.slash_command(
    name='leaderboards',
    description='📊 See the Leaderboards!'
)
@log_command('leaderboards')
async def leaderboards(ctx, type: str = nextcord.SlashOption(
        name="type",
        description="Select the ranking type.",
        choices={"Level": "level", "Gold": "gold", "Net Worth": "networth"
        },
        required=True
    )
):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    await load_characters()

    if type == "level":
        sorted_characters = sorted(characters.values(), key=lambda c: c.level, reverse=True)
        rank_list = [f'{char.name} (Level {char.level})' for char in sorted_characters]
        await send_rankings_embed(ctx, 'Level Rankings', rank_list)
    elif type == "gold":
        sorted_characters = sorted(characters.values(), key=lambda c: c.gold, reverse=True)
        rank_list = [f'{char.name} (Gold: {char.gold})' for char in sorted_characters]
        await send_rankings_embed(ctx, 'Gold Rankings', rank_list)
    elif type == "networth":
        sorted_characters = sorted(characters.values(), key=lambda c: c.calculate_networth(), reverse=True)
        rank_list = [f'{char.name} (Net Worth: {char.calculate_networth()})' for char in sorted_characters]
        await send_rankings_embed(ctx, 'Net Worth Rankings', rank_list)
    else:
        await ctx.send("🪙 Available ranking types: 'Level', 'Gold', 'Net Worth'", ephemeral=True)

# 🥇 /achievements 
class AchievementsView(nextcord.ui.View):
    def __init__(self, achievements):
        super().__init__()

        self.achievements = [achievement for achievement in achievements if not achievement.get("hidden", False)]
        self.page = 1
        self.items_per_page = 4
        self.num_pages = -(-len(achievements) // self.items_per_page)

    async def show_page(self, page):
        start_index = (page - 1) * self.items_per_page
        end_index = page * self.items_per_page

        embed = nextcord.Embed(title="🎖️ Achievements", color=nextcord.Color.blue())

        for i in range(start_index, end_index):
            if i >= len(self.achievements):
                break

            achievement = self.achievements[i]
            embed.add_field(name=achievement["name"], value=achievement["description"], inline=False)

        embed.set_footer(text=f"🏆 Seite {page}/{self.num_pages} | 🦅 | @prodbyeagle", icon_url=pic_link)
        return embed

    @nextcord.ui.button(label="Vorherige Seite", style=nextcord.ButtonStyle.red, emoji="⬅️")
    async def previous_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.page > 1:
            self.page -= 1
        embed = await self.show_page(self.page)
        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="Nächste Seite", style=nextcord.ButtonStyle.green, emoji="➡️")
    async def next_page(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.page < self.num_pages:
            self.page += 1
        embed = await self.show_page(self.page)
        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="Free Gold??!", style=nextcord.ButtonStyle.blurple, custom_id="fakegold", emoji="🪙")
    async def nothing(self, button: nextcord.Button, interaction: nextcord.Interaction):
        player_name = interaction.user.name
        player_data = await load_player_data(player_name)
    
        if player_data:
            embed_before_purchase = nextcord.Embed(title="Checking your Gold...", color=0xFFD700)
            embed_before_purchase.add_field(name="🪙 Gold", value=player_data['gold'])
    
            embed_after_purchase = nextcord.Embed(title="Item Bought", color=0x7CFC00)
            embed_after_purchase.add_field(name="🪙 Gold", value="0")

            await interaction.response.send_message(content="Checking your Gold...", embed=embed_before_purchase, ephemeral=True)
            await asyncio.sleep(2)

            await interaction.edit_original_message(content="✅ Item Bought!", embed=embed_after_purchase)
            await asyncio.sleep(2)
            await interaction.delete_original_message()

with open("rpg_achievements.json", "r", encoding="utf-8") as file:
    achievements_data = json.load(file)

@bot.slash_command(
    name='achievements',
    description='🥇 Look at the Achievements.'
)
@log_command('achievements')
async def achievements(ctx):
    achievements_list = list(achievements_data.values())

    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    achievements_view = AchievementsView(achievements_list)
    await achievements_view.show_page(1)
    await ctx.send(embed=await achievements_view.show_page(1), view=achievements_view, ephemeral=True)

# 👛 /wallet
@bot.slash_command(
    name='wallet',
    description='👛 Open your Wallet to see your Gold.'
)
@log_command('wallet')
async def wallet(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    gold = player_data.get('gold', 0)

    embed = nextcord.Embed(title="💰 Wallet", color=nextcord.Color.gold())
    embed.add_field(name="📊 Balance", value=f"{gold} Gold", inline=False)
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)

    await ctx.send(embed=embed, ephemeral=True)
    await save_player_data(player_name, player_data)

# 💻 /rpgcommands
@bot.slash_command(
    name='rpgcommands',
    description='💻 Displays a list of available commands.'
)
@log_command('rpgcommands')
async def rpgcommands(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
    
    embed = nextcord.Embed(title="**🔓 All Active Commands**")
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    embed.set_author(name="Work in Progress! Not Final on some Things!")

    embed.add_field(name="🪙 **Standard Commands**", value="""
    :beginner: `/start` - Start your adventure now!
    :trophy: `/leaderboards [gold | level | networth]` - View the leaderboard.
    :notebook_with_decorative_cover: `/itemlist` - Item list.
    :gear: `/settings` - Access user settings.
    :dna: `/redeem` - Redeem your rewards using special codes.  
    :trophy: `/achievements` - Show all achievements in the game.                    
    :bar_chart: `/profile [user]` - Show statistics of a user.
    """, inline=False)

    embed.add_field(name="**🤝 Player Commands**", value="""
    :moneybag: `/wallet` - Look at your Gold in your Wallet.
    :chart_with_downwards_trend: `/masterys` - View and Upgrade your Masterys!                    
    :bulb: `/tip [user] [amount]` - Give a tip to a user.
    :gift: `/gift [user] [item]` - Give an item to another user.
    :sun_with_face: `/daily` - Claim your daily rewards!
    :frame_photo: `/weekly` - Claim your weekly rewards!
    :rainbow: `/monthly` - Claim your monthly rewards!  
    :briefcase: `/inventory` - Open your inventory.                                      
    """, inline=False)

    embed.add_field(name="**👑 Clan Commands**", value="""
    :shield: `/clancreate [clanname] [privacy]` - Create a new clan.
    :handshake: `/clanjoin [clanname]` - Join an existing clan.
    :door: `/clanleave` - Leave your current clan.
    :envelope: `/claninvite [user]` - Invite Users to your clan.
    :hammer: `/clanban [user]` - Ban a user from your clan.
    :unlock: `/clanunban [user]` - Unban a user from your clan.
    """, inline=False)

    embed.add_field(name="🕹️ Game Commands", value="""
    :video_game: `/clicker` - Start a Clicking Adventure...
    :boxing_glove: `/fight [opponent]` - Fight for your glory!
    :jigsaw: `/dailyquiz` - Take a daily quiz (Reset every 24 Hours)
    :fish: `/fish` - Fish some Items! (1 per Hour)
    """, inline=False)

    await ctx.send(embed=embed, ephemeral=True)

# 💻 /devcommands
@bot.slash_command(
    name='devcommands',
    description='💻 Displays a list of available devcommands.'
)
@log_command('devcommands')
async def devcommands(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)

    allowed_roles = ['⚙️ Developer']
    if any(role.name in allowed_roles for role in ctx.user.roles): 

        if player_data is None or not player_data:
            embed = nextcord.Embed(
            title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
            color=nextcord.Color.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed)
            return
     
        if update_active:
            update_embed = nextcord.Embed(
                title="🛠️ Update in Progress",
                description="A system update is currently in progress. Please try again later.",
                color=nextcord.Color.orange()
            )
            update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=update_embed, ephemeral=True)
            return
    
        embed = nextcord.Embed(title="**🔓 Developer Commands**")
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    
        embed.add_field(name="**⚙️ Developer Commands**", value="""
            :hammer: `/giveitem [user] [item] [amount]` - Give an item to a user.
            :gear: `/additem [item] [amount]` - Add an item to the game.
            :gear: `/testadditem [item] [amount]` - Test adding an item to the game.
            :hammer: `/deleteitem [item] [amount]` - Delete an item from the game.
            :goldbag: `/goldrain [amount]` - Make gold rain.
            """, inline=False) 
                        
        embed.add_field(name="**⚙️ Developer Commands**", value="""           
            :x: `/deleteuser [user]` - Delete a user account.
            :chart_with_upwards_trend: `/givexp [user] [amount]` - Give experience points to a user.
            :arrows_counterclockwise: `/resetxp [user]` - Reset the experience points of a user.
            :arrows_counterclockwise: `/update` - Initiate a game update.
            :checkered_flag: `/endupdate` - End the ongoing game update.
            :cloud_rain: `/itemrain [chances]` - Make items rain in the game.
            :wastebasket: `/cleartestacc` - Clear test accounts from the system.
            :rocket: `/createtestacc` - Create a test account for testing purposes.
            :broom: `/clearchannel [channel]` - Clear messages from a specific channel.
            """, inline=False)
        await ctx.send(embed=embed, ephemeral=True)       
    else:
        error_embed = nextcord.Embed(
            title="❌ Error",
            description="You do not have permission for this command.",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_embed, ephemeral=True)

# 🤖 /profile 
def format_number(number):
    suffixes = ['', 'k', 'm', 'b', 't', 'qd', 'qt', 'qq', 'qn', 'qnt', 's', 'se', 'sp', 'o', 'n', 'd', 'e', 'z', 'y', 'r']
    suffix_index = 0
    while number >= 1000 and suffix_index < len(suffixes) - 1:
        number /= 1000
        suffix_index += 1
    return f'{number:.2f}{suffixes[suffix_index]}'

@bot.slash_command(
    name='profile',
    description='🤖 View your profile or from Other players.'
)
@log_command('profile')
async def profile(ctx, player_name: nextcord.Member):
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
    
    if not player_data.get('profile_visibility', True):
        visibility_embed = nextcord.Embed(
            title="❌ Profile is not visible",
            description=f"The profile for {player_name} is set to private.",
            color=nextcord.Color.red()
        )
        visibility_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=visibility_embed, ephemeral=True)
        return   
     
    if player_data:
        embed = nextcord.Embed(title=f"🪪 Profile from @{player_name}", color=nextcord.Color.blue())
        embed.add_field(name="🪪 Name", value=player_data['name'])
        embed.add_field(name="⚙️ Level", value=player_data['level'])
        embed.add_field(name="📊 XP", value=player_data['xp'])       
        embed.add_field(name="🪙 Gold", value=format_number(player_data['gold']))
        embed.add_field(name="📬 Messages Sent", value=format_number(player_data['messages_sent']))
        embed.add_field(name="🖱️ Clicks", value=format_number(player_data['clicks']))
        embed.add_field(name="🥇 Fight Won", value=player_data['fights_won'])
        embed.add_field(name="💀 Fights Lost", value=player_data['fights_lost'])  
        embed.add_field(name="🌟 Mastery Points", value=player_data['mastery_points'])              
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(title="❌ Error", description=f"Profile for {player_name} not found. ", color=nextcord.Color.red())
        await ctx.send(embed=embed, ephemeral=True)

# 🎁 /gift 
async def load_inventory(user_file):
    try:
        with open(user_file, 'r') as file:
            user_data = json.load(file)
            return user_data.get('inventory', {})
    except FileNotFoundError:
        return {}

async def send_gift_message(sender, recipient, item_name):
    gift_embed = nextcord.Embed(
        title="✉️ Gift Received",
        description=f"**{sender.mention}** has sent you **`{item_name}`** as a gift!",
        color=nextcord.Color.green()
    )
    gift_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await recipient.send(embed=gift_embed)

@bot.slash_command(
    name='gift',
    description='🎁 Gift an item to another user.',
)
async def gift(ctx, recipient: nextcord.User, item_name: str):
    player_name = ctx.user.name
    user_file = f"{player_name}.json"
    user_inventory = await load_inventory(user_file)
 
    if user_file is None or not user_file:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    if item_name in user_inventory and user_inventory[item_name].get("amount", 0) > 0:
        user_inventory_copy = user_inventory.copy()

        user_inventory_copy[item_name]['amount'] -= 1

        if "amount" in user_inventory_copy[item_name] and user_inventory_copy[item_name]["amount"] <= 0:
            del user_inventory_copy[item_name]

        user_inventory = user_inventory_copy

        with open(user_file, 'r') as file:
            user_data = json.load(file)

        user_data['inventory'] = user_inventory

        with open(user_file, 'w') as file:
            json.dump(user_data, file, indent=4)

        recipient_name = recipient.name.lower()
        recipient_file = f"{recipient_name}.json"
        try:
            with open(recipient_file, 'r') as file:
                recipient_data = json.load(file)
        except FileNotFoundError:
            recipient_data = {}

        if user_file is None or not user_file:
            embed = nextcord.Embed(
                title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
                color=nextcord.Color.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed)
            return

        if 'inventory' not in recipient_data:
            embed = nextcord.Embed(
                title="❌ Error",
                description="**`The recipient doesn't have an active profile!`**",
                color=nextcord.Color.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return

        if item_name in recipient_data['inventory']:
            recipient_data['inventory'][item_name]['amount'] += 1
        else:
            recipient_data['inventory'][item_name] = {
                "name": item_name,
                "durability": item_name.durability,
                "amount": 1
            }

        with open(recipient_file, 'w') as file:
            json.dump(recipient_data, file, indent=4)

        await send_gift_message(ctx.user, recipient, item_name)

        success_embed = nextcord.Embed(
            title="✅ Gift Sent",
            description=f"You have sent **`{item_name}`** as a gift to **{recipient.mention}**.",
            color=nextcord.Color.green()
        )
        success_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=success_embed, ephemeral=True)
    else:
        error_embed = nextcord.Embed(
            title="❌ Error",
            description=f"You do not have any more of the item '{item_name}' to gift.",
            color=nextcord.Color.red()
        )
        error_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=error_embed, ephemeral=True)

# 🤔 /suggesttochillyrpg
@bot.slash_command(
    name='suggesttochillyrpg',
    description='🤔 Send Tips for Chilly: RPG (no bug reports)'
)
@log_command('suggesttochillyrpg')
async def suggesttochillyrpg(interaction: nextcord.Interaction):
    suggest_modal = SuggestModal(bot)
    await interaction.response.send_modal(suggest_modal)

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await interaction.send(embed=update_embed, ephemeral=True)
        return

class SuggestModal(nextcord.ui.Modal):
    def __init__(self, bot):
        super().__init__(
            "Submit a Suggestion!",
        )
        self.bot = bot

        self.suggestion = nextcord.ui.TextInput(
            label="Share your suggestion:",
            min_length=5,
            max_length=500,
            required=True
        )
        self.add_item(self.suggestion)

    async def callback(self, interaction: nextcord.Interaction):
        suggestion_text = self.suggestion.value

        channel = self.bot.get_channel(893762440196677646)
        if channel is not None:
            embed = nextcord.Embed(
                title=f'🦅 Suggestion from {interaction.user.name}',
                description=f'\n**`{suggestion_text}`**',
                color=nextcord.Colour.green()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await channel.send(embed=embed)

            confirmation_embed = nextcord.Embed(
                title='✅ Suggestion Sent',
                description='**`Your suggestion has been sent to the bot developer.`**',
                color=nextcord.Colour.green()
            )
            confirmation_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title='❌ Error',
                description='**`The channel where suggestions are sent to could not be found.`**',
                color=nextcord.Colour.red()
            )
            error_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
 
# 📉 /masterys
with open('rpg_masterydata.json', 'r') as f:
    mastery_data = json.load(f)

@bot.slash_command(
    name='masterys',
    description='📉 View and Upgrade your Masterys!'
)
@log_command('masterys')
async def masterys(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)

    await save_player_data(player_name, player_data)

    if player_data is None or not player_data:
        nodataembed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        nodataembed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=nodataembed)
        return

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    async def upgrade_mastery(interaction, player_data, selected_mastery):
        if 'current_level' not in selected_mastery:
            selected_mastery['current_level'] = 0

        mastery_name = selected_mastery["name"]
        cost = selected_mastery['cost']
    
        updated_mastery_points = player_data['mastery_points'] - cost
    
        if updated_mastery_points >= 0 and selected_mastery['current_level'] < selected_mastery['maxlevel']:
            selected_mastery['current_level'] += 1
            player_data['mastery_points'] -= cost
            player_data['masteries'][mastery_name] = selected_mastery
            await save_player_data(player_name, player_data)
    
            response_embed = nextcord.Embed(
                title=f'✅ {selected_mastery["name"]} updated!',
                description=f'**You have updated** **`{selected_mastery["name"]}`** **to level** **`{selected_mastery["current_level"]}`**',
                color=nextcord.Color.green()
            )

            await interaction.response.send_message(embed=response_embed, ephemeral=True)
            await update_mastery_embed(ctx, player_data, view)
            await view.disable_buttons(selected_mastery)
    
        else:
            if updated_mastery_points < 0:
                errorresponse_embed = nextcord.Embed(
                    title='❌ Error',
                    description=f'**You don`t have enough points! You need {cost} Points**',
                    color=nextcord.Color.red()
                )
                await interaction.response.send_message(embed=errorresponse_embed, ephemeral=True)
            elif selected_mastery['current_level'] >= selected_mastery['maxlevel']:
                maxresponse_embed = nextcord.Embed(
                    title='❌ Error',
                    description=f'**The maximum level for** **`{selected_mastery["name"]}`** **has been reached!**',
                    color=nextcord.Color.red()
                )
                await interaction.response.send_message(embed=maxresponse_embed, ephemeral=True)
    
    class MasteryButton(nextcord.ui.Button):
        def __init__(self, selected_mastery, **kwargs):
            super().__init__(**kwargs)
            self.selected_mastery = selected_mastery
    
        async def callback(self, interaction: nextcord.Interaction):
            await upgrade_mastery(interaction, player_data, self.selected_mastery)
    
            if self.selected_mastery['current_level'] >= self.selected_mastery['maxlevel']:
                self.style = nextcord.ButtonStyle.green
                self.disabled = True
    
    class MasteryView(View):
        async def interaction_check(self, interaction: nextcord.Interaction):
            if interaction.user == ctx.user:
                return True
            else:
                response_embed = nextcord.Embed(
                    title='❌ Error',
                    description='**`This command is not for you. But wait... HOW DO YOU EVEN GOT THIS. THAT WAS EPHEMERAL!??!?!`**',
                    color=nextcord.Color.red()
                )
                await interaction.message.send(embed=response_embed, ephemeral=True)
                return False

        async def disable_buttons(self, selected_mastery):
            for child in self.children:
                if isinstance(child, nextcord.ui.Button):
                    if child.selected_mastery == selected_mastery:
                        child.disabled = True

    async def update_mastery_embed(ctx, player_data, view):
        mastery_points = player_data.get('mastery_points', 0)
        embed = nextcord.Embed(title=f"📜 Masterys for {ctx.user.name} - {mastery_points} Points Left", color=nextcord.Color.gold())
        
        for mastery_name, mastery_data in player_data.get('masteries', {}).items():
            current_level = mastery_data.get('current_level', 0)
            max_level = mastery_data.get('maxlevel', 0)
            description = mastery_data.get('description', "No description available.")
            cost = mastery_data.get('cost', 0)
            formatted_mastery_name = f"{mastery_data['name']}"
    
            if current_level >= max_level:
                formatted_mastery_name = f"~~{formatted_mastery_name}~~"
    
            embed.add_field(
                name=f"{formatted_mastery_name} (Level {current_level}/{max_level})",
                value=f"Cost: `{cost} Points`\n{description}\n",
                inline=False
            )
    
        embed.set_footer(text="🦅 | @prodbyeagle | Sometimes can you upgrade each Mastery only 2 times because the Magician cant handle more.", icon_url=pic_link)

        if hasattr(view, 'message') and view.message:
            await view.message.edit(embed=embed, view=view)
        else:
            view.message = await ctx.send(embed=embed, view=view, ephemeral=True)

    view = MasteryView()

    async def button_callback(interaction, button, selected_mastery):
        await upgrade_mastery(interaction, player_data, selected_mastery)

        if selected_mastery['current_level'] >= selected_mastery['maxlevel']:
            button.style = nextcord.ButtonStyle.green
            button.disabled = True

    for mastery_name, mastery_data in player_data.get('masteries', {}).items():
        formatted_mastery_name = f"{mastery_data['name']}"

        button = MasteryButton(style=nextcord.ButtonStyle.grey, label=formatted_mastery_name, selected_mastery=mastery_data)
        button.callback = lambda i, m=mastery_data: button_callback(i, button, m)

        if mastery_data['current_level'] >= mastery_data['maxlevel']:
            button.style = nextcord.ButtonStyle.green
            button.disabled = True

        view.add_item(button)

    await update_mastery_embed(ctx, player_data, view)
    await view.wait()

# 🧬 /redeem
ACTIVE_CODES_FILE = "rpg_activecodes.json"

class RedeemModal(nextcord.ui.Modal):
    def __init__(self, bot, user):
        super().__init__("Enter your Merch Code!")
        self.bot = bot
        self.user = user.name

        self.merchfield = nextcord.ui.TextInput(
            label="Enter Here! | 'lowercase' allowed",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="CL-XXX-XXXX-XXXXX",
            required=True,
            max_length=17,
        )
        self.add_item(self.merchfield)

    async def callback(self, interaction: nextcord.Interaction):
        entered_code = self.merchfield.value.upper()

        with open(ACTIVE_CODES_FILE, 'r') as file:
            active_codes_data = json.load(file)
        
        active_codes = active_codes_data.get('codes', [])
        used_codes = active_codes_data.get('used', [])

        if entered_code in used_codes:
            already_used_embed = nextcord.Embed(
                title='❌ Code Already Redeemed',
                description=f'The code "{entered_code}" has already been redeemed.',
                color=0xFF0000
            )
            await interaction.response.send_message(embed=already_used_embed, ephemeral=True)
        elif entered_code in active_codes:
            active_codes.remove(entered_code)
            used_codes.append(entered_code)

            with open(ACTIVE_CODES_FILE, 'w') as file:
                json.dump({'codes': active_codes, 'used': used_codes}, file, indent=4)

            success_embed = nextcord.Embed(
                title='✅ Code Redeemed',
                description=f'The code "{entered_code}" has been successfully redeemed!',
                color=0x00FF00
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title='❌ Invalid Code',
                description=f'The code "{entered_code}" is not valid. Please check and try again.',
                color=0xFF0000
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

@bot.slash_command(
    name='redeem',
    description='👾 Redeem a Merch Code.'
)
@log_command('redeem')
async def redeem(interaction: nextcord.Interaction):
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await interaction.send(embed=update_embed, ephemeral=True)
        return

    with open(ACTIVE_CODES_FILE, 'r') as file:
        active_codes_data = json.load(file)
    
    active_codes = active_codes_data.get('codes', [])

    if not active_codes:
        no_codes_embed = nextcord.Embed(
            title='❌ No Codes Available',
            description='There are currently no active merch codes available. Please try again later.',
            color=0xFF0000
        )
        await interaction.response.send_message(embed=no_codes_embed, ephemeral=True)
        return

    redeem_modal = RedeemModal(bot, interaction.user)
    await interaction.response.send_modal(redeem_modal)
# -------------

# SETTINGS:
# 🔢 /settings
def generate_confirmation_code():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

def delete_player_file(user_name):
    file_path = f'{user_name.lower()}.json'

    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    else:
        return False

confirmation_codes = {}

async def remove_achievement_roles(member, achievements_path, guild):
    try:
        with open(achievements_path, 'r', encoding='utf-8') as achievements_file:
            achievements_data = json.load(achievements_file)

        member_roles = [role.name for role in member.roles]

        for achievement, data in achievements_data.items():
            achievement_name = data.get("name", "")
            if achievement_name in member_roles:
                role_to_remove = next((role for role in guild.roles if role.name == achievement_name), None)
                if role_to_remove:
                    await member.remove_roles(role_to_remove)
    except Exception as e:
        print(f"Error removing achievement roles: {e}")

class SettingsView(nextcord.ui.View):
    def __init__(self, user_name, guild):
        super().__init__()
        self.user_name = user_name
        self.bot = bot
        self.guild = guild

    @nextcord.ui.button(label="Delete Player Data", style=nextcord.ButtonStyle.red)
    async def delete_player_data(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        confirmation_code = generate_confirmation_code()
        confirmation_codes[self.user_name] = confirmation_code
    
        code_embed = nextcord.Embed(
            title="💔 I hope I can see you again!",
            description=f"| `{confirmation_code}` | 30 Seconds for you to Send it in the DM's of the Bot! Goodbye.",
            color=nextcord.Color.red()
        )
        await interaction.response.edit_message(embed=code_embed, view=self)
    
        def check(message):
            return isinstance(message.channel, nextcord.DMChannel) and message.author.id == interaction.user.id
    
        try:
            user_response = await self.bot.wait_for('message', check=check, timeout=30)
            if user_response.content == f'{confirmation_code}':
                user = await self.bot.fetch_user(interaction.user.id)
                member = self.guild.get_member(user.id)
                delete_request_channel = self.guild.get_channel(1177771568114442250)
                if delete_request_channel:
                    player_data_file_path = f"{user.name}.json"
                    if os.path.exists(player_data_file_path):
                        os.remove(player_data_file_path)
    
                    with open('rpg_achievementsearned.json', 'r') as achievements_file:
                        achievements_data = json.load(achievements_file)
    
                    if str(user.name) in achievements_data:
                        del achievements_data[str(user.name)]
    
                    with open('rpg_achievementsearned.json', 'w') as achievements_file:
                        json.dump(achievements_data, achievements_file, indent=4)
    
                    await remove_achievement_roles(member, ACHIEVEMENTS_PATH, self.guild)
    
                    delete_request_embed = nextcord.Embed(
                        title="🗑️ Delete Player Data Request",
                        description=f"User: {user.name} ({user.id}) has deleted their player data.",
                        color=nextcord.Color.red()
                    )
                    await delete_request_channel.send(embed=delete_request_embed)
                    await user.send("✅ Your Player + Achievements was Successfully Deleted Use </start:1178729424854728744> to Start again!")
                else:
                    await user.send("❌ Delete request channel not found. Unable to process the request.")                    
            else:
                await user.send("❌ The Code was Incorrect. The Deletion was stopped!")                    
        except asyncio.TimeoutError:
            await interaction.response.followup.send("❌ 30 Seconds are Over!. Action canceled.")

    @nextcord.ui.button(label="Toggle XP Notifications", style=nextcord.ButtonStyle.red)
    async def toggle_xp_notifications(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user_filename = f'{self.user_name}.json'
        user_data = cash_load_data(user_filename)
        user_data['xp_notification'] = not user_data.get('xp_notification', True)
        cash_save_data(user_filename, user_data)
    
        button.style = nextcord.ButtonStyle.green if user_data['xp_notification'] else nextcord.ButtonStyle.red
    
        notification_status = "On" if user_data['xp_notification'] else "Off"

        embed = nextcord.Embed(
            title="XP Notifications Toggle",
            description=f"XP Notifications are now {notification_status}!",
            color=nextcord.Color.green() if user_data['xp_notification'] else nextcord.Color.red()
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="Set Profile Visbility", style=nextcord.ButtonStyle.red)
    async def toggle_profile_visibility(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user_filename = f'{self.user_name}.json'
        user_data = cash_load_data(user_filename)
        user_data['profile_visibility'] = not user_data.get('profile_visibility', True)
        cash_save_data(user_filename, user_data)
    
        button.style = nextcord.ButtonStyle.green if user_data['profile_visibility'] else nextcord.ButtonStyle.red
    
        notification_status = "True" if user_data['profile_visibility'] else "False"

        embed = nextcord.Embed(
            title="Profile Visibility",
            description=f"Profile Visibility is now {notification_status}!",
            color=nextcord.Color.green() if user_data['profile_visibility'] else nextcord.Color.red()
        )

        await interaction.response.edit_message(embed=embed, view=self)

@bot.slash_command(
    name='settings',
    description='🔢 Change some Settings!'
)
@log_command('settings')
async def settings(ctx):
    user_name = ctx.user.name
    user_filename = f'{ctx.user.name.lower()}.json'
    user_data = cash_load_data(user_filename)
    xp_notification = user_data.get('xp_notification', True)
    guild = ctx.guild

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    if user_data is None or not user_data:
        embed = nextcord.Embed(
            title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    view = SettingsView(ctx.user.name.lower(), guild)
    
    view.children[0].style = nextcord.ButtonStyle.green if xp_notification else nextcord.ButtonStyle.red

    settings_embed = nextcord.Embed(
        title="⚙️ Settings Menu",
        description=f"Hello, {ctx.user.name}! This is your settings menu.",
        color=nextcord.Color.dark_grey()
    )
    settings_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    settings_embed.add_field(name="", value="- **Delete Player Data**: **`Clears your player data`**.\n- **Toggle XP Notifications:** **`Enable/Disable XP notifications`**.\n- **Set Profile Visibility**: **`Toggle visibility of your profile stats.`**")
    await ctx.send(embed=settings_embed, view=view, ephemeral=True)

# -------------
# REWARDS SYSTEM:

def calculate_random_rewards(min_gold, max_gold, min_xp, max_xp):
    random_xp = random.randint(min_xp, max_xp)
    random_gold = random.randint(min_gold, max_gold)
    return random_xp, random_gold

async def can_claim(command_name, player_data, cooldown, mastery_level):
    last_claim_key = f"last_{command_name}_claim"
    last_claim_timestamp = player_data.get(last_claim_key, 0)
    current_timestamp = time.time()
    time_since_last_claim = current_timestamp - last_claim_timestamp
    adjusted_cooldown = cooldown * (1 - mastery_level * 0.1)

    if time_since_last_claim < adjusted_cooldown:
        return False, int(adjusted_cooldown - time_since_last_claim)
    return True, 0

# 🌞 /daily
@bot.slash_command(
    name='daily',
    description='🌞 Claim your daily rewards!'
)
@log_command('daily')
async def daily(ctx):
    player_name = str(ctx.user.name)
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    mastery_level = player_data['masteries'].get('Reduce Rewards Cooldown', {}).get('current_level', 0)

    cooldown = 24 * 60 * 60
    can_claim_daily, time_until_next_claim = await can_claim('daily', player_data, cooldown, mastery_level)

    if not can_claim_daily:
        remaining_time = time_until_next_claim

        remaining_hours, remaining_seconds = divmod(remaining_time, 3600)
        remaining_minutes, remaining_seconds = divmod(remaining_seconds, 60)

        unix_timestamp_next_claim = int(time.time() + time_until_next_claim)

        embed = nextcord.Embed(title="⏰ Daily Reward Reminder", color=nextcord.Color.gold())
        embed.description = f"You have already claimed your daily reward today. Next claim available at <t:{unix_timestamp_next_claim}:R>"
        embed.set_footer(text="🦅 | @prodbyeagle")
        await ctx.send(embed=embed, ephemeral=True)
        return

    random_xp, random_gold = calculate_random_rewards(500, 1000, 100, 750)

    player_data["xp"] += random_xp
    player_data["gold"] += random_gold
    player_data["last_daily_claim"] = time.time()

    await save_player_data(player_name, player_data)

    formatted_gold = f"{random_gold} Gold"

    embed = nextcord.Embed(title="🌞 Daily Rewards", color=nextcord.Color.gold())
    embed.add_field(name="🪙 Gold", value=formatted_gold, inline=False)
    embed.add_field(name="🌟 XP", value=random_xp, inline=False)
    embed.set_footer(text="🦅 | @prodbyeagle")
    await ctx.send(embed=embed, ephemeral=True)

# 🖼️ /weekly
@bot.slash_command(
    name='weekly',
    description='🖼️ Claim your weekly rewards!'
)
@log_command('weekly')
async def weekly(ctx):
    player_name = str(ctx.user.name)
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
  
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    mastery_level = player_data['masteries'].get('Unlock /weekly', {}).get('current_level', 0)
    
    if mastery_level < 1:
        embed = nextcord.Embed(
            title="❌ **`You need to upgrade your Unlock /weekly mastery to use this command! Click this to visit the Masterys:`** </masterys:1179166654391930931>",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    mastery_level = player_data['masteries'].get('Reduce Rewards Cooldown', {}).get('current_level', 0)
    cooldown = 7 * 24 * 60 * 60
    can_claim_weekly, time_until_next_claim = await can_claim('weekly', player_data, cooldown, mastery_level)

    if not can_claim_weekly:
        remaining_time = time_until_next_claim

        remaining_hours, remaining_seconds = divmod(remaining_time, 3600)
        remaining_minutes, remaining_seconds = divmod(remaining_seconds, 60)

        unix_timestamp_next_claim = int(time.time() + time_until_next_claim)

        embed = nextcord.Embed(title="⏰ Weekly Reward Reminder", color=nextcord.Color.gold())
        embed.description = f"You have already claimed your Weekly reward. Next claim available at <t:{unix_timestamp_next_claim}:R>"
        embed.set_footer(text="🦅 | @prodbyeagle")
        await ctx.send(embed=embed, ephemeral=True)
        return

    random_xp, random_gold = calculate_random_rewards(1250, 2000, 500, 1000)

    player_data["xp"] += random_xp
    player_data["gold"] += random_gold
    player_data["last_weekly_claim"] = time.time()

    await save_player_data(player_name, player_data)

    formatted_gold = f"{random_gold} gold"

    embed = nextcord.Embed(title="🌤️ Weekly Rewards", color=nextcord.Color.gold())
    embed.add_field(name="🪙 Gold", value=formatted_gold, inline=False)
    embed.add_field(name="🌟 XP", value=random_xp, inline=False)
    embed.set_footer(text="🦅 | @prodbyeagle")
    await ctx.send(embed=embed, ephemeral=True)

# 🌈 /monthly
@bot.slash_command(
    name='monthly',
    description='🌈 Claim your monthly rewards!'
)
@log_command('monthly')
async def monthly(ctx):
    player_name = str(ctx.user.name)
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
  
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    mastery_level = player_data['masteries'].get('Unlock /monthly', {}).get('current_level', 0)
    
    if mastery_level < 1:
        embed = nextcord.Embed(
            title="❌ **`You need to upgrade your Unlock /monthly mastery to use this command! Click this to visit the Masterys:`** </masterys:1179166654391930931>",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    mastery_level = player_data['masteries'].get('Reduce Rewards Cooldown', {}).get('current_level', 0)
    cooldown = 30 * 24 * 60 * 60
    can_claim_monthly, time_until_next_claim = await can_claim('monthly', player_data, cooldown, mastery_level)

    if not can_claim_monthly:
        remaining_time = time_until_next_claim

        remaining_hours, remaining_seconds = divmod(remaining_time, 3600)
        remaining_minutes, remaining_seconds = divmod(remaining_seconds, 60)

        unix_timestamp_next_claim = int(time.time() + time_until_next_claim)

        embed = nextcord.Embed(title="⏰ Monthly Reward Reminder", color=nextcord.Color.gold())
        embed.description = f"You have already claimed your Monthly reward. Next claim available at <t:{unix_timestamp_next_claim}:R>"
        embed.set_footer(text="🦅 | @prodbyeagle")
        await ctx.send(embed=embed, ephemeral=True)
        return

    random_xp, random_gold = calculate_random_rewards(2500, 6250, 2000, 5000)

    player_data["xp"] += random_xp
    player_data["gold"] += random_gold
    player_data["last_monthly_claim"] = time.time()

    await save_player_data(player_name, player_data)

    formatted_gold = f"{random_gold} gold"

    embed = nextcord.Embed(title="🌈 Monthly Rewards", color=nextcord.Color.gold())
    embed.add_field(name="🪙 Gold", value=formatted_gold, inline=False)
    embed.add_field(name="🌟 XP", value=random_xp, inline=False)
    embed.set_footer(text="🦅 | @prodbyeagle")
    await ctx.send(embed=embed, ephemeral=True)
# -------------
# CLAN SYSTEM:
try:
    with open('rpg_clandata.json', 'r') as file:
        clan_data = json.load(file)
except FileNotFoundError:
    clan_data = {}

def save_clan_data():
    with open("rpg_clandata.json", "w") as f:
        json.dump(clan_data, f, indent=4)

# 🫅🏻 /clancreate
@bot.slash_command(
    name='clancreate',
    description='🫅🏻 Create Your OWN Clan!'
)
@log_command('clancreate')
async def clancreate(ctx, clan_name: str, privacy: str = nextcord.SlashOption(
    name="privacy",
    description="Choose the privacy setting for your clan.",
    choices={"Public": "public", "Private": "private"
    },
    required=True
)):
    global clan_data
    leader_id = ctx.user.id
    leader_name = ctx.user.name
    cleaned_clan_name = clan_name.strip().lower()
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
  
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
    
    for clan in clan_data.values():
        if leader_name in clan['members']:
            embed = nextcord.Embed(
                title='⚠️ Warning',
                description='**`You already belong to a clan. You can only create one clan at a time.`**',
                color=nextcord.Colour.yellow()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return

        if cleaned_clan_name in clan_data:
            embed = nextcord.Embed(
                title='⚠️ Warning',
                description=f'**`The clan name "{clan_name}" already exists. Please choose a different name.`**',
                color=nextcord.Colour.yellow()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return

    leader_role = await ctx.guild.create_role(name=f'👑 {clan_name} - Leader')
    member_role = await ctx.guild.create_role(name=f'🧑🏻 {clan_name} - Member')

    if leader_role is None or member_role is None:
        embed = nextcord.Embed(
            title='❌ Error',
            description='**`Failed to create clan roles. Please try again.`**',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    clan_category = 1160662906459914383
    role = ctx.guild.get_role(clan_category)
    await ctx.user.add_roles(leader_role)
    await ctx.user.add_roles(role)

    if cleaned_clan_name not in clan_data:
        guild_id = ctx.guild.id

        clan_data[cleaned_clan_name] = {
            'clan_name': clan_name,
            'leader_id': leader_id,
            'leader_name': leader_name,
            'leader_role_id': leader_role.id,
            'member_role_id': member_role.id,
            'members': [leader_name],
            'banned_players': [],
            'privacy': privacy,
            'guild_id': guild_id
        }
        save_clan_data()

        embed = nextcord.Embed(
            title='✅ Success',
            description=f'**`The clan "{clan_name}" has been successfully created.`**',
            color=nextcord.Colour.green()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# 💠 /claninfo
@bot.slash_command(
    name='claninfo',
    description='💠 Get Information About a Clan'
)
@log_command('claninfo')
async def claninfo(ctx, clanname: str):
    clanname = clanname.lower()
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
  
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
     
    if clanname in clan_data:
        clan_info = clan_data[clanname]

        embed = nextcord.Embed(
            title=f'🏰 Clan Info - @{clanname}',
            color=nextcord.Colour.random()
        )
        embed.add_field(name='Leader', value=clan_info['leader_name'])
        embed.add_field(name='Privacy', value=clan_info['privacy'])
        embed.add_field(name='Total Members', value=len(clan_info['members']))
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)

        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title='❌ Error',
            description='The specified clan does not exist.',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# 🚪 /clanjoin
@bot.slash_command(
    name='clanjoin',
    description='🚪 Join the Clan!'
)
@log_command('clanjoin')
async def clanjoin(ctx, name):
    name = name.lower()
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
   
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    if name in clan_data:
        leader_name = clan_data[name]['leader_id']

        def is_leader_id_in_clan_data(leader_id):
            for clan_name in clan_data:
                if clan_data[clan_name]['leader_id'] == leader_id:
                    return True
            return False
        
        if len(clan_data[name]['members']) >= 50:
            embed = nextcord.Embed(
                title="❌ **`Clan is Full!`**",
                description="**`The clan you're trying to join already has the maximum number of members.`**",
                color=nextcord.Color.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if not is_leader_id_in_clan_data(leader_name):
            embed = nextcord.Embed(
                title='❌ Error',
                description='**`The clan leader is no longer in the clan.`**',
                color=nextcord.Colour.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return
    
    if name in clan_data:
        if ctx.user.name == clan_data[name]['leader_name']:
            embed = nextcord.Embed(
                title='❌ Error',
                description='**`You cannot join your own clan.`**',
                color=nextcord.Colour.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
        elif clan_data[name]['privacy'] == 'public':
            clan_data[name]['members'].append(ctx.user.name)
            save_clan_data()

            clan_name = clan_data[name]['clan_name']
            await ctx.guild.fetch_roles()
            member_role = nextcord.utils.get(ctx.guild.roles, name=f'🧑🏻 {clan_name} - Member')
            if member_role:
                await ctx.user.add_roles(member_role)
                clan_category = 1160662906459914383
                role = ctx.guild.get_role(clan_category)
                await ctx.user.add_roles(role)

            embed = nextcord.Embed(
                title='✅ Success',
                description=f'You have joined the clan **`{name}`**. The role **`"{member_role.name}"`** has been assigned to you.',
                color=nextcord.Colour.green()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title='✅ Success',
                description=f'Your request to join the clan **`{name}`** has been sent to the clan leader. You will be notified when they have responded.',
                color=nextcord.Colour.green()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)

            leader_id = clan_data[name]['leader_id']
            leader = await bot.fetch_user(leader_id)
            leader_dm = await leader.create_dm()

            embed = nextcord.Embed(
                title='🦅 Clan Join Request',
                description=f'The user **`{ctx.user.name}`** has requested to join your clan, **`{name}`**.',
                color=nextcord.Colour.orange()
            )
            embed.add_field(name='🏷️ Server Nickname', value=ctx.user.display_name, inline=True)
            embed.add_field(name='🗓️ Creation Date', value=ctx.user.created_at.strftime('%d-%m-%Y'), inline=True)
            embed.add_field(name='/claninvite Command', value=f'/claninvite invited_user:@{ctx.user.name} clan_name:{name}', inline=True)
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            
            embed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar.url)
            await leader_dm.send(embed=embed)
    else:
        embed = nextcord.Embed(
            title='❌ Error',
            description='**`This clan does not exist.`**',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# 🚷 /clanleave
@bot.slash_command(
    name='clanleave',
    description='🚷 Leave the Clan!'
)
@log_command('clanleave')
async def clanleave(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
   
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    with open('rpg_clandata.json', 'r') as clan_file:
        clan_data = json.load(clan_file)

    for clan_name, clan_info in clan_data.items():
        if player_name in clan_info['members']:
            if clan_info['leader_name'] == player_name:
                embed = nextcord.Embed(
                    title='❌ Error',
                    description='You cannot leave the clan as you are the leader.',
                    color=nextcord.Color.red()
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)
                return

            clan_info['members'].remove(player_name)

            with open('rpg_clandata.json', 'w') as clan_file:
                json.dump(clan_data, clan_file, indent=4)

            guild = ctx.guild
            leader_role_id = clan_info['leader_role_id']
            member_role_id = clan_info['member_role_id']
            leader_role = nextcord.utils.get(guild.roles, id=leader_role_id)
            member_role = nextcord.utils.get(guild.roles, id=member_role_id)

            if leader_role:
                try:
                    await ctx.user.remove_roles(leader_role)
                except Exception as e:
                    print(f"Fehler beim Entfernen der Leader-Rolle: {e}")

            if member_role:
                try:
                    await ctx.user.remove_roles(member_role)
                except Exception as e:
                    print(f"Fehler beim Entfernen der Member-Rolle: {e}")

            embed = nextcord.Embed(
                title='✅ Goodbye!',
                description=f'You have left the clan **`{clan_name}`**.',
                color=nextcord.Colour.green()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return

    embed = nextcord.Embed(
        title='❌ Error',
        description='**`You are not a member of any clan.`**',
        color=nextcord.Colour.red()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

# 🪪 /claninvite
class InviteConfirmationView(nextcord.ui.View):
    def __init__(self, user, clan_name):
        super().__init__()
        self.user = user
        self.clan_name = clan_name.lower()

    @nextcord.ui.button(label="Accept ✅", style=nextcord.ButtonStyle.success, custom_id="accept_invite")
    async def accept_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        member_role = None
    
        if self.clan_name in clan_data:
            clan_info = clan_data[self.clan_name]
            guild_id = clan_info.get('guild_id')
    
            if guild_id:
                guild = bot.get_guild(guild_id)
    
                if guild:
                    member_role_id = clan_info.get('member_role_id')
                    if member_role_id:
                        member_role = guild.get_role(member_role_id)
    
                    if member_role:
                        await self.user.add_roles(member_role)
                        embed = nextcord.Embed(
                            title='✅ Success',
                            description=f'You have joined the clan **`{self.clan_name}`**. The role **`{member_role.name}`** has been assigned to you.',
                            color=nextcord.Colour.green()
                        )
                        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
    
                        clan_data[self.clan_name]['members'].append(self.user.name)
                        save_clan_data()
                    else:
                        embed = nextcord.Embed(
                            title='❌ Error',
                            description='**`The role could not be found. Please contact an administrator.`**',
                            color=nextcord.Colour.red()
                        )
                        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = nextcord.Embed(
                        title='❌ Error',
                        description='**`The clan guild could not be found. Please contact an administrator.`**',
                        color=nextcord.Colour.red()
                    )
                    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = nextcord.Embed(
                    title='❌ Error',
                    description='**`The Guild-ID for this clan was not found. Please contact an administrator.`**',
                    color=nextcord.Colour.red()
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            nextcord.Embed(
                title='❌ Error',
                description='**`Clan not found`.**',
                color=nextcord.Colour.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.ui.button(label="Decline ❌", style=nextcord.ButtonStyle.red, custom_id="decline_invite")
    async def decline_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title='❌ Error',
            description='**`You declined the Invite.`**',
            color=nextcord.Colour.red()
            )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(
    name='claninvite',
    description='🪪 Invite Users to your Clan!'
)
@log_command('claninvite')
async def claninvite(ctx, invited_user: nextcord.User):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)

    if player_data is None or not player_data:
        embed = nextcord.Embed(
            title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    invited_user_data = await load_player_data(invited_user.name)
    if invited_user_data is None or not invited_user_data:
        embed = nextcord.Embed(
            title=f"❌ **`{invited_user.name} doesn't have an active profile!`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return

    with open('rpg_clandata.json', 'r') as f:
        clan_data = json.load(f)

    clan_name = None
    for clan_entry in clan_data.values():
        if player_name in clan_entry['members']:
            clan_name = clan_entry['clan_name']
            break

    if not clan_name:
        embed = nextcord.Embed(
            title="❌ **`You are not a member of any clan!`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return

    for clan_data_entry in clan_data.values():
        if invited_user.name == clan_data_entry['leader_id'] or invited_user.name in clan_data_entry['members']:
            embed = nextcord.Embed(
                title='❌ Error',
                description=f'{invited_user.mention} **`is already a leader or member of another clan. Ask him to leave / delete his active clan so he can join.`**',
                color=nextcord.Colour.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)
            return

    if clan_name in clan_data and len(clan_data[clan_name]['members']) >= 50:
        embed = nextcord.Embed(
            title="❌ **`Clan is Full!`**",
            description="**`The clan you're trying to invite to already has the maximum number of members.`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    leader_role_name = f'👑 {clan_name} - Leader'
    member_role_name = f'🧑🏻 {clan_name} - Member'

    leader_role = nextcord.utils.get(ctx.guild.roles, name=leader_role_name)
    member_role = nextcord.utils.get(ctx.guild.roles, name=member_role_name)

    if not leader_role or not member_role:

        leader_role = await ctx.guild.create_role(name=leader_role_name)
        member_role = await ctx.guild.create_role(name=member_role_name)

    embed = nextcord.Embed(
        title=f'📩 Clan Invitation',
        description=f'**You have been invited to join the** **`{clan_name}`** **clan. Would you like to accept the invitation?**',
        color=nextcord.Colour.green()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    view = InviteConfirmationView(invited_user, clan_name)
    await invited_user.send(embed=embed, view=view)

    confirmation_embed = nextcord.Embed(
        title='✅ Success',
        description=f'An invitation has been sent to {invited_user.mention} to join the clan **`{clan_name}`**.\nBe aware that the Server you send the Invite is Important.',
        color=nextcord.Colour.green()
    )
    confirmation_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=confirmation_embed, ephemeral=True)


# 📛 /clanban
@bot.slash_command(
    name='clanban',
    description='📛 Ban a Clan Member'
)
@log_command('clanban')
async def clanban(ctx, user: nextcord.User, *, reason: str = None):
    clan_name = None
    clan_leader_id = None
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
   
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
    
    for name, data in clan_data.items():
        if ctx.user.name == data['leader_name']:
            clan_name = name
            clan_leader_id = data['leader_name']
            if user.name in data['members']:
                data['members'].remove(user.name)
                data['banned_players'].append(user.name)
                save_clan_data()
                if reason:
                    embed = nextcord.Embed(
                        title=f'🔨 Banned from Clan',
                        description=f'**{user.mention}**! You got BANNED from the **`{name}`** clan by **{ctx.user.mention}**.\nReason: **`{reason}`**',
                        color=nextcord.Colour.red()
                    )
                    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                else:
                    embed = nextcord.Embed(
                        title=f'🔨 Banned from Clan',
                        description=f'**{user.mention}** has been banned from the **`{name}`** clan by **{ctx.user.mention}**.',
                        color=nextcord.Colour.red()
                    )
                    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            member_role = nextcord.utils.get(ctx.guild.roles, name=f'🧑🏻 {clan_name} - Member')
            if member_role:
                await ctx.user.remove_roles(member_role)

                await user.send(embed=embed)
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)
                return
            else:
                embed = nextcord.Embed(
                    title='❌ Error',
                    description=f'{user.mention} is not a member of your clan.',
                    color=nextcord.Colour.red()
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)
                return

    if clan_name is None:
        embed = nextcord.Embed(
            title='❌ Error',
            description='You are not a member of any clan.',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
    elif ctx.user.name != clan_leader_id:
        embed = nextcord.Embed(
            title='❌ Error',
            description='Only clan leaders can ban members from this clan.',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# ✅ /clanunban
@bot.slash_command(
    name='clanunban',
    description='✅ Unban a Clan Member'
)
@log_command('clanunban')
async def clanunban(ctx, user: nextcord.User):
    clan_name = None
    clan_leader_name = None
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
   
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
    
    for name, data in clan_data.items():
        if ctx.user.name == data['leader_name']:
            clan_name = name
            clan_leader_name = data['leader_name']
            if user.name in data['banned_players']:
                data['banned_players'].remove(user.name)
                data['members'].append(user.name)
                save_clan_data()

                embed = nextcord.Embed(
                    title=f'🔓 Unbanned from Clan',
                    description=f'**{user.mention}** has been unbanned from the **`{name}`** clan by **{ctx.user.mention}**.',
                    color=nextcord.Colour.green()
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)

                await user.send(embed=embed)
                await ctx.send(embed=embed, ephemeral=True)
                return
            else:
                embed = nextcord.Embed(
                    title='❌ Error',
                    description=f'{user.mention} is not banned from your clan.',
                    color=nextcord.Colour.red()
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)
                return

    if clan_name is None:
        embed = nextcord.Embed(
            title='❌ Error',
            description='You are not a member of any clan.',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

    elif ctx.user.name != clan_leader_name:
        embed = nextcord.Embed(
            title='❌ Error',
            description='Only clan leaders can unban members from this clan.',
            color=nextcord.Colour.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# -------------
# ITEM SYSTEM:

@dataclass
class Enchanting:
    name: str
    level: int
    description: str

@dataclass
class Item:
    name: str
    value: int
    rarity: str
    durability: int = field(default=None)
    enchantments: Optional[List[Enchanting]] = field(default_factory=list)

    def __post_init__(self):
        default_durabilities = {
            "Basic": 100,
            "Rare": 250,
            "Epic": 500,
            "Legendary": 950,
            "Mythic": 2500,
            "Secret": 3000,
            "Exclusive": 22222,
            "Admin": 1000000,
        }
        if self.durability is None:
            self.durability = default_durabilities.get(self.rarity, 100)

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value,
            'rarity': self.rarity,
            'durability': self.durability,
            'enchantments': [{'name': e.name, 'level': e.level, 'description': e.description} for e in self.enchantments]
        }

def load_enchantments():
    file_path = "C:\\Users\\heypa\\rpg_botdata\\rpg_enchants.json"
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as file:
            try:
                return [Enchanting(**enchant) for enchant in json.load(file)]
            except json.JSONDecodeError:
                return []
    else:
        return []

def item_exists(name: str, items: List[Item]) -> bool:
    return any(item.name == name for item in items)

def load_items():
    file_path = "C:\\Users\\heypa\\rpg_botdata\\rpg_items.json"
    if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r') as file:
            try:
                serialized_items = json.load(file)
                items = []
                for item_data in serialized_items:
                    item = Item(name=item_data['name'], value=item_data['value'], rarity=item_data['rarity'], durability=item_data.get('durability', 100))
                    enchantments_data = item_data.get('enchantments', [])
                    enchantments = [Enchanting(**e) for e in enchantments_data]
                    item.enchantments = enchantments
                    items.append(item)
                return items
            except json.JSONDecodeError:
                return []
    else:
        return []

def save_items(items):
    serialized_items = [item.to_dict() for item in items]
    with open('rpg_items.json', 'w') as file:
        json.dump(serialized_items, file, indent=4)

def get_rarity_color(rarity):
            rarity_colors = {
            "Basic": nextcord.Color.dark_gray(),
            "Rare": nextcord.Color.green(),
            "Epic": nextcord.Color.gold(),
            "Legendary": nextcord.Color.orange(),
            "Mythic": nextcord.Color.from_rgb(255,204,0),
            "Secret": nextcord.Color.from_rgb(26, 26, 26),
            "Exclusive": nextcord.Color.purple(),
            "Admin": nextcord.Color.dark_red(),
    }
            return rarity_colors.get(rarity, nextcord.Color.default())

# 🍁 /additem 
@bot.slash_command(
    name='additem',
    description='🍁 Add an item.'
)
@log_command('additem')
async def additem(ctx, name: str, value: int, rarity: str = nextcord.SlashOption(
        name="rarity",
        description="Select the rarity level.",
        choices={"Basic": "Basic", "Rare": "Rare", "Epic": "Epic", "Legendary": "Legendary", "Mythic": "Mythic", "Secret": "Secret", "Exclusive": "Exclusive", "Admin": "Admin"},
        required=True
), durability: int = 100, enchantment: str = nextcord.SlashOption(
        name="enchantment",
        description="Select an enchantment.",
        choices={"Fire": "fire", "Frost": "frost", "Healing": "healing", "Strength": "strength", "Vulnerability": "vulnerability", "Damage": "damage", "Healing": "healing", "Speed": "speed", "Invisibility": "invisibility", "Fortune": "fortune", "Teleportation": "teleportation"},
        required=False
), enchantment_level: int = nextcord.SlashOption(
        name="enchantment_level",
        description="Select the enchantment level.",
        choices={1: "1", 2: "2", 3: "3",4: "4", 5: "5", 6: "6",7: "7", 8: "8", 9: "9", 10: "10"},
        required=False
)):
    max_gold_value = 10000000
    if value > max_gold_value:
        value = max_gold_value
        embed = nextcord.Embed(
            title=f"⚠️ The specified value exceeds the maximum gold value of **`{max_gold_value}`** gold. The value has been set to the limit of **`{max_gold_value}`**.",
            color=nextcord.Color.gold()
        )
        embed.set_footer(text="❄️ | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    existing_items = load_items()
    if item_exists(name, existing_items):
        embed = nextcord.Embed(
            title=f"❌ An item with the name '{name}' already exists.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="❄️ | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return
    else:
        new_item = Item(name=name, value=value, rarity=rarity, durability=durability)

        enchantments = load_enchantments()

        if enchantment:
            enchantment = enchantment.lower()
            if enchantment not in {e.name.lower() for e in enchantments}:
                embed = nextcord.Embed(
                    title=f"❌ Invalid enchantment '{enchantment}'.",
                    color=nextcord.Color.red()
                )
                embed.set_footer(text="❄️ | @prodbyeagle", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)
                return

        if enchantment:
            selected_enchant = next(e for e in enchantments if e.name.lower() == enchantment)
            enchant_level = enchantment_level or 1
            new_item.enchantments.append(Enchanting(name=selected_enchant.name, level=enchant_level, description=selected_enchant.description))

        existing_items.append(new_item)
        save_items(existing_items)

    rarity_color = get_rarity_color(rarity)
    enchantment_info = f" Enchanted with **`{enchantment}`** **`{enchantment_level}`**." if enchantment else ""
    embed = nextcord.Embed(
        title="✅ Item Added",
        description=f"The item **`{name}`** has been successfully added with rarity **`{rarity}`**, gold value 🪙 **`{value}`**, durability **`{durability}`**.{enchantment_info}",
        color=rarity_color
    )
    embed.set_footer(text="❄️ | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

# 🔨 /testadditem  
@bot.slash_command(
    name='testadditem',
    description='🔨 Add test items.'
)
@log_command('testadditem')
async def testadditem(ctx):
    items_to_add = [
        ("Item 1", 1000, "Basic"),
        ("Item 2", 2000, "Rare"),
        ("Item 3", 3000, "Epic"),
        ("Item 4", 4000, "Legendary"),
        ("Item 5", 5000, "Mythic"),
        ("Item 6", 6000, "Secret"),
        ("Item 7", 70000, "Exclusive"),
        ("Item 8", 80000, "Admin"),
    ]

    existing_items = load_items()
    added_items = []
    error_messages = []

    for item_data in items_to_add:
        name, value, rarity = item_data

        if item_exists(name, existing_items):
            error_messages.append(f"❌ An item with the name '{name}' already exists.")
            continue

        new_item = Item(name, value, rarity)
        added_items.append(new_item)

    message_objects = []

    for item in added_items:
        rarity_color = get_rarity_color(item.rarity)
        embed = nextcord.Embed(
            title="Item Added",
            description=f"✅ The item **`{item.name}`** has been successfully added with **`{item.rarity}`** and gold value 🪙 **`{item.value}`**.",
            color=rarity_color
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        message = await ctx.send(embed=embed)
        message_objects.append(message)

    for error_message in error_messages:
        error_message_obj = await ctx.send(error_message)
        message_objects.append(error_message_obj)

    question_embed = nextcord.Embed(title="🤔 Test Passed?", description="Did the tests run successfully?")
    question_message = await ctx.send(embed=question_embed)
    await question_message.add_reaction("✅")
    await question_message.add_reaction("❎")

    def check(reaction, user):
        return user == ctx.user and str(reaction.emoji) in ["✅", "❎"] and reaction.message.id == question_message.id

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
        if str(reaction.emoji) == "✅":
            success_message = await ctx.send("✅ Test passed")
            message_objects.append(success_message)
        else:
            failure_message = await ctx.send("❌ Test failed.")
            message_objects.append(failure_message)
    except asyncio.TimeoutError:
        timeout_message = await ctx.send("⚠️ Test skipped because there wasn't an answer.")
        message_objects.append(timeout_message)

    await question_message.delete()

    for message in message_objects:
        await message.delete()

# ⛔ /deleteitem  
@bot.slash_command(
    name='deleteitem',
    description='⛔ Delete an item.'
)
@log_command('deleteitem')
async def deleteitem(ctx, name: str):
    existing_items = load_items()
    if not item_exists(name, existing_items):
        embed = nextcord.Embed(
            title=f"An item with the name **`{name}`** does not exist.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    existing_items = [item for item in existing_items if item.name != name]
    save_items(existing_items)

    embed = nextcord.Embed(
        title="Item Deleted",
        description=f"The item **`{name}`** has been deleted.",
        color=nextcord.Color.green()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

# 📝 /itemlist  
@bot.slash_command(
    name='itemlist',
    description='📝 View all Items.'
)
@log_command('itemlist')
async def itemlist(ctx):   
    player_name = ctx.user.name
    player_data = await load_player_data(player_name) 
 
    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
   
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
 
    if ctx.guild is None:
        embed = nextcord.Embed(
            title="⛔ Command Error",
            description="This command can only be used in Chill Lounge text channels.",
            color=0xFF5733
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    embed = nextcord.Embed(
        title="See all Items",
        url="https://chilladventures.gitbook.io/chill-adventures/game-stuff/items",
        color=nextcord.Color.magenta()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

# 📊 /iteminfo
@bot.slash_command(
    name='iteminfo',
    description='📊 Look at the Stats from all the Items!'
)
@log_command('iteminfo')
async def item(ctx, item_name: str):
    existing_items = load_items()
    selected_item = next((item for item in existing_items if item.name.lower() == item_name.lower()), None)
    player_name = ctx.user.name
    player_data = await load_player_data(player_name) 

    if player_data is None or not player_data:
        embed = nextcord.Embed(
        title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
        color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return
   
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
 
    if selected_item:
        embed = nextcord.Embed(
            title=f"⚙️ Item Stats: {selected_item.name}",
            description=f"**💎 Rarity:** {selected_item.rarity}\n"
                        f"**⛓️ Durability:** {selected_item.durability}\n"
                        f"**🪙 Value:** {selected_item.value}\n"
                        f"**👑 Enchantments:** {', '.join([f'{e.name} {e.level}' for e in selected_item.enchantments]) if selected_item.enchantments else '❌'}",
            color=get_rarity_color(selected_item.rarity)
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title=f"❌ Item not found",
            description=f"No item with the name '{item_name}' was found.",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# 💁🏻 /giveitem 
@bot.slash_command(
    name='giveitem',
    description='💁🏻 Gives an item!'
)
@log_command('giveitem')
async def giveitem(ctx, amount: int, itemname: str):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
    
    with open('rpg_items.json') as f:
        items_data = json.load(f)
    
    item_data = next((item for item in items_data if item['name'] == itemname), None)
    
    if item_data is None:
        embed = nextcord.Embed(description=f'❌ The item "{itemname}" does not exist.', color=nextcord.Color.red())
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return
    
    player_inventory = player_data.get('inventory', {})
    
    if itemname in player_inventory:
        player_inventory[itemname]['durability'] = item_data.get('durability', 0)
    else:
        player_inventory[itemname] = {
            "name": item_data['name'],
            "rarity": item_data['rarity'],
            "durability": item_data.get('durability', 0),
            "enchantments": item_data['enchantments'],
            "amount": amount
        }
    
    player_data['inventory'] = player_inventory

    embed = nextcord.Embed(
        title="✅ Success",
        description=f"Added {amount}x \"{itemname}\" to your inventory!",
        color=nextcord.Color.green()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)
    await save_player_data(player_name, player_data)

# -------------
# STORY & GAMES:

# 🧩 /dailyquiz
with open('rpg_dailyquiz.json', 'r', encoding='utf-8') as file:
    questions = json.load(file)

def has_day_passed(last_quiz_attempt):
    current_time = time.time()
    return current_time - last_quiz_attempt >= 86400

class DailyQuizModal(nextcord.ui.Modal):
    def __init__(self, bot, question, correct_answer, gold_reward, xp_reward, last_quiz_attempt, is_developer):
        super().__init__(
            f"Daily Quiz: {question}",
        )
        self.bot = bot
        self.correct_answer = correct_answer
        self.gold_reward = gold_reward
        self.xp_reward = xp_reward
        self.last_quiz_attempt = last_quiz_attempt
        self.is_developer = is_developer

        if is_developer:
            placeholder_text = f" Correct Answer: {self.correct_answer}"
        else:
            placeholder_text = ""

        label_text = f"❓ Please enter your Answer:"

        self.answer_input = nextcord.ui.TextInput(
            label=label_text,
            placeholder=placeholder_text,
            min_length=1,
            max_length=500,
        )
        self.add_item(self.answer_input)

    async def callback(self, interaction: nextcord.Interaction):
        answer_text = self.answer_input.value
    
        if answer_text == self.correct_answer:
            embed = nextcord.Embed(
                title="✅ Correct Answer!",
                description=f"Your answer was correct. Here is your reward:"
            )
            embed.add_field(name="🪙 Gold Reward", value=f"{self.gold_reward} gold", inline=True)
            embed.add_field(name="❇️ XP Reward", value=f"{self.xp_reward} XP", inline=True)
    
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
            player_name = interaction.user.name
            player_data = await load_player_data(player_name)
            player_data["gold"] += self.gold_reward
            player_data["xp"] += self.xp_reward
            player_data["last_quiz_attempt"] = time.time()
            await save_player_data(player_name, player_data)
        else:
            wrong_embed = nextcord.Embed(
                title="Wrong Answer!",
                description=f"❌ The correct answer was: {self.correct_answer}"
            )
            await interaction.response.send_message(embed=wrong_embed, ephemeral=True)

@bot.slash_command(
    name='dailyquiz',
    description='🧩 Take a daily quiz (Reset every 24 Hours)'
)
@log_command('dailyquiz')
async def dailyquiz(interaction: nextcord.Interaction):
    player_name = interaction.user.name
    player_data = await load_player_data(player_name)
    last_quiz_attempt = player_data.get("last_quiz_attempt", 0)
    is_developer = any(role.name == DEVELOPER_RANK for role in interaction.user.roles)

    if not has_day_passed(last_quiz_attempt):
        cooldown_time_left = round(86400 - (time.time() - last_quiz_attempt))
        
        unix_timestamp_next_quiz = int(time.time() + cooldown_time_left)

        next_quiz_embed = nextcord.Embed(
            title="❌ Hey!",
            description=f"The next quiz will be available in <t:{unix_timestamp_next_quiz}:R>",
            color=0x3498db
        )
        await interaction.response.send_message(embed=next_quiz_embed, ephemeral=True)
        return

    question = random.choice(questions)
    gold_reward = random.randint(1000, 50000)
    xp_reward = random.randint(1000, 2500)

    dailyquiz_modal = DailyQuizModal(bot, question["question"], question["answer"], gold_reward, xp_reward, last_quiz_attempt, is_developer)
    await interaction.response.send_modal(dailyquiz_modal)

# 🐟 /fish
class FishingView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.message = None
        self.current_rod_index = 0

    @nextcord.ui.button(label="🎣 Switch Rod", style=nextcord.ButtonStyle.gray)
    async def switch_rod_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        player_name = self.ctx.user.name
        player_data = await load_player_data(player_name)
        fishing_rods = ["Fishing Rod", "Pro Fishing Rod", "Broken Fishing Rod", "Admin Fishing Rod"]
        available_rods = [rod for rod in fishing_rods if rod in player_data.get("inventory", {})]

        if not available_rods:
            await interaction.response.edit_message(content="You don't have any fishing rods in your inventory.")
            return

        self.current_rod_index = (self.current_rod_index + 1) % len(available_rods)
        selected_rod = available_rods[self.current_rod_index]

        player_data['active_rod'] = {"name": selected_rod}
        await save_player_data(player_name, player_data)

        await interaction.response.edit_message(content=f"Current Rod: {selected_rod}")

    @nextcord.ui.button(label="🎣 Fish", style=nextcord.ButtonStyle.green)
    async def fish_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        player_name = self.ctx.user.name
        player_data = await load_player_data(player_name)

        used_rod = player_data.get('active_rod', {}).get('name')

        if used_rod not in player_data.get("inventory", {}):
            embed = nextcord.Embed(title="🪝Fish", description="**`Your active fishing rod is not present in your inventory.`**", color=0xFF0000)
            await self.ctx.send(embed=embed, ephemeral=True)
            return

        last_fish_time = player_data.get("last_fish_time", 0)
        current_time = time.time()

        chances = {
            "Admin Fishing Rod": {"Basic": 0, "Rare": 0, "Epic": 0, "Legendary": 0, "Secret": 50, "Mythic": 50},
            "Pro Fishing Rod": {"Basic": 10, "Rare": 30, "Epic": 20, "Legendary": 10, "Secret": 5, "Mythic": 1},
            "Fishing Rod": {"Basic": 20, "Rare": 20, "Epic": 10, "Legendary": 2, "Secret": 1, "Mythic": 0.1},
            "Broken Fishing Rod": {"Basic": 40, "Rare": 20, "Epic": 10, "Legendary": 5, "Secret": 0.5, "Mythic": 0},
        }

        cooldown_reduction_percent = 0
    
        if "Reduce Fishing Cooldown" in player_data.get("masteries", {}):
            mastery_data = player_data["masteries"]["Reduce Fishing Cooldown"]
            cooldown_reduction_percent = min(mastery_data.get("current_level", 0) * 10, 60)
    
        base_cooldown = 3600
        cooldown_after_reduction = base_cooldown - (base_cooldown * cooldown_reduction_percent / 100)
        countdown_seconds = max(0, last_fish_time + cooldown_after_reduction - current_time)

        unix_timestamp_next_fish = int(current_time + countdown_seconds)

        if current_time - last_fish_time < cooldown_after_reduction:
            embed = nextcord.Embed(title="🕰️ Cooldown!", description=f"**`🎣 You can fish again in`** <t:{unix_timestamp_next_fish}:R>", color=0xFF0000)
            await interaction.response.edit_message(embed=embed)
            return
        else:
            player_data["last_fish_time"] = current_time

            fishing_rods = ["Fishing Rod", "Pro Fishing Rod", "Broken Fishing Rod"]

            self.current_rod_index = (self.current_rod_index + 1) % len(fishing_rods)

            used_rod = player_data.get('active_rod', {}).get('name')
            banned_rarities = ["Exclusive", "Admin"]
            allowed_rarities = [rarity for rarity in chances[used_rod] if rarity not in banned_rarities]

            caught_item = None
            can_fish = random.random()
            
            if can_fish < 0.5:
                caught_item = random.choice(load_items())

                while caught_item is None:
                    candidate_item = random.choice(load_items())
    
                    if candidate_item.rarity not in allowed_rarities:
                        continue
    
                    caught_item = candidate_item
    
                    player_data["inventory"][used_rod]["durability"] -= 1
                
                    if player_data["inventory"][used_rod]["amount"] > 1 and player_data["inventory"][used_rod]["durability"] <= 0:
                        player_data["inventory"][used_rod]["amount"] -= 1
                        player_data["inventory"][used_rod]["durability"] = 100
                
                    if player_data["inventory"][used_rod]["durability"] <= 0:
                        del player_data["inventory"][used_rod]
                        embed = nextcord.Embed(title="🎣 Fish", description="**`Your fishing rod broke!`**", color=0xFF0000)
                        await self.ctx.send(embed=embed)
    
                    fortune_enchantment = None
                    for enchantment in player_data.get("active_rod", {}).get("enchantments", []):
                        if enchantment.get("name") == "Fortune":
                            fortune_enchantment = enchantment
                            break
    
                    if fortune_enchantment:
                        for rarity, chance in chances[used_rod].items():
                            chances[used_rod][rarity] += fortune_enchantment.get("level") * 5
    
                    if caught_item:
                        item_name = caught_item.name
                
                        if item_name in player_data["inventory"]:
                            player_data["inventory"][item_name]["amount"] += 1
                        else:
                            player_data["inventory"][item_name] = {
                                "name": item_name,
                                "value": caught_item.value,
                                "durability": caught_item.durability,
                                "amount": 1,
                                "enchantments": []
                            }
                
                        embed = nextcord.Embed(title="🎣 Fish", description=f"**`You caught a item and got {item_name}!`**", color=0x00FF00)
            else:
                embed = nextcord.Embed(title="🎣 Fish", description="**`You didn't catch any item this time.`**", color=0xFF0000)
            
                await interaction.response.edit_message(embed=embed)
                await save_player_data(player_name, player_data)

@bot.slash_command(
    name='fish',
    description='🐟 Fish some Items! (1 per Hour)'
)
@log_command('fish')
async def fish(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name) 

    if player_data is None or not player_data:
        embed = nextcord.Embed(
            title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed)
        return

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    mastery_level = player_data['masteries'].get('Unlock /fish', {}).get('current_level', 0)
    
    if mastery_level < 1:
        embed = nextcord.Embed(
            title="❌ **`You need to upgrade your Unlock /fish mastery to use this command! Click this to visit the Masterys:`** </masterys:1179166654391930931>",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    if not player_data.get("1st_fish_gift", False):
        gift_item = {
            "name": "Broken Fishing Rod",
            "value": 10,
            "rarity": "Basic",
            "durability": 20,
            "enchantments": [],
            "amount": 1            
        }
        player_data["inventory"]["Broken Fishing Rod"] = gift_item
        player_data["1st_fish_gift"] = True
        await save_player_data(player_name, player_data)

        gift_embed = nextcord.Embed(
            title="🎁 First Fish Gift!",
            description="**`Seems like it's your first time fishing. Here is a starter rod. When you can't use the Command Reload.`**",
            color=0xFFD700
        )
        await ctx.send(embed=gift_embed, ephemeral=True)

    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return

    view = FishingView(ctx)
    embed = nextcord.Embed(title="🐟 Fish some Fishes", description="**`Get your rod warm!`**", color=0x0000FF)
    await ctx.send(embed=embed, view=view, ephemeral=True)

# 🗿 /clicker
channel = bot.get_channel(1164691308917559326)

class ClickerView(View):
    def __init__(self, username, player_data, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.player_data = player_data
        self.count = self.load_count()
        self.clicked = False
        self.multiplier = 1
        
    def add_xp(self, xp):
        file_name = f"{self.username}.json"
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                data = json.load(file)
        else:
            data = {}

        data["xp"] = data.get("xp", 0) + xp
    
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def add_gold(self, gold):
        file_name = f"{self.username}.json"
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                data = json.load(file)
        else:
            data = {}

        data["gold"] = data.get("gold", 0) + gold

        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

    def load_count(self):
        file_name = f"{self.username}.json"
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                data = json.load(file)
                return data.get("clicks", 0)
        return 0

    def save_count(self):
        file_name = f"{self.username}.json"
        data = {}
        
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                data = json.load(file)

        data["clicks"] = self.count

        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)
    
    async def perform_event(self, interaction):
        event_chance = random.randint(1, 5000)
        special_role_ids = [1112844728422105149, 1148624320550158490]
        
        has_special_role = False
        
        if interaction.guild:
            member = interaction.guild.get_member(interaction.user.id)
            if member:
                has_special_role = any(role.id in special_role_ids for role in member.roles)
        
        if event_chance <= 2 or (has_special_role and event_chance <= 1000):
            self.count += 750
            self.save_count()
            self.add_xp(500)
            self.add_gold(1000)
        
            embed = nextcord.Embed(
                title="🎀 JACKPOT Clicks",
                description="**`+ 750 clicks! | + 500 XP | + 1000 Gold`**",
                color=0xFF9900
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        
            message = await interaction.followup.send(embed=embed, ephemeral=True)
            await asyncio.sleep(2)
            await message.delete()
        
        elif event_chance <= 20 or (has_special_role and event_chance <= 5000):
            event_type = random.choice(["extraclicks"])
        
            if event_type == "extraclicks":
                self.count += 150
                self.save_count()
                self.add_xp(100)
                self.add_gold(100)
        
                embed = nextcord.Embed(
                    title="🎉 Bonus Clicks",
                    description="**`+ 150 clicks | + 100 XP | + 100 Gold`**",
                    color=0xFF9900
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        
                message = await interaction.followup.send(embed=embed, ephemeral=True)
                await asyncio.sleep(2)
                await message.delete()

    @nextcord.ui.button(label="+ 1 Click", style=nextcord.ButtonStyle.primary)
    async def click_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        user_id = str(interaction.user.id)
        self.check_user_id(user_id)

        if not self.clicked:
            self.clicked = False
            more_clicks_level = self.player_data['masteries'].get('More Clicks', {}).get('current_level', 0)
            clicks_multiplier = 1 + more_clicks_level
            self.count += 1 * self.multiplier * clicks_multiplier
            self.save_count()
            self.add_xp(1 * self.multiplier * clicks_multiplier)
            self.add_gold(2 * self.multiplier * clicks_multiplier)
            embed = self.get_embed()
            await interaction.response.edit_message(embed=embed)

        await self.perform_event(interaction)

    def check_user_id(self, user_id):
        if user_id == "893759402832699392":
            self.multiplier = 1

    def get_embed(self):
        embed = nextcord.Embed(
            title=f"Chilly-Clicker v.2.0 - {self.username}",
            description=f"**You have made** **`{self.count}`** **clicks in Total!**",
            color=0x00ff00
        )
        embed.set_author(name="? +1 XP & +2 Gold")
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        return embed
    
@bot.slash_command(
    name='clicker',
    description='🗿 Click the Button. Thats It!'
)
@log_command('clicker')
async def clicker(ctx):      
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
 
    username = ctx.user.name
    player_data = await load_player_data(username)
    if player_data is not None:
        view = ClickerView(username, player_data)
        await ctx.send(embed=view.get_embed(), view=view, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title="**`❌ You don't have an active profile!`** </start:1178729424854728744> **`to Start`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

# 🥊 /fight
class FightView(View):
    def __init__(self, player1, player2):
        super().__init__()
        self.player1 = player1
        self.player2 = player2
        self.lives1 = 150
        self.lives2 = 150
        self.can_attack = self.player2.id
        self.game_over = False

    def disable_buttons(self):
        for child in self.children:
            if isinstance(child, nextcord.ui.Button):
                child.disabled = True

    async def send_success_message(self, interaction, success_messages):
        try:
            success_message = random.choice(success_messages)
    
            success_embed = nextcord.Embed(
                title="🗡️ Success",
                description=success_message,
                color=0x00FF00
            )
            success_embed.add_field(name="**`🧔🏽‍♂️ Current Player`**", value=self.player2.name if self.can_attack == self.player1.id else self.player1.name, inline=True)
            success_embed.add_field(name=f"**`🫀 {self.player1.name}'s Health`**", value=f"**`{self.lives1} ❤️`**", inline=True)
            success_embed.add_field(name=f"**`🫀 {self.player2.name}'s Health`**", value=f"**`{self.lives2} ❤️`**", inline=True)
            success_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    
            if self.lives1 <= 0 or self.lives2 <= 0:
                self.disable_buttons()
    
            await interaction.response.edit_message(embed=success_embed, view=self)
    
        except nextcord.errors.InteractionResponded:
            print("Fighting sounds: pow, bam, ping, blug | @prodbyeagle")
    
    async def send_failure_message(self, interaction, failure_messages):
        try:
            failure_message = random.choice(failure_messages)
    
            failure_embed = nextcord.Embed(
                title="😭 Failure",
                description=failure_message,
                color=0xFF0000
            )
            failure_embed.add_field(name="**`🧔🏽‍♂️ Current Player`**", value=self.player2.name if self.can_attack == self.player1.id else self.player1.name, inline=True)
            failure_embed.add_field(name=f"**`🫀 {self.player1.name}'s Health`**", value=f"**`{self.lives1} ❤️`**", inline=True)
            failure_embed.add_field(name=f"**`🫀 {self.player2.name}'s Health`**", value=f"**`{self.lives2} ❤️`**", inline=True)
            failure_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    
            if self.lives1 <= 0 or self.lives2 <= 0:
                self.disable_buttons()
    
            await interaction.response.edit_message(embed=failure_embed, view=self)
    
        except nextcord.errors.InteractionResponded:
            print("Fighting sounds: pow, bam, ping, blug | @prodbyeagle")

    async def send_surrender_message(self, interaction):
        try:
            surrender_message = "The player has surrendered. The battle is over!"
    
            if self.can_attack == self.player1.id:
                self.lives1 = 0
            else:
                self.lives2 = 0
            
            surrender_embed = nextcord.Embed(
                title="🏳️ Surrender",
                description=surrender_message,
                color=0x808080
            )
            surrender_embed.add_field(name="**`🧔🏽‍♂️ Current Player`**", value=self.player2.name if self.can_attack == self.player1.id else self.player1.name, inline=True)
            surrender_embed.add_field(name=f"**`🫀 {self.player1.name}'s Health`**", value=f"**`{self.lives1} ❤️`**", inline=True)
            surrender_embed.add_field(name=f"**`🫀 {self.player2.name}'s Health`**", value=f"**`{self.lives2} ❤️`**", inline=True)
            surrender_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    
            if self.lives1 <= 0 or self.lives2 <= 0:
                self.disable_buttons()
    
            await interaction.response.edit_message(embed=surrender_embed, view=self)

        except nextcord.errors.InteractionResponded:
            print("Fighting sounds: pow, bam, ping, blug | @prodbyeagle")
    
    async def update_player_stats(self, winner, loser):
        with open(f"{winner.name}.json", "r") as file:
            data = json.load(file)
            data["fights_won"] += 1
        with open(f"{winner.name}.json", "w") as file:
            json.dump(data, file, indent=4)

        with open(f"{loser.name}.json", "r") as file:
            data = json.load(file)
            data["fights_lost"] += 1
        with open(f"{loser.name}.json", "w") as file:
            json.dump(data, file, indent=4)

    async def update_game(self, interaction):
        if self.lives1 <= 0 or self.lives2 <= 0:
            winner = self.player2 if self.lives1 <= 0 else self.player1
            loser = self.player1 if self.lives1 <= 0 else self.player2
    
            final_message = f"**`The battle has ended!`**\n\n**`{winner.name}`** wins against **`{loser.name}`**!"
            final_embed = nextcord.Embed(
                title="⚔️ Battle Result",
                description=final_message,
                color=0x800080
            )
            final_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(embed=final_embed)
                    await self.update_player_stats(winner, loser)
            except nextcord.errors.InteractionResponded:
                print("Interaction already responded.")

    async def send_stop_message(self, interaction):
        stop_message = nextcord.Embed(
            title="⛔ Stop",
            description="it's the other user's turn.",
            color=0xFF0000
        )
        if not interaction.response.is_done():
            try:
                await interaction.response.send_message(embed=stop_message, ephemeral=True)
            except nextcord.errors.InteractionResponded:
                print("Interaction already responded.")

    @nextcord.ui.button(label="🗡️ Attack", style=nextcord.ButtonStyle.red, custom_id="attack")
    async def attack(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.can_attack == interaction.user.id:
            if random.random() < 0.5:
                damage = 120
                if self.can_attack == self.player1.id:
                    self.lives2 = max(0, self.lives2 - damage)
                else:
                    self.lives1 = max(0, self.lives1 - damage)
                success_messages = [
                    "**`You deftly swung your sword and hit your opponent! 🥊`**",
                    "**`Your attack was so swift, your opponent didn't even see it coming! 🫢`**",
                    "**`Bullseye! Your attack landed perfectly on your opponent! 🎯`**"
                ]
                await self.send_success_message(interaction, success_messages)
            else:
                damage = 6
                if self.can_attack == self.player1.id:
                    self.lives1 = max(0, self.lives1 - damage)
                else:
                    self.lives2 = max(0, self.lives2 - damage)
    
                if self.game_over:
                    await self.update_game(interaction)
                    self.game_over = True
    
                    winner = self.player2 if self.lives1 <= 0 else self.player1
                    loser = self.player1 if self.lives1 <= 0 else self.player2
    
                    await self.update_player_stats(winner, loser)    
    
                failure_messages = [
                    "**`Oops! You tripped over your own shoelaces while trying to attack! 👟`**",
                    "**`You missed your opponent and accidentally hit a nearby tree! 🌳`**",
                    "**`Your attack looked impressive, but it didn't do much damage. Your opponent is fine! 😵`**"
                ]
                await self.send_failure_message(interaction, failure_messages)
            
            self.can_attack = self.player2.id if self.can_attack == self.player1.id else self.player1.id
        else:
            await self.send_stop_message(interaction)
    
        if not self.game_over:
            await self.update_game(interaction)

    @nextcord.ui.button(label="🛡️ Block", style=nextcord.ButtonStyle.blurple, custom_id="block")
    async def block(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.can_attack == interaction.user.id:
            if random.random() < 0.3:
                block_value = 2
                success_messages = [
                    "**`Perfect block with your shield! Your shield taunted your opponent. 🥴`**",
                    "**`Your expert block made your opponent question their life choices. 😵‍💫`**",
                    "**`Your opponent's attack had no effect on you. Your shield taunted them. 😴`**"
                ]
            else:
                block_value = -3
                failure_messages = [
                    "**`Your casual wave of a block didn't stop the attack! 🌊`**",
                    "**`Your block didn't work, and your shield is on vacation. 🏞️`**",
                    "**`Your opponent's attack slipped right through your block! 🧱`**"
                ]
    
            if self.can_attack == self.player1.id:
                self.lives1 = max(0, self.lives1 + block_value)
            else:
                self.lives2 = max(0, self.lives2 + block_value)
    
            if self.game_over:
                await self.update_game(interaction)
                self.game_over = True
    
            if block_value > 0:
                await self.send_success_message(interaction, success_messages)
            else:
                await self.send_failure_message(interaction, failure_messages)
    
            self.can_attack = self.player2.id if self.can_attack == self.player1.id else self.player1.id
        else:
            await self.send_stop_message(interaction)
    
        if not self.game_over:
            await self.update_game(interaction)
    
    @nextcord.ui.button(label="🦶🏻 Kick", style=nextcord.ButtonStyle.green, custom_id="kick")
    async def kick(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.can_attack == interaction.user.id:
            if random.random() < 0.20:
                damage = 120
                if self.can_attack == self.player1.id:
                    self.lives2 = max(0, self.lives2 - damage)
                else:
                    self.lives1 = max(0, self.lives1 - damage)
                success_messages = [
                    "**`Powerful kick! Your opponent went flying! 🐦 `**",
                    "**`Your kick created a gust of wind! Birds joined in for a dance party. 🪩`**",
                    "**`Sneaky kick! Your opponent vanished to another dimension. 🥱`**"
                ]
                await self.send_success_message(interaction, success_messages)
            else:
                damage = 20
                if self.can_attack == self.player1.id:
                    self.lives1 = max(0, self.lives1 - damage)
                else:
                    self.lives2 = max(0, self.lives2 - damage)
    
                if self.game_over:
                    await self.update_game(interaction)
                    self.game_over = True
    
                    winner = self.player2 if self.lives1 <= 0 else self.player1
                    loser = self.player1 if self.lives1 <= 0 else self.player2
    
                    await self.update_player_stats(winner, loser)
    
                failure_messages = [
                    "**`Oops! You slipped and fell on your back. 😓`**",
                    "**`Your kick turned into a silly dance move. The crowd cheered! 😂`**",
                    "**`Slow-motion kick, but your opponent dodged and took a selfie. 📷`**"
                ]
                await self.send_failure_message(interaction, failure_messages)
            self.can_attack = self.player2.id if self.can_attack == self.player1.id else self.player1.id
        else:
            await self.send_stop_message(interaction)
    
        if not self.game_over:
            await self.update_game(interaction)

    @nextcord.ui.button(label="🏥 Heal", style=nextcord.ButtonStyle.green, custom_id="heal")
    async def heal(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.can_attack == interaction.user.id:
            heal_amount = random.randint(5, 15)
            if self.can_attack == self.player1.id:
                self.lives1 += heal_amount
            else:
                self.lives2 += heal_amount
            if self.game_over:
                await self.update_game(interaction)
                self.game_over = True    

            success_messages = [
                f"**`You used a healing potion and regained {heal_amount} health! 🏥`**",
                f"**`Magical healing energy flows through you, restoring {heal_amount} health! 🌟`**",
                f"**`You feel reinvigorated, gaining {heal_amount} health! 💪`**"
            ]
            await self.send_success_message(interaction, success_messages)
            self.can_attack = self.player2.id if self.can_attack == self.player1.id else self.player1.id
        else:
            await self.send_stop_message(interaction)
    
        if not self.game_over:
            await self.update_game(interaction)

    @nextcord.ui.button(label="🏳️ Surrender", style=nextcord.ButtonStyle.grey, custom_id="surrender")
    async def surrender(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.lives1 > 0 and self.lives2 > 0:
            if interaction.user.id == self.can_attack:
                if self.can_attack == self.player1.id:
                    self.lives1 = 0
                else:
                    self.lives2 = 0
    
                if self.game_over:
                    await self.update_game(interaction)
                    self.game_over = True
    
                    winner = self.player2 if self.lives1 <= 0 else self.player1
                    loser = self.player1 if self.lives1 <= 0 else self.player2
    
                    await self.update_player_stats(winner, loser)
        else:
            await self.send_stop_message(interaction)
    
        if not self.game_over:
            await self.update_game(interaction)

@bot.slash_command(
    name='fight',
    description='🥊 Fight for your glory and gold...'
)
@log_command('fight')
async def fight(ctx, opponent: nextcord.Member):
    opponent_name = str(opponent.name)
    player_data = await load_player_data(opponent_name)
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=update_embed, ephemeral=True)
        return
 
    if opponent_name is None or not player_data:
        embed = nextcord.Embed(
            title="❌ **`The opponent doesn't have an active profile!`**",
            color=nextcord.Color.red()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)
        return

    if ctx.user == opponent:
        error_embed = nextcord.Embed(
            title="❗ Nope.",
            description="**`You can't fight yourself!`**",
            color=0xFF0000
        )
        error_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=error_embed, ephemeral=True)
        return

    player1 = opponent
    player2 = ctx.user

    if player1.status in [nextcord.Status.offline, nextcord.Status.idle]:
        notification_message = f"{ctx.user.name} invited you to a duel!"
        notification_embed = nextcord.Embed(title="✉️ Duel Invitation", description=notification_message, color=0x008000)
        notification_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await player1.send(embed=notification_embed)

    view = FightView(player1, player2)

    fight_start_embed = nextcord.Embed(title=f'{player2.name} 1st Hit', description="**`Choose your first hit or block...`**\n\n⚠️ Currently is the Ending Embed broken but the Game works. Just without seeing an Winner Embed. But you will clearly see the winner lol.`**", color=0xFFA500)
    fight_start_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)

    try:
        await ctx.send(embed=fight_start_embed, view=view)
    except nextcord.errors.InteractionResponded:
        print("Everything's fine")

# -------------
# PET SYSTEM
def load_pet_data():
    with open('rpg_petsdata.json', 'r') as file:
        pet_data = json.load(file)
    return pet_data['pets']       
        
class Pet:
    def __init__(self, name, rarity, level=1, xp=0, xp_bonus=0, gold_bonus=0, clicker_bonus=0, fish_bonus=0, fight_bonus=0):
        self.name = name
        self.rarity = rarity
        self.level = level
        self.xp = xp
        self.xp_bonus = xp_bonus
        self.gold_bonus = gold_bonus
        self.clicker_bonus = clicker_bonus
        self.fish_bonus = fish_bonus
        self.fight_bonus = fight_bonus

def create_random_pet(base_pet):
    name = base_pet['name']
    rarity = base_pet['rarity']
    level = 1
    xp = 0

    available_bonuses = ["xp_bonus", "gold_bonus", "clicker_bonus", "fish_bonus", "fight_bonus"]
    selected_bonuses = random.sample(available_bonuses, min(2, len(available_bonuses)))

    xp_bonus = 0
    gold_bonus = 0
    clicker_bonus = 0
    fish_bonus = 0
    fight_bonus = 0

    for bonus in selected_bonuses:
        if bonus == "xp_bonus":
            xp_bonus = random.randint(1, 6)
        elif bonus == "gold_bonus":
            gold_bonus = random.randint(1, 8)
        elif bonus == "clicker_bonus":
            clicker_bonus = random.randint(1, 5)
        elif bonus == "fish_bonus":
            fish_bonus = random.randint(1, 5)
        elif bonus == "fight_bonus":
            fight_bonus = random.randint(1, 5)

    return Pet(name, rarity, level, xp, xp_bonus, gold_bonus, clicker_bonus, fish_bonus, fight_bonus)

def update_pet_level_and_rarity(pet):
    if pet.level >= 250:
        pet.rarity = 'Mythic'
    elif pet.level >= 100:
        pet.rarity = 'Legendary'
    elif pet.level >= 50:
        pet.rarity = 'Epic'
    elif pet.level >= 20:
        pet.rarity = 'Rare'
    elif pet.level >= 10:
        pet.rarity = 'Uncommon'
    elif pet.level >= 5:
        pet.rarity = 'Common'
    elif pet.level >= 1:
        pet.rarity = 'Basic'

# Pet Kauf System
async def purchase_pet(player_name, pet_name):
    player_data = await load_player_data(player_name)
    pet_data = load_pet_data()

    selected_pet = None
    for pet in pet_data:
        if pet['name'] == pet_name:
            selected_pet = pet
            break

    if selected_pet and player_data["gold"] >= selected_pet.get('price', 0):
        player_data["gold"] -= selected_pet.get('price', 0)

        if "pets" not in player_data:
            player_data["pets"] = {}

        new_pet = create_random_pet(selected_pet)
        player_data["pets"][pet_name] = {
            "name": new_pet.name,
            "rarity": new_pet.rarity,
            "level": new_pet.level,
            "xp": new_pet.xp,
            "xp_bonus": new_pet.xp_bonus,
            "gold_bonus": new_pet.gold_bonus,
            "clicker_bonus": new_pet.clicker_bonus,
            "fish_bonus": new_pet.fish_bonus,
            "fight_bonus": new_pet.fight_bonus
        }

        await save_player_data(player_name, player_data)
        return True
    else:
        return False

def get_pet_price(pet_name):
    pet_data = load_pet_data()
    for pet in pet_data:
        if pet['name'] == pet_name:
            return pet.get('price', 0)
    return 0

class AdoptPetButton(nextcord.ui.Button):
    def __init__(self, pet_data, **kwargs):
        super().__init__(**kwargs)
        self.pet_data = pet_data

class AdoptPetView(View):
    def __init__(self, player_data, **kwargs):
        super().__init__(**kwargs)
        self.player_data = player_data

async def adopt_pet_callback(interaction, button, player_data, selected_pet):
    pet_price = get_pet_price(selected_pet['name'])
    player_name = interaction.user.name
    player_data = await load_player_data(player_name)

    if player_data["gold"] >= pet_price:
        if selected_pet['name'] in player_data.get('pets', {}):
            embed = nextcord.Embed(
                title="⚠️ Pet Already Owned",
                description="You already own this pet.",
                color=nextcord.Color.yellow()
            )
            embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        num_pets = len(player_data.get('pets', {}))
        if num_pets >= 2:
            embed = nextcord.Embed(
                title="❌ Max Pets Reached",
                description="You can have a maximum of 2 pets.",
                color=nextcord.Color.red()
            )
            embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        success = await purchase_pet(player_data['name'], selected_pet['name'])

        embed = nextcord.Embed()
        embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link)

        if success:
            player_data["gold"] -= pet_price
            embed = nextcord.Embed(
                title="✅ Success!",
                description=f"You've successfully adopted {selected_pet['name']}!",
                color=nextcord.Color.green()
            )
            embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Error adopting the pet.",
                color=nextcord.Color.red()
            )
            embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title="🪙 Not Enough Gold",
            description=f"You don't have enough gold to adopt this pet. It costs {pet_price}",
            color=nextcord.Color.red()
        )
        embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# 🐶 /adoptpet
@bot.slash_command(
    name='adoptpet',
    description='🐶 Adopt a New Pet!'
)
@log_command('adoptpet')
async def adoptpet(ctx):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)
    pets_data = load_pet_data()

    view = AdoptPetView(player_data)

    embed = nextcord.Embed(title="🐇 Adopt a New Pet", description="Choose a pet to adopt!")

    for pet in pets_data:
        embed.add_field(
            name=f"{pet['name']} ({pet['rarity']})", 
            value=f"Price: {pet.get('price', 0)} gold",
            inline=True
        )
        embed.set_footer(text=f"You have {player_data['gold']} Gold | @prodbyeagle", icon_url=pic_link) 

        button = AdoptPetButton(style=nextcord.ButtonStyle.primary, label=pet['name'], pet_data=pet)
        button.callback = lambda i, p=pet: adopt_pet_callback(i, button, player_data, p)

        view.add_item(button)

    await ctx.send(embed=embed, view=view, ephemeral=True)

# 🦍 /equippet
@bot.slash_command(
    name='equippet',
    description='🦍 Equip a Pet!'
)
@log_command('equippet')
async def equippet(ctx, pet_name: str):
    if pet_name is not None and pet_name.lower() != "none":
        player_name = ctx.user.name
        player_data = await load_player_data(player_name)

        if "active_pets" not in player_data:
            player_data["active_pets"] = {}

        if pet_name in player_data["pets"]:
            if player_data["active_pets"]:
                old_pet_name = next(iter(player_data["active_pets"]))
                player_data["pets"][old_pet_name] = player_data["active_pets"].pop(old_pet_name)
                embed = nextcord.Embed(
                    title="✅ Equipped Pet!",
                    description=f"Pet Equipped: {pet_name}",
                    color=nextcord.Color.orange()
                )
                embed.set_footer(text=f"You've put back {old_pet_name}.")
                await ctx.send(embed=embed)

            player_data["active_pets"][pet_name] = player_data["pets"].pop(pet_name)
            await save_player_data(player_name, player_data)

            embed = nextcord.Embed(
                title="Pet Equipped",
                description=f"You've equipped {pet_name}!",
                color=nextcord.Color.green()
            )
            await ctx.send(embed=embed)

        else:
            embed = nextcord.Embed(
                title="Pet Not Found",
                description=f"You don't have a pet named {pet_name}.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=embed)
    else:

        player_name = ctx.user.name
        player_data = await load_player_data(player_name)

        if "active_pets" in player_data and player_data["active_pets"]:

            old_pet_name = next(iter(player_data["active_pets"]))
            player_data["pets"][old_pet_name] = player_data["active_pets"].pop(old_pet_name)
            await save_player_data(player_name, player_data)

            embed = nextcord.Embed(
                title="✅ Equipped Pet!",
                description=f"Pet Equipped: None",
                color=nextcord.Color.orange()
            )
            embed.set_footer(text=f"You've put back {old_pet_name}.")
            await ctx.send(embed=embed)
        else:
            embed = nextcord.Embed(
                title="No Active Pet",
                description="You don't have any active pet.",
                color=nextcord.Color.orange()
            )
            await ctx.send(embed=embed)

AFK_XP_BASE = 5
AFK_GOLD_BASE = 10
AFK_FARM_INTERVAL = 1
PET_POINT_CHANCE = 0.05

# 🦍 /afk
@bot.slash_command(
    name='afk',
    description='AFK Test'
)
@log_command('afk')
async def afk_rewards_task(self):
    all_users = await get_all_player_names()

    for player_name in all_users:
        player = nextcord.Guild.fetch_members(self)
        print(f"{player}")

        if player.status in [nextcord.Status.offline, nextcord.Status.idle]:
            print(f"{player.name} started AFK farming.")

            player_data = await load_player_data(player_name)

            total_xp = AFK_XP_BASE
            total_gold = AFK_GOLD_BASE
            pet_point = 0

            if "active_pets" in player_data:
                for pet_name, pet_info in player_data["active_pets"].items():
                    pet_level = pet_info["level"]
                    xp_bonus = pet_info["xp_bonus"]
                    gold_bonus = pet_info["gold_bonus"]
                    cooldown_reduction = min(pet_level // 10, 5)

                    xp_bonus *= min(pet_level, 8)
                    gold_bonus *= min(pet_level, 8)

                    cooldown = max(60 - cooldown_reduction * 10, 10)

                    earned_xp = pet_level * xp_bonus
                    earned_gold = pet_level * gold_bonus

                    total_xp += earned_xp
                    total_gold += earned_gold

                    pet_info["xp"] += pet_level * 2

                    if random.random() < PET_POINT_CHANCE:
                        pet_point += 1

                    print(f"{player_name}'s pet {pet_name} earned {earned_xp} XP and {earned_gold} Gold.")

            else:
                continue

            player_data["xp"] += total_xp
            player_data["gold"] += total_gold
            player_data["pet_points"] = player_data.get("pet_points", 0) + pet_point

            await save_player_data(player_name, player_data)

            if player_name.status in [nextcord.Status.online]:
                message = f"During your AFK time, your pets earned you {total_xp} XP and {total_gold} Gold."
                if pet_point > 0:
                    message += f"\nYou also received {pet_point} pet point(s)!"
                await self.user.send(message)
# -------------
# ADMIN CMDS:

ACTIVE_CODES_FILE = 'rpg_activecodes.json'

@bot.slash_command(
    name='generatecodes',
    description='🟪 Generate Merch Codes (Exclusives)'
)
@log_command('generatecodes')
async def generatecodes(ctx, amount: int):
    if amount > 99:
        await ctx.send('Sorry, that`s too much! Please generate 99 codes or fewer.', ephemeral=True)
        return
    try:
        with open(ACTIVE_CODES_FILE, 'r') as file:
            existing_data = json.load(file)
            existing_used_codes = existing_data.get('used', [])
    except FileNotFoundError:
        existing_used_codes = []

    codes = []

    for _ in range(amount):
        random_order = random.sample(string.ascii_uppercase + string.digits, len(string.ascii_uppercase + string.digits))
        code = f'CL-{"".join(random.sample(random_order, k=3))}-{"".join(random.sample(random_order, k=4))}-{"".join(random.sample(random_order, k=5))}'
        codes.append(code)

    used_codes = existing_used_codes

    with open(ACTIVE_CODES_FILE, 'w') as file:
        json.dump({'codes': codes}, file, indent=4)

    with open(ACTIVE_CODES_FILE, 'r') as file:
        data = json.load(file)
        data['used'] = used_codes

    with open(ACTIVE_CODES_FILE, 'w') as file:
        json.dump(data, file, indent=4)

    if amount > 10:
        await ctx.send(f'Successfully generated {amount} codes.', ephemeral=True)
    else:
        embed = nextcord.Embed(title=f'CL - RPG Codes', color=0x00ff00)
        embed.add_field(name='Number of Codes', value=len(codes), inline=False)

        for code in codes:
            embed.add_field(name='Code', value=code, inline=False)

        await ctx.send(embed=embed, ephemeral=True)

# 👾 /bug
try:
    with open("rpg_bugvalue.json", "r") as file:
        data = json.load(file)
        bugcounter = data.get("bugcounter", 0)
except FileNotFoundError:
    bugcounter = 0

class BugModal(nextcord.ui.Modal):
    def __init__(self, bot, bug_id):
        super().__init__(
            "Submit a Bug!",
        )
        self.bot = bot
        self.bug_id = bug_id

        self.name = nextcord.ui.TextInput(
            label="Give the Bug an Title!",
            min_length=2,
            max_length=50,
        )
        self.add_item(self.name)

        self.description = nextcord.ui.TextInput(
            label="Description",
            style=nextcord.TextInputStyle.paragraph,
            placeholder="Describe your Bug.",
            required=True,
            max_length=1800,
        )
        self.add_item(self.description)

    async def callback(self, interaction: nextcord.Interaction):
        global bugcounter

        bug_text = self.description.value

        bug_channel = self.bot.get_channel(BUG_CHANNEL)
        if bug_channel:
            bugcounter += 1
            bugembed = nextcord.Embed(
                title=f'❓ | {bugcounter} | {self.name.value}',
                description=bug_text,
                color=0xFF0000
            )
            bugembed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)            
            if interaction.user.avatar:
                bugembed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
            else:
                bugembed.set_author(name=interaction.user.display_name)

            await bug_channel.send(embed=bugembed)

            confirmation_embed = nextcord.Embed(
                title='✅ Bug Reported',
                description=f'Thank you for reporting! It has been successfully submitted.',
                color=0x00FF00
            )
            await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)
            with open("rpg_bugvalue.json", "w") as file:
                json.dump({"bugcounter": bugcounter}, file, indent=4)
        else:
            await interaction.response.send_message(content='Bug channel not found. Please contact the server administrator.', ephemeral=True)

@bot.slash_command(
    name='bug',
    description='👾 Report a Bug.'
)
@log_command('bug')
async def bug(interaction: nextcord.Interaction):
 
    if update_active:
        update_embed = nextcord.Embed(
            title="🛠️ Update in Progress",
            description="A system update is currently in progress. Please try again later.",
            color=nextcord.Color.orange()
        )
        update_embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
        await interaction.send(embed=update_embed, ephemeral=True)
        return
     
    global bugcounter
    bug_modal = BugModal(bot, bug_id=bugcounter)
    await interaction.response.send_modal(bug_modal)

# 💫 /createevent
event_duration_seconds = 3600

def parse_duration(duration_str):
    match = re.match(r'(\d+)([smh])', duration_str)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
    return None

async def event_expired_notification(ctx, boost_type):
    global xp_multiplier, gold_multiplier
    await asyncio.sleep(event_duration_seconds)

    embed = nextcord.Embed(
        title="Weekend Booster Expired!",
        description=f"The weekend booster of type {boost_type.capitalize()} has expired!",
        color=nextcord.Color.red()
    )
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed)

def is_weekend():
    current_day = datetime.datetime.utcnow().weekday()
    return current_day in [1, 2, 3, 4, 5, 6]

async def check_and_start_weekend_boost():
    global xp_multiplier, gold_multiplier, event_duration_seconds

    while True:
        await asyncio.sleep(3)

        if is_weekend():
            boost_type = random.choice(['xp', 'gold'])

            if boost_type == 'xp':
                xp_multiplier = 6
                gold_multiplier = 8
            else:
                gold_multiplier = 8
                xp_multiplier = 6

            channel = bot.get_channel(EVENT_CHANNEL_ID)
            role = channel.guild.get_role(BOOSTERPING_ROLE_ID)

            embed = nextcord.Embed(
                title="😎 Weekend Booster Started!",
                description=f"{role.mention}, the weekend booster has been started!\n\n"
                            f"**▪︎ Multiplier Type:** **`{boost_type}`**\n **▪ Multiplier:** **`{xp_multiplier}x`**",
                color=nextcord.Color.gold()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await channel.send(embed=embed)
            await asyncio.sleep(event_duration_seconds)
            await event_expired_notification(None, boost_type)

@bot.slash_command(
    name='createevent',
    description='💫 Start an Event'
)
@log_command('createevent')
async def set_event(ctx, multipliertype: str, multiplier: float, duration: str):
    global xp_multiplier, gold_multiplier, event_duration_seconds

    user = ctx.user
    allowed_role = nextcord.utils.get(user.roles, name=DEVELOPER_RANK)

    parsed_duration = parse_duration(duration)

    if parsed_duration is not None:
        multipliertype = multipliertype.lower()

        if multipliertype == 'xp':
            xp_multiplier = multiplier
            gold_multiplier = 1
        elif multipliertype == 'gold':
            gold_multiplier = multiplier
            xp_multiplier = 1
        else:
            await ctx.send("Invalid multiplier type. Use 'xp' or 'gold'.")
            return

        event_duration_seconds = parsed_duration

        embed_event = nextcord.Embed(
            title="Event",
            description=f"**▪︎ Multiplier Type:** **`{multipliertype}`**\n **▪︎ Multiplier:** **`{multiplier}x`**\n **▪︎ Duration:** **`{parsed_duration} seconds`**",
            color=nextcord.Color.green()
        )
        embed_event.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed_event)

        xp_multiplier *= multiplier
        gold_multiplier *= multiplier

        bot.loop.create_task(event_expired_notification(ctx, multipliertype))
    else:
        error_embed = nextcord.Embed(
            title="❌ ERROR",
            description="**You don't have permission to use this command!**",
            color=nextcord.Color.red()
        )
        error_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=error_embed, ephemeral=True)

# 🗑️ /deleteuser
@bot.slash_command(
    name='deleteuser',
    description='🗑️ Delete user data'
)
@log_command('deleteuser')
async def deleteuser(ctx, member: nextcord.Member):
    user_name = member.name.lower()
    filename = f'{user_name}.json'

    if os.path.exists(filename):
        os.remove(filename)

        with open('rpg_achievementsearned.json', 'r') as achievements_file:
            achievements_data = json.load(achievements_file)

        if str(user_name) in achievements_data:
            del achievements_data[str(user_name)]
            
        with open('rpg_achievementsearned.json', 'w') as achievements_file:
            json.dump(achievements_data, achievements_file, indent=4)   

        embed = nextcord.Embed(
            title='🗑️ User Data Deleted',
            description=f"Successfully deleted data for {member.mention} ",
            color=nextcord.Color.green()
        )
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title='❌ File Not Found',
            description=f"No data found for {member.mention} ",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)

# 📜 /givempoints 
@bot.slash_command(
    name='givempoints',
    description='📜 Gives Mastery Points!'
)
@log_command('givempoints')
async def givempoints(ctx, value: int):
    player_name = ctx.user.name
    player_data = await load_player_data(player_name)

    if player_data is not None:
        player_data['mastery_points'] += value
        await save_player_data(player_name, player_data)

        embed = nextcord.Embed(
            title='🗑️ User Data Deleted',
            description=f"Successfully gave {value} Mastery Points to {ctx.user.mention} ",
            color=nextcord.Color.green()
        )
        await ctx.send(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(
            title='❌ File Not Found',
            description=f"No data found for {ctx.user.mention} ",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)

# ⭐ /givexp
@bot.slash_command(
    name='givexp',
    description='⭐ Give XP to and user'
)
@log_command('givexp')
async def givexp(ctx, member: nextcord.Member, value: int):
    user_name = member.name.lower()
    filename = f'{user_name}.json'
    user_data = cash_load_data(filename)

    if 'xp' not in user_data:
        user_data['xp'] = 0
    user_data['xp'] += value
    cash_save_data(filename, user_data)

    embed = nextcord.Embed(
        title='⭐ XP Given',
        description=f"Successfully gave {value} XP to {member.mention}",
        color=nextcord.Color.green()
    )
    await ctx.send(embed=embed, ephemeral=True)

# 😢 /resetxp
@bot.slash_command(
    name='resetxp',
    description='😢 Reset the xp of an user'
)
@log_command('resetxp')
async def resetxp(ctx, member: nextcord.Member):
    user_name = member.name.lower()
    filename = f'{user_name}.json'
    user_data = cash_load_data(filename)

    if 'xp' not in user_data:
        user_data['xp'] = 0
    user_data['xp'] = 0

    if 'level' not in user_data:
        user_data['level'] = 0
    user_data['level'] = 0

    cash_save_data(filename, user_data)

    embed = nextcord.Embed(
        title='😢 XP Reset',
        description=f"Successfully reset XP for {member.mention}",
        color=nextcord.Color.green()
    )
    await ctx.send(embed=embed, ephemeral=True)

# 🪫 /update
@bot.slash_command(
    name='update',
    description='🪫 Initiates an update process.'
)
@log_command('update')
async def update(ctx, updatemessage: str = None):
    try:
        allowed_roles = ['⚙️ Developer']
            
        if any(role.name in allowed_roles for role in ctx.user.roles):
            global update_active

            if update_active:
                update_embed = nextcord.Embed(
                    title="⚠️ Update in Progress",
                    description="An update is already in progress. Please wait until it is completed.",
                    color=nextcord.Color.orange()
                )
                await ctx.send(embed=update_embed, ephemeral=True)
                return

            channel = bot.get_channel(UPDATE_CHANNEL_ID)
            role = channel.guild.get_role(UPDATE_PING_ROLE_ID)

            if not channel:
                target_not_found_embed = nextcord.Embed(
                    title="❌ Target Channel Not Found",
                    description="Target channel not found. Please configure the target channel ID.",
                    color=nextcord.Color.red()
                )
                await ctx.send(embed=target_not_found_embed, ephemeral=True)
                return

            update_active = True
            await set_rich_presence(RPC_UPDATE_STATE)

            message_parts = []
            if updatemessage is not None:
                message_parts = [updatemessage[i:i + 2000] for i in range(0, len(updatemessage), 2000)]

            for part in message_parts:
                embed = nextcord.Embed(
                    title=f"🔄 Update",
                    description=part,
                    color=nextcord.Color.yellow()
                )
                embed.set_footer(text="Made by @prodbyeagle", icon_url=pic_link)
                await channel.send(role.mention, embed=embed)

            update_started_embed = nextcord.Embed(
                title="✅ Update Started",
                color=nextcord.Color.green()
            )
            await ctx.send(embed=update_started_embed, ephemeral=True)
        else:
            error_embed = nextcord.Embed(
                title="❌ Error",
                description="You do not have permission for this command.",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed, ephemeral=True)

    except Exception as e:
        error_message_embed = nextcord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(e)}",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_message_embed, ephemeral=True)

# 🔋 /endupdate
@bot.slash_command(
    name='endupdate',
    description='🔋 Ends an update process.'
)
@log_command('endupdate')
async def endupdate(ctx):
    if ctx.guild is None:
        embed = nextcord.Embed(
            title="⛔ Command Error",
            description="This command can only be used in Chill Lounge text channels.",
            color=0xFF5733
        )
        await ctx.send(embed=embed, ephemeral=True)
        return

    allowed_roles = ['⚙️ Developer']
    if any(role.name in allowed_roles for role in ctx.user.roles):
        global update_active
        if update_active:

            update_active = False
            success_embed = nextcord.Embed(
                title="⚙️ Update Completed",
                description="The update has been successfully completed.",
                color=nextcord.Color.green()
            )
            await set_rich_presence(RPC_DEFAULT_STATE)
            await ctx.send(embed=success_embed, ephemeral=True)
        else:
            no_update_embed = nextcord.Embed(
                title="⚙️ No Update Running",
                description="There is no update running that needs to be ended.",
                color=nextcord.Color.blue()
            )
            await ctx.send(embed=no_update_embed, ephemeral=True)
    else:
        error_embed = nextcord.Embed(
            title="❌ Error",
            description="You do not have permission for this command.",
            color=nextcord.Color.red()
        )
        await ctx.send(embed=error_embed, ephemeral=True)

# 🪙 /goldrain
@bot.slash_command(
    name='goldrain',
    description='🪙 LET IT RAIN!'
)
@log_command('goldrain')
async def goldrain(ctx, amount: int):
    all_player_names = await get_all_player_names()
    player_names = [player_name for player_name in all_player_names if not player_name.lower().startswith('rpg_')]
    
    num_players = len(player_names)
    print(f"{num_players}")

    if num_players == 0:
        await ctx.send("⚠️ No eligible players are registered.", ephemeral=True)
        return

    gold_per_player = amount // num_players

    for player_name in player_names:
        player_data = await load_player_data(player_name)

        if player_data and "gold" in player_data:
            player_data["gold"] += gold_per_player
            await save_player_data(player_name, player_data)

    formatted_gold_per_player = format_gold(gold_per_player)

    embed = nextcord.Embed(title="🪙 Gold Rainstorm", color=nextcord.Color.gold())
    embed.add_field(name="📦 Amount", value=f"{amount} gold", inline=False)
    embed.add_field(name="🧑🏻 Per Player", value=f"{formatted_gold_per_player} gold", inline=False)
    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
    await ctx.send(embed=embed, ephemeral=True)

# 🌧️ /itemrain
@bot.slash_command(
    name='itemrain',
    description='🌧️ Trigger an item rain with specified rarities and chances'
)
async def itemrain(ctx, basic: int, rare: int, epic: int, legendary: int, secret: int, exclusive: int):
    rarity_chances = {
        'basic': basic,
        'rare': rare,
        'epic': epic,
        'legendary': legendary,
        'secret': secret,
        'exclusive': exclusive
    }

    if sum(rarity_chances.values()) != 100:
        await ctx.send("❌ The total chance must be 100.")
        return

    all_items = load_itemrain()

    player_names = await get_all_player_names()
    num_players = len(player_names)
    
    if num_players == 0:
        await ctx.send("⚠️ No players are registered.", ephemeral=True)
        return

    items_to_give_by_player = {}
    for player_name in player_names:
        if "rpg" in player_name.lower():
            continue
        
        items_to_give = {}
        for rarity, chance in rarity_chances.items():
            if random.randint(1, 100) <= chance:
                selected_item_name, quantity = get_random_item_by_rarity(all_items, rarity)
                items_to_give[selected_item_name] = quantity

        if items_to_give:
            items_to_give_by_player[player_name] = items_to_give

    if items_to_give_by_player:
        await send_item_rain_embed(ctx, items_to_give_by_player)
        for player_name, items_to_give in items_to_give_by_player.items():
            await update_player_inventory(player_name, items_to_give)

async def send_item_rain_embed(ctx, items_to_give_by_player):
    embed = nextcord.Embed(title="Item Rain Results", color=0x00ff00)
    for player_name, items_to_give in items_to_give_by_player.items():
        embed.add_field(name=f"Player: {player_name}", value=format_items_for_embed(items_to_give), inline=False)

    await ctx.send(embed=embed)

def format_items_for_embed(items):
    formatted_items = ""
    for item_name, quantity in items.items():
        formatted_items += f"{item_name} x{quantity}\n"
    return formatted_items.strip()

def get_random_item_by_rarity(items, rarity):
    selected_item = random.choice(items.get(rarity, []))
    return selected_item["name"], 1

def load_itemrain():
    with open('rpg_items.json', 'r') as file:
        items_data = json.load(file)

    items_by_rarity = {}
    for item in items_data:
        rarity = item['rarity'].lower()
        if rarity not in items_by_rarity:
            items_by_rarity[rarity] = []
        items_by_rarity[rarity].append(item)

    return items_by_rarity

async def update_player_inventory(player_name, items):
    player_data = await load_player_data(player_name)

    if player_data and "inventory" in player_data:
        for item_name, quantity in items.items():
            if item_name in player_data["inventory"]:
                player_data["inventory"][item_name] += quantity
            else:
                player_data["inventory"][item_name] = 1

        await save_player_data(player_name, player_data)

async def send_items_embed(ctx, items_for_all_players):
    embed = nextcord.Embed(title="Item Rain Results", color=0x00ff00)

    for player_name, items_to_give in items_for_all_players.items():
        item_list = "\n".join([f"{item_name} x{quantity}" for item_name, quantity in items_to_give.items()])
        embed.add_field(name=f"Player: {player_name}", value=item_list, inline=False)

    await ctx.send(embed=embed)

# 💀 /cleartestacc
@bot.slash_command(
    name='cleartestacc',
    description='💀 Clear test files / Accounts for Developing'
)
@log_command('cleartestacc')
async def clear_test_accounts(ctx):
    deleted_accounts = []

    for file_name in os.listdir():
        if file_name.startswith("testplayer"):
            os.remove(file_name)
            deleted_accounts.append(file_name)

    await ctx.send(f"{len(deleted_accounts)} Test accounts cleared", ephemeral=True)

# 📂 /createtestacc
@bot.slash_command(
    name='createtestacc',
    description='📂 Create Test Files / Accounts for Developing'
)
@log_command('createtestacc')
async def create_test_accounts(ctx, amount: int):
    if ctx.user.id == OWNER_ID:
        created_accounts = []
        if amount < 11:
            for i in range(1, amount + 1):
                name = f"TestPlayer{i}"
                player_data = {
                    'name': name,
                    'game_started': True,    
                    'xp_notification': True,   
                    '1st_fish_gift': False,
                    'level': 1,
                    'mastery_points': 0,
                    'xp': 0,
                    'gold': 100,
                    'last_daily_claim': 0,
                    'last_weekly_claim': 0,
                    'last_monthly_claim': 0,
                    'last_fish_time': 0,
                    'last_quiz_attempt': 0,
                    'messages_sent': 0,
                    'clicks': 0,
                    'fights_won': 0,
                    'fights_lost': 0,
                    'completed_missions': 0,
                    'active_missions': {},
                    'active_rod': {},
                    'pets': {},
                    'inventory': {},
                    'masteries': {},
            }
                file_path = f"{name.lower()}.json"
                with open(file_path, 'w') as file:
                    json.dump(player_data, file, indent=4)
        
                created_accounts.append(name)
            
            accounts_message = f"Created {', '.join(created_accounts)}"
            await ctx.send(accounts_message, ephemeral=True)
        else:
            await ctx.send("Zu groß! Maximal 10", ephemeral=True)
    else:
        await ctx.send("nur @prodbyeagle kann das.", ephemeral=True)

# 🚮 /clearchannel
class ConfirmationView(View):
    def __init__(self):
        super().__init__()

    @nextcord.ui.button(label="🫡 Im 100% Confident", style=nextcord.ButtonStyle.red)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            content="**`♻️ Deletion Started!`**",
            ephemeral=True
        )
        channel = interaction.channel
        await channel.purge()
        await asyncio.sleep(5)
        self.stop()
        
        embed = nextcord.Embed(
            title="**`🚮 Channel Cleared!`**",
            description="**`All messages in this channel have been cleared.`**",
            color=nextcord.Color.blue()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        confirmation_message = await channel.send(embed=embed)
        await asyncio.sleep(3)
        await confirmation_message.delete()

    @nextcord.ui.button(label="😑 Nevermind.", style=nextcord.ButtonStyle.green)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("**`⛔ Deletion Stopped!`**", ephemeral=True)
        self.stop()

@bot.slash_command(
    name='clearchannel',
    description='🚮 Deletes all messages in this channel.'
)
@log_command('clearchannel')
async def clearchannel_command(ctx):
    try:
        allowed_roles = DEVELOPER_RANK

        if any(role.name in allowed_roles for role in ctx.user.roles):
            if isinstance(ctx.channel, nextcord.TextChannel):
                if ctx.channel.id not in blacklisted_channels:
                    view = ConfirmationView()
                    embed = nextcord.Embed(
                        title="**`⚠️ Channel Clearing Warning`**",
                        description="**`💯 Are you sure you want to delete ALL messages in this channel?`**",
                        color=0xFF5733
                    )
                    embed.add_field(name="", value="**`⚠️ If you want to add Blacklisted Channels DM @prodbyeagle`**")
                    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                    await ctx.send(embed=embed, view=view, ephemeral=True)
                else:
                    embed = nextcord.Embed(
                        title="**`⛔ BLACKLISTED`**",
                        description="**`This channel cannot be cleared.`**",
                        color=0xFF5733
                    )
                    embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                    await ctx.send(embed=embed, ephemeral=True)
            else:
                embed = nextcord.Embed(
                    title="**`🦅 Server Only`**",
                    description="**`This command can only be used in the Chill Lounge Server | Link in Bot Bio.`**",
                    color=0xFF5733
                )
                embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(
                title="**`👑 Server Devs Only`**",
                description="**`You do not have permission for this command.`**",
                color=nextcord.Color.red()
            )
            embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
            await ctx.send(embed=embed, ephemeral=True)

    except Exception as e:
        embed = nextcord.Embed(
            title="**`❌ Command Error`**",
            description=f"**`{str(e)} | Send me please to @prodbyeagle`**\n\nIf Error is 'User' object has no attribute 'roles' then is because you are in an Private Chat.",
            color=0xFF5733
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await ctx.send(embed=embed, ephemeral=True)

# -------------
# ON MESSAGE SYSTEM:
async def create_role(guild, role_name, color):
    try:
        role = await guild.create_role(name=role_name, color=color)
        return role
    except nextcord.Forbidden:
        return None

async def send_dm_to_admin(guild, admin_id, content):
    admin = await guild.fetch_member(admin_id)
    if admin:
        try:
            await admin.send(content)
        except nextcord.Forbidden:
            pass

def cash_load_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}

def cash_save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_message(message):
    global xp_multiplier, gold_multiplier
    if message.author == bot.user or message.author.bot or message.guild is None:
        return
    
    ctx = await bot.get_context(message)
    player_name = ctx.author.name
    player_data = await load_player_data(player_name)

    if player_data is None or not player_data:
        return

    user_name = message.author.name.lower()

    filename = f'{user_name}.json'
    user_data = player_data

    if 'xp' not in user_data:
        user_data['xp'] = 0

    xp_earned = 10 * xp_multiplier
    gold_earned = 20 * gold_multiplier

    user_data['xp'] += xp_earned
    user_data['gold'] += gold_earned
    user_data['messages_sent'] = user_data.get('messages_sent', 0) + 1

    level = 0
    required_xp = 100

    while user_data['xp'] >= required_xp:
        level += 1
        required_xp = int(required_xp + 50)

    if level > user_data.get('level', 0):
        level_up = True
        mastery_points_earned = level - user_data.get('level', 0)
        
        user_data['level'] = level
        user_data['mastery_points'] = user_data.get('mastery_points', 0) + mastery_points_earned
        user_data['xp'] = 0
    else:
        level_up = False
    
    cash_save_data(filename, user_data)

    if level_up and user_data.get('xp_notification', True):
        message_text = f"You've reached Level **{level}** Congrats"

        if level > 150:
            message_text += " and earned 1 Mastery Point (50% chance)!"

        embed = nextcord.Embed(
            title=f"🆙 Congratulations {message.author.name}!",
            description=message_text,
            color=nextcord.Color.green()
        )
        embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
        await message.author.send(embed=embed)

    if user_name not in achievements_earned:
        achievements_earned[user_name] = []

    achievements_file = "rpg_achievements.json"

    with open(achievements_file, 'r', encoding='utf-8') as achievements_json:
        achievements = json.load(achievements_json)

    for achievement_name, achievement_data in achievements.items():
        if achievement_name not in achievements_earned[user_name]:
            criteria = achievement_data.get("criteria", {})
            clicks = user_data.get('clicks', 0)
            level = user_data.get('level', 0)
            fights_won = user_data.get('fights_won', 0)
            fights_lost = user_data.get('fights_lost', 0)
            gold = user_data.get('gold', 0)
    
            if "clicks" in criteria and criteria["clicks"] <= clicks:
                achievements_earned[user_name].append(achievement_name)
                save_earnedachievements_data()
    
                achievement_embed = nextcord.Embed(
                    title=f"🎊 ACHIEVEMENT UNLOCKED",
                    description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                    color=nextcord.Color.gold()
                )
                achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await message.author.send(embed=achievement_embed)
    
                role_name = achievement_data['name']
                role_color = nextcord.Color(achievement_data.get('color', 0))
    
                role = nextcord.utils.get(message.guild.roles, name=role_name)
    
                if not role:
                    role = await create_role(message.guild, role_name, role_color)
                    if role:
                        await send_dm_to_admin(message.guild, message.guild.owner_id,
                        f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")
    
                if role:
                    member = message.author.guild.get_member(message.author.id)
                    await member.add_roles(role)

            if "level" in criteria and criteria["level"] <= level:
                achievements_earned[user_name].append(achievement_name)
                save_earnedachievements_data()
          
                achievement_embed = nextcord.Embed(
                    title=f"🎊 ACHIEVEMENT UNLOCKED",
                    description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                    color=nextcord.Color.gold()
                )
                achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await message.author.send(embed=achievement_embed)
    
                role_name = achievement_data['name']
                role_color = nextcord.Color(achievement_data.get('color', 0))
    
                role = nextcord.utils.get(message.guild.roles, name=role_name)
    
                if not role:
                    role = await create_role(message.guild, role_name, role_color)
                    if role:
                        await send_dm_to_admin(message.guild, message.guild.owner_id,
                        f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")
    
                if role:
                    member = message.author.guild.get_member(message.author.id)
                    await member.add_roles(role)

            if "fights_won" in criteria and criteria["fights_won"] <= fights_won:
                achievements_earned[user_name].append(achievement_name)
                save_earnedachievements_data()
          
                achievement_embed = nextcord.Embed(
                    title=f"🎊 ACHIEVEMENT UNLOCKED",
                    description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                    color=nextcord.Color.gold()
                )
                achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await message.author.send(embed=achievement_embed)
    
                role_name = achievement_data['name']
                role_color = nextcord.Color(achievement_data.get('color', 0))
    
                role = nextcord.utils.get(message.guild.roles, name=role_name)
    
                if not role:
                    role = await create_role(message.guild, role_name, role_color)
                    if role:
                        await send_dm_to_admin(message.guild, message.guild.owner_id,
                        f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")
    
                if role:
                    member = message.author.guild.get_member(message.author.id)
                    await member.add_roles(role)

            if "fights_lost" in criteria and criteria["fights_lost"] <= fights_lost:
                achievements_earned[user_name].append(achievement_name)
                save_earnedachievements_data()
          
                achievement_embed = nextcord.Embed(
                    title=f"🎊 ACHIEVEMENT UNLOCKED",
                    description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                    color=nextcord.Color.gold()
                )
                achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await message.author.send(embed=achievement_embed)
    
                role_name = achievement_data['name']
                role_color = nextcord.Color(achievement_data.get('color', 0))
    
                role = nextcord.utils.get(message.guild.roles, name=role_name)
    
                if not role:
                    role = await create_role(message.guild, role_name, role_color)
                    if role:
                        await send_dm_to_admin(message.guild, message.guild.owner_id,
                        f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")
    
                if role:
                    member = message.author.guild.get_member(message.author.id)
                    await member.add_roles(role)

            if "gold" in criteria and criteria["gold"] <= gold:
                achievements_earned[user_name].append(achievement_name)
                save_earnedachievements_data()
          
                achievement_embed = nextcord.Embed(
                    title=f"🎊 ACHIEVEMENT UNLOCKED",
                    description=f"<@{message.author.id}>, you've achieved the `{achievement_data['name']}` ACHIEVEMENT!",
                    color=nextcord.Color.gold()
                )
                achievement_embed.set_footer(text="🦅 | @prodbyeagle", icon_url=pic_link)
                await message.author.send(embed=achievement_embed)
    
                role_name = achievement_data['name']
                role_color = nextcord.Color(achievement_data.get('color', 0))
    
                role = nextcord.utils.get(message.guild.roles, name=role_name)
    
                if not role:
                    role = await create_role(message.guild, role_name, role_color)
                    if role:
                        await send_dm_to_admin(message.guild, message.guild.owner_id,
                        f"A new role '{role_name}' has been created for the achievement '{achievement_name}'.")
    
                if role:
                    member = message.author.guild.get_member(message.author.id)
                    await member.add_roles(role)

bot.run(TOKEN)