from core.settings import settings
from core.repo.guild import guild as guild_repo
from interactions import (
    Client,
    listen,
    Intents,
    ActivityType,
    Activity,
    Status
)
from interactions.ext import prefixed_commands
from core.help import PrefixedHelpCommand


bot = Client(
    intents = Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.GUILD_MESSAGES | Intents.GUILDS | Intents.GUILD_INVITES | Intents.GUILD_MEMBERS | Intents.ALL,
    sync_interactions=True
)
bot.send_command_tracebacks = False
prefixed_commands.setup(bot, default_prefix='!')
help_cmd = PrefixedHelpCommand(bot, show_usage=True, show_prefix=True)
help_cmd.register()

@listen()
async def on_ready():

    print('\n\n')
    print(f'{bot.user.display_name} is Online!')


    await bot.change_presence(
        status=Status.ONLINE,
        activity=Activity(
            name="0x-fivem-finder | !tutor",
            type=ActivityType.PLAYING
        )
    )

    # Auto-announce bot online to all configured guilds
    try:
        guilds_with_announce = await guild_repo.get_all_with_announce_channel()

        if guilds_with_announce:
            print(f"Sending announcements to {len(guilds_with_announce)} guild(s)...")

            for guild in guilds_with_announce:
                try:
                    channel = await bot.fetch_channel(guild.announce_channel_id)
                    await channel.send(f"✅ **{bot.user.display_name}** @here BOT ONLINE! MASI PAKE LAPTOP GW BELIIN VPS NGAPA")
                    print(f"✓ Announced to {guild.guild_name}")
                except Exception as e:
                    print(f"✗ Failed to announce to {guild.guild_name}: {e}")
        else:
            print("No guilds configured for announcements")
    except Exception as e:
        print(f"Failed to process announcements: {e}")

if __name__ == '__main__':

    bot.load_extensions("extensions")

    try:
        bot.start(settings.DISCORD_TOKEN)
    except Exception as e:
        print(str(e))