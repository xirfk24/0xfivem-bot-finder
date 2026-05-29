import interactions
from core.repo.guild import guild as guild_repo
from core.repo.admin import admin as admin_repo
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext


class AdminExtension(interactions.Extension):
    """Discord bot extension for admin commands."""

    def __init__(self, bot: interactions.Client) -> None:
        """Initialize the Admin extension.

        Args:
            bot: The Discord bot client instance
        """
        self.bot = bot

    async def is_admin(self, user_id: int) -> bool:
        """Check if a user is a bot admin.

        Args:
            user_id: Discord user ID

        Returns:
            True if user is admin, False otherwise
        """
        return await admin_repo.is_admin(user_id)

    @interactions.slash_command(
        name="set_announce_channel",
        description="Set the channel where bot online announcements will be sent"
    )
    @interactions.slash_option(
        "channel",
        "The channel to send announcements to",
        required=True,
        opt_type=interactions.OptionType.CHANNEL
    )
    async def set_announce_channel(
        self,
        ctx: interactions.SlashContext,
        channel: interactions.GuildText
    ):
        """Set the announcement channel for this server.

        Args:
            ctx: The command context
            channel: The channel to set as announcement channel
        """
        # Defer response to prevent timeout
        await ctx.defer(ephemeral=True)

        # Check if user has administrator permission
        if not ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            await ctx.send("❌ You need Administrator permission to use this command!", ephemeral=True)
            return

        try:
            # Get or create guild in database
            guild_data = await guild_repo.get_by_guild_id(ctx.guild_id)

            if not guild_data:
                # Create new guild entry
                await guild_repo.create({
                    'guild_id': ctx.guild_id,
                    'guild_name': ctx.guild.name,
                    'announce_channel_id': channel.id
                })
            else:
                # Update existing guild
                await guild_repo.set_announce_channel(ctx.guild_id, channel.id)

            await ctx.send(
                f"✅ Announcement channel set to {channel.mention}\n"
                f"The bot will send a message here when it comes online.",
                ephemeral=True
            )
        except Exception as e:
            await ctx.send(f"❌ Failed to set announcement channel: {str(e)}", ephemeral=True)

    @interactions.slash_command(
        name="remove_announce_channel",
        description="Remove the announcement channel (disable announcements)"
    )
    async def remove_announce_channel(self, ctx: interactions.SlashContext):
        """Remove the announcement channel for this server.

        Args:
            ctx: The command context
        """
        # Defer response to prevent timeout
        await ctx.defer(ephemeral=True)

        # Check if user has administrator permission
        if not ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            await ctx.send("❌ You need Administrator permission to use this command!", ephemeral=True)
            return

        try:
            guild_data = await guild_repo.get_by_guild_id(ctx.guild_id)

            if not guild_data or not guild_data.announce_channel_id:
                await ctx.send("❌ No announcement channel is currently set.", ephemeral=True)
                return

            await guild_repo.set_announce_channel(ctx.guild_id, None)
            await ctx.send("✅ Announcement channel removed. The bot will no longer announce when it comes online.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to remove announcement channel: {str(e)}", ephemeral=True)

    @interactions.slash_command(
        name="test_announce",
        description="Test the announcement message in the configured channel"
    )
    async def test_announce(self, ctx: interactions.SlashContext):
        """Test the announcement message.

        Args:
            ctx: The command context
        """
        # Defer response to prevent timeout
        await ctx.defer(ephemeral=True)

        # Check if user has administrator permission
        if not ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            await ctx.send("❌ You need Administrator permission to use this command!", ephemeral=True)
            return

        try:
            guild_data = await guild_repo.get_by_guild_id(ctx.guild_id)

            if not guild_data or not guild_data.announce_channel_id:
                await ctx.send("❌ No announcement channel is set. Use `/set_announce_channel` first.", ephemeral=True)
                return

            channel = await self.bot.fetch_channel(guild_data.announce_channel_id)
            await channel.send(f"✅ **{self.bot.user.display_name}** is now online and ready! (Test)")
            await ctx.send(f"✅ Test announcement sent to <#{guild_data.announce_channel_id}>", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ Failed to send test announcement: {str(e)}", ephemeral=True)

    @prefixed_command(name="umurgm")
    async def umurgm(self, ctx: PrefixedContext):
        """Respond with UDAH TUA BABI."""
        await ctx.reply("UDAH TUA BABI")

    @prefixed_command(name="bio")
    async def bio(self, ctx: PrefixedContext, *, name: str = None):
        """Show bio information."""
        if name and name.lower() == "sully":
            await ctx.reply("ini sully stark myers lahir di idp anak dari pasangan ferdy stark myers npd dan lala stark myers, sully pernah di kasi mobil oleh kyo myers , pernah mencoba mendekati natalia , sully ini merupakan salah satu kategori yang full emosi ketika panas2an bersama BS bwmc dan BM")
        else:
            await ctx.reply("❌ Bio tidak ditemukan. Gunakan: `!bio sully`")


def setup(bot: interactions.Client):
    """Setup function to load the extension."""
    AdminExtension(bot)
