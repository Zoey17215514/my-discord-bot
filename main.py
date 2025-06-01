import discord
from discord.ext import commands
import re
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]

# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Create the bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Mapping student ID 4th character to faculty role
faculty_roles = {
    "B": "FAFB",
    "K": "FCCI",
    "L": "FOAS",
    "J": "FSSH",
    "V": "FOBE",
    "F": "CPUS",
    "M": "FOCS",
    "G": "FOET"
}

# Set of role names for quick checking
faculty_role_names = set(faculty_roles.values())

# Regex pattern for validating student ID format
student_id_pattern = re.compile(r"^\d{2}[A-Z]{3}\d{2}\d{3}$")


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')


@bot.event
async def on_member_join(member):
    try:
        await member.send(
            "🎓 Welcome! Please enter your student ID (e.g., 23WMD09867) to get verified:"
        )
    except discord.Forbidden:
        print(f"⚠️ Couldn't send DM to {member.name} (forbidden)")


@bot.event
async def on_message(message):
    if message.guild is None and not message.author.bot:
        student_id = message.content.strip().upper()
        user = message.author

        # Validate student ID format
        if not student_id_pattern.match(student_id):
            await user.send(
                "❌ Invalid student ID format. Please use the format like `23WMD09867`."
            )
            return

        # Extract faculty character and get role
        faculty_code = student_id[3]
        role_name = faculty_roles.get(faculty_code)

        if not role_name:
            await user.send(
                "❌ Student ID does not match any known faculty. Please check and try again."
            )
            return

        # Search for the user in all guilds the bot is in
        for guild in bot.guilds:
            member = guild.get_member(user.id)
            if member:
                # Check if member already has any faculty role
                existing_roles = [
                    role for role in member.roles
                    if role.name in faculty_role_names
                ]
                if existing_roles:
                    await user.send(
                        f"❌ You already have a faculty role: **{existing_roles[0].name}**.\nYou cannot change it. Contact an admin if this is incorrect."
                    )
                    break

                # Assign role if it exists
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    await member.add_roles(role)
                    await user.send(
                        f"✅ You've been verified and given the role: **{role_name}**"
                    )
                else:
                    await user.send(
                        f"⚠️ Role '{role_name}' not found in the server. Please contact an admin."
                    )
                break

    await bot.process_commands(message)


# Run the bot
bot.run(TOKEN)
