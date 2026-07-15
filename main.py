import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
from typing import Optional
from aiohttp import web
import asyncio

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))
SESSIONS_ROLE_ID = int(os.getenv('SESSIONS_ROLE_ID', 0))
STAFF_TEAM_ROLE_ID = int(os.getenv('STAFF_TEAM_ROLE_ID', 0))
INTERNAL_AFFAIRS_ROLE_ID = int(os.getenv('INTERNAL_AFFAIRS_ROLE_ID', 0))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents, activity=discord.Activity(
    type=discord.ActivityType.watching,
    name="Moderating SFRP, Assisting Members, Moderating Staff"
))

# Infraction data storage
INFRACTIONS_FILE = 'infractions.json'

def load_infractions():
    try:
        with open(INFRACTIONS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_infractions(infractions):
    with open(INFRACTIONS_FILE, 'w') as f:
        json.dump(infractions, f, indent=4)

def has_ia_permission(interaction: discord.Interaction) -> bool:
    """Check if user has Internal Affairs role or is administrator"""
    if interaction.user.guild_permissions.administrator:
        return True
    if INTERNAL_AFFAIRS_ROLE_ID:
        role = interaction.guild.get_role(INTERNAL_AFFAIRS_ROLE_ID)
        if role and role in interaction.user.roles:
            return True
    return False

def has_admin_permission(interaction: discord.Interaction) -> bool:
    """Check if user has administrator permissions"""
    return interaction.user.guild_permissions.administrator

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Guild ID: {GUILD_ID}')
    
    # Sync commands with guild
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f'Synced {len(synced)} command(s) to guild')
    except Exception as e:
        print(f'Error syncing commands to guild: {e}')
        # Try global sync as fallback
        try:
            synced = await bot.tree.sync()
            print(f'Synced {len(synced)} command(s) globally')
        except Exception as e2:
            print(f'Error syncing commands globally: {e2}')

# Session Commands
@bot.tree.command(name='session', description='Session management commands')
@app_commands.describe(action='The session action to perform')
@app_commands.choices(action=[
    app_commands.Choice(name='start', value='start'),
    app_commands.Choice(name='end', value='end'),
    app_commands.Choice(name='boost', value='boost'),
    app_commands.Choice(name='vote', value='vote'),
])
async def session(interaction: discord.Interaction, action: str):
    """Session management commands (IA+ only)"""
    if not has_ia_permission(interaction):
        await interaction.response.send_message('You do not have permission to use this command. Only Internal Affairs and Administrators can use session commands.', ephemeral=True)
        return

    guild = interaction.guild
    sessions_role = guild.get_role(SESSIONS_ROLE_ID) if SESSIONS_ROLE_ID else None
    staff_role = guild.get_role(STAFF_TEAM_ROLE_ID) if STAFF_TEAM_ROLE_ID else None

    if action == 'start':
        embed = discord.Embed(
            title='🚀 Session Started',
            description='A Session has begun by the Springfield Roleplay Community HR\'s. Join up!',
            color=discord.Color.green()
        )
        embed.add_field(name='Server Code', value='sfrpj', inline=False)
        embed.set_footer(text='Springfield Roleplay Community')
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        mentions = []
        if sessions_role:
            mentions.append(sessions_role.mention)
        if staff_role:
            mentions.append(staff_role.mention)
        
        mention_text = ' '.join(mentions) if mentions else ''
        await interaction.response.send_message(f'{mention_text}', embed=embed)

    elif action == 'end':
        embed = discord.Embed(
            title='🔴 Session Ended',
            description='The server is now shutdown. Do not join In-Game or you will be moderated.',
            color=discord.Color.red()
        )
        embed.set_footer(text='Springfield Roleplay Community')
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)

    elif action == 'boost':
        embed = discord.Embed(
            title='⚡ Session Boost',
            description='A Session Boost has begun. We are low players. Join up!',
            color=discord.Color.gold()
        )
        embed.set_footer(text='Springfield Roleplay Community')
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        mentions = []
        if sessions_role:
            mentions.append(sessions_role.mention)
        if staff_role:
            mentions.append(staff_role.mention)
        
        mention_text = ' '.join(mentions) if mentions else ''
        await interaction.response.send_message(f'{mention_text}', embed=embed)

    elif action == 'vote':
        embed = discord.Embed(
            title='🗳️ Session Vote',
            description='A Session is being initiated. Vote if you will join In-Game.',
            color=discord.Color.blue()
        )
        embed.add_field(name='Instructions', value='React with ✅ if you will join, ❌ if you cannot.', inline=False)
        embed.set_footer(text='Springfield Roleplay Community')
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        mentions = []
        if sessions_role:
            mentions.append(sessions_role.mention)
        if staff_role:
            mentions.append(staff_role.mention)
        
        mention_text = ' '.join(mentions) if mentions else ''
        message = await interaction.response.send_message(f'{mention_text}', embed=embed)
        
        # Add reactions
        message = await interaction.original_response()
        await message.add_reaction('✅')
        await message.add_reaction('❌')

# Admin Commands
@bot.tree.command(name='promotion_issue', description='Issue a promotion')
@app_commands.describe(staff_member='The staff member being promoted', issuer='The issuer of the promotion', reason='Reason for promotion', notes='Additional notes (optional)')
async def promotion_issue(interaction: discord.Interaction, staff_member: discord.Member, issuer: str, reason: str, notes: Optional[str] = None):
    """Issue a promotion (Admin only)"""
    if not has_admin_permission(interaction):
        await interaction.response.send_message('You do not have permission to use this command. Only Administrators can use this command.', ephemeral=True)
        return

    embed = discord.Embed(
        title='🎉 Promotion Issued',
        color=discord.Color.purple()
    )
    embed.add_field(name='Staff Member', value=staff_member.mention, inline=False)
    embed.add_field(name='Issuer', value=issuer, inline=False)
    embed.add_field(name='Reason', value=reason, inline=False)
    if notes:
        embed.add_field(name='Notes', value=notes, inline=False)
    embed.set_footer(text='Springfield Roleplay Community')
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='infraction_issue', description='Issue an infraction')
@app_commands.describe(staff_member='The staff member being infracted', issuer='The issuer of the infraction', infraction_type='Type of infraction', reason='Reason for infraction', notes='Additional notes (optional)')
@app_commands.choices(infraction_type=[
    app_commands.Choice(name='Verbal Warning', value='verbal_warning'),
    app_commands.Choice(name='Warning', value='warning'),
    app_commands.Choice(name='Strike', value='strike'),
    app_commands.Choice(name='Termination', value='termination'),
    app_commands.Choice(name='Blacklist', value='blacklist'),
])
async def infraction_issue(interaction: discord.Interaction, staff_member: discord.Member, issuer: str, infraction_type: str, reason: str, notes: Optional[str] = None):
    """Issue an infraction (Admin only)"""
    if not has_admin_permission(interaction):
        await interaction.response.send_message('You do not have permission to use this command. Only Administrators can use this command.', ephemeral=True)
        return

    # Load infractions
    infractions = load_infractions()
    user_id = str(staff_member.id)
    
    if user_id not in infractions:
        infractions[user_id] = {'warnings': 0, 'strikes': 0}
    
    # Handle warning progression
    infraction_display = infraction_type.replace('_', ' ').title()
    
    if infraction_type == 'warning':
        infractions[user_id]['warnings'] += 1
        warning_num = infractions[user_id]['warnings']
        infraction_display = f'Warning {warning_num}'
        
        # Assign warning role if it exists (you'll need to create these roles in your server)
        # Warning 1, Warning 2, Warning 3 roles
        warning_role_name = f'Warning {warning_num}'
        warning_role = discord.utils.get(interaction.guild.roles, name=warning_role_name)
        if warning_role:
            await staff_member.add_roles(warning_role)
            
    elif infraction_type == 'strike':
        infractions[user_id]['strikes'] += 1
        strike_num = infractions[user_id]['strikes']
        infraction_display = f'Strike {strike_num}'
        
        # Assign strike role if it exists
        strike_role_name = f'Strike {strike_num}'
        strike_role = discord.utils.get(interaction.guild.roles, name=strike_role_name)
        if strike_role:
            await staff_member.add_roles(strike_role)
    
    # Save infractions
    save_infractions(infractions)

    # Create embed
    embed = discord.Embed(
        title='⚠️ Infraction Issued',
        color=discord.Color.orange()
    )
    embed.add_field(name='Staff Member', value=staff_member.mention, inline=False)
    embed.add_field(name='Issuer', value=issuer, inline=False)
    embed.add_field(name='Infraction Type', value=infraction_display, inline=False)
    embed.add_field(name='Reason', value=reason, inline=False)
    if notes:
        embed.add_field(name='Notes', value=notes, inline=False)
    embed.set_footer(text='Springfield Roleplay Community')
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    await interaction.response.send_message(embed=embed)
    
    # Create thread for appeal
    message = await interaction.original_response()
    thread = await message.create_thread(
        name=f'Appeal - {staff_member.display_name}',
        auto_archive_duration=1440
    )
    await thread.send(f'{staff_member.mention} If you wish to appeal this infraction, please provide your reasoning here.')

@bot.tree.command(name='say', description='Make the bot say a message')
@app_commands.describe(message='The message for the bot to say')
async def say(interaction: discord.Interaction, message: str):
    """Make the bot say a message (Admin only)"""
    if not has_admin_permission(interaction):
        await interaction.response.send_message('You do not have permission to use this command. Only Administrators can use this command.', ephemeral=True)
        return

    await interaction.response.send_message(message)

@bot.tree.command(name='infractions_check', description='Check a user\'s infraction history')
@app_commands.describe(user='The user to check')
async def infractions_check(interaction: discord.Interaction, user: discord.Member):
    """Check a user's infraction history"""
    infractions = load_infractions()
    user_id = str(user.id)
    
    if user_id not in infractions or (infractions[user_id]['warnings'] == 0 and infractions[user_id]['strikes'] == 0):
        await interaction.response.send_message(f'{user.mention} has no infractions on record.', ephemeral=True)
        return
    
    data = infractions[user_id]
    embed = discord.Embed(
        title=f'Infraction Record - {user.display_name}',
        color=discord.Color.blue()
    )
    embed.add_field(name='Warnings', value=str(data['warnings']), inline=True)
    embed.add_field(name='Strikes', value=str(data['strikes']), inline=True)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    embed.set_footer(text='Springfield Roleplay Community')
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='infractions_clear', description='Clear a user\'s infraction record')
@app_commands.describe(user='The user to clear infractions for')
async def infractions_clear(interaction: discord.Interaction, user: discord.Member):
    """Clear a user's infraction record (Admin only)"""
    if not has_admin_permission(interaction):
        await interaction.response.send_message('You do not have permission to use this command. Only Administrators can use this command.', ephemeral=True)
        return
    
    infractions = load_infractions()
    user_id = str(user.id)
    
    if user_id in infractions:
        del infractions[user_id]
        save_infractions(infractions)
        
        # Remove warning roles
        for i in range(1, 4):
            warning_role = discord.utils.get(interaction.guild.roles, name=f'Warning {i}')
            if warning_role and warning_role in user.roles:
                await user.remove_roles(warning_role)
        
        # Remove strike roles
        for i in range(1, 4):
            strike_role = discord.utils.get(interaction.guild.roles, name=f'Strike {i}')
            if strike_role and strike_role in user.roles:
                await user.remove_roles(strike_role)
        
        await interaction.response.send_message(f'Cleared infraction record for {user.mention}.', ephemeral=True)
    else:
        await interaction.response.send_message(f'{user.mention} has no infractions to clear.', ephemeral=True)

# HTTP Server for health checks
async def health_check(request):
    return web.Response(text="Bot is running", status=200)

async def start_http_server():
    port = int(os.getenv('PORT', 10000))
    app = web.Application()
    app.add_routes([web.get('/', health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f'HTTP server started on port {port}')
    return runner

# Run the bot
async def main():
    if not TOKEN:
        print('Error: DISCORD_TOKEN not found in environment variables.')
        print('Please create a .env file with your bot token.')
        return
    
    # Start HTTP server for health checks
    runner = await start_http_server()
    
    # Start Discord bot
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
