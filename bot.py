import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GITHUB_PAT = os.getenv('GITHUB_PAT')
GITHUB_REPO = os.getenv('GITHUB_REPO')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def trigger_github_action(event_type: str, user: str):
    """Sends a repository_dispatch event to the GitHub repository."""
    print(f"Attempting to trigger '{event_type}' for user '{user}'...")
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_PAT}"
    }
    
    data = {
        "event_type": event_type,
        "client_payload": { "user": user }
    }
    
    # API call
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 204:
        print("Successfully triggered GitHub Action.")
        return True
    else:
        print(f"Failed to trigger GitHub Action. Status: {response.status_code}, Response: {response.text}")
        return False

@client.event
async def on_ready():
    """Event runs when the bot connects to Discord."""
    await tree.sync() 
    print(f'Logged in as {client.user}. Commands are synced and ready!')

@tree.command(name="start-server", description="Starts the game server by triggering the GitHub workflow.")
async def start_server_command(interaction: discord.Interaction):
    """Slash command to start the server."""
    await interaction.response.defer()
    
    success = trigger_github_action("start_server_request", interaction.user.name)
    
    if success:
        await interaction.followup.send("✅ **Start request sent!** Please wait a moment. A new message with the IP address will appear here shortly...")
    else:
        await interaction.followup.send("❌ **Error!** Could not trigger the server start. Please contact an admin.")

@tree.command(name="stop-server", description="Stops the game server by triggering the GitHub workflow.")
async def stop_server_command(interaction: discord.Interaction):
    """Slash command to stop the server."""
    await interaction.response.defer()

    success = trigger_github_action("stop_server_request", interaction.user.name)
    
    if success:
        await interaction.followup.send("✅ **Stop request sent!** The server will now save its state and shut down.")
    else:
        await interaction.followup.send("❌ **Error!** Could not trigger the server stop. Please contact an admin.")

if not DISCORD_BOT_TOKEN:
    print("Error: DISCORD_BOT_TOKEN not found. Make sure it's set in your .env file.")
else:
    client.run(DISCORD_BOT_TOKEN)