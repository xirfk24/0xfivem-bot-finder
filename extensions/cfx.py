import interactions
from typing import Optional, Union, List, Dict, Any
from core.repo import cfx
from lib.cfx_services import CFXService
from interactions.ext.paginators import Paginator
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext


class CfxExtension(interactions.Extension):
    """Discord bot extension for managing CFX/FiveM servers."""

    def __init__(self, bot: interactions.Client) -> None:
        """Initialize the CFX extension.
        
        Args:
            bot: The Discord bot client instance
        """
        self.bot = bot

    def get_ping_indicator(self, ping: int) -> str:
        """Get emoji indicator based on ping value.

        Args:
            ping: Player's ping in milliseconds

        Returns:
            Emoji indicator string
        """
        if ping < 50:
            return "🟢"  # Green - Excellent
        elif ping < 100:
            return "🟡"  # Yellow - Good
        elif ping < 150:
            return "🟠"  # Orange - Fair
        else:
            return "🔴"  # Red - Poor

    def format_player_list(self, players_chunk: List[Dict[str, Any]]) -> str:
        """Format a chunk of players into a readable string.

        Args:
            players_chunk: List of player dictionaries containing id, name, and ping

        Returns:
            Formatted string with player information
        """
        formatted_lines = []

        # Add header
        formatted_lines.append("```")
        formatted_lines.append("┌─────┬──────────────────────────────┬──────┐")
        formatted_lines.append("│  ID │          Player Name         │ Ping │")
        formatted_lines.append("├─────┼──────────────────────────────┼──────┤")
        formatted_lines.append("```")

        for player in players_chunk:
            player_id = player.get('id', 'Unknown')
            name = player.get('name', 'Unknown')
            ping = player.get('ping', 0)

            # Get ping indicator
            ping_emoji = self.get_ping_indicator(ping)

            # Format with better structure
            line = f"{ping_emoji} `#{player_id:>3}` ┃ **{name[:28]}** ┃ `{ping}ms`"
            formatted_lines.append(line)

        # Add footer separator
        formatted_lines.append("```")
        formatted_lines.append("└─────┴──────────────────────────────┴──────┘")
        formatted_lines.append("```")

        return "\n".join(formatted_lines)

    def chunk_array(self, data: List[Any], chunk_size: int = 20) -> List[List[Any]]:
        """Split an array into smaller chunks.
        
        Args:
            data: The array to split
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of chunked arrays
        """
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunks.append(data[i:i + chunk_size])
        return chunks

    def create_embeds_from_players(self, server_name: str, players: List[Dict[str, Any]],
                                 chunk_size: int = 30) -> List[interactions.Embed]:
        """Create paginated embeds from player data.

        Args:
            server_name: Name of the server
            players: List of player dictionaries
            chunk_size: Number of players per embed page

        Returns:
            List of Discord embeds
        """
        # Sort players by ID in descending order
        players_sorted = sorted(players, key=lambda x: x.get('id', 0), reverse=True)
        chunks = self.chunk_array(players_sorted, chunk_size)
        embeds = []

        # Calculate statistics
        total_players = len(players)
        pings = [p.get('ping', 0) for p in players]
        avg_ping = sum(pings) // len(pings) if pings else 0
        min_ping = min(pings) if pings else 0
        max_ping = max(pings) if pings else 0

        # Count ping categories
        excellent = sum(1 for p in pings if p < 50)
        good = sum(1 for p in pings if 50 <= p < 100)
        fair = sum(1 for p in pings if 100 <= p < 150)
        poor = sum(1 for p in pings if p >= 150)

        # Determine embed color based on average ping
        if avg_ping < 50:
            embed_color = 0x00FF00  # Green
        elif avg_ping < 100:
            embed_color = 0xFFFF00  # Yellow
        elif avg_ping < 150:
            embed_color = 0xFFA500  # Orange
        else:
            embed_color = 0xFF0000  # Red

        for page_num, chunk in enumerate(chunks, 1):
            content = self.format_player_list(chunk)

            embed = interactions.Embed(
                title=f"🎮 {server_name}",
                description=content,
                color=embed_color
            )

            # Add statistics field on first page
            if page_num == 1:
                stats = (
                    f"👥 **Total Players:** `{total_players}`\n"
                    f"📊 **Average Ping:** `{avg_ping}ms`\n"
                    f"⚡ **Best Ping:** `{min_ping}ms` | **Worst:** `{max_ping}ms`\n\n"
                    f"🟢 Excellent (<50ms): `{excellent}` | "
                    f"🟡 Good (50-99ms): `{good}`\n"
                    f"🟠 Fair (100-149ms): `{fair}` | "
                    f"🔴 Poor (≥150ms): `{poor}`"
                )
                embed.add_field(name="📈 Server Statistics", value=stats, inline=False)

            embed.set_footer(text=f"Page {page_num}/{len(chunks)} • Total Players: {total_players}")
            embeds.append(embed)

        return embeds

    @interactions.slash_command(
        name="add_server",
        description="Add a CFX server to the bot"
    )
    @interactions.slash_option(
        "address",
        "Server address (IP:Port)",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    @interactions.slash_option(
        "initial",
        "City/Server initial identifier", 
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def add_server(self, ctx: interactions.SlashContext, address: str, initial: str) -> None:
        """Add a new CFX server to the bot's database.
        
        Args:
            ctx: Slash command context
            address: Server address
            initial: Server initial/identifier
        """
        embed = interactions.Embed(
            description="🔍 Checking server...",
            color=interactions.Color.random()
        )
        await ctx.send(embed=embed)

        # Check if server already exists
        existing_service = await cfx.get_address(address)
        if existing_service:
            embed.description = "❌ Server already exists!"
            embed.color = interactions.Color.random()
            embed.add_field("Server Name", existing_service.server_name)
            return await ctx.edit(embed=embed)

        # Try to connect to the server
        cfx_service = CFXService(address)
        try:
            server_data = await cfx_service.getInfo()
        except Exception as e:
            embed.description = "❌ Failed to connect to server!"
            embed.color = interactions.Color.random()
            return await ctx.edit(embed=embed)

        # Validate server response
        server_vars = server_data.get('vars')
        if not server_vars:
            embed.description = "❌ Server is not accessible or invalid!"
            embed.color = interactions.Color.random()
            return await ctx.edit(embed=embed)

        server_name = server_vars.get('sv_projectName', 'Unknown Server')

        # Save server to database
        await cfx.create({
            'server_address': address,
            'server_name': server_name,
            'initial': initial
        })

        embed.description = "✅ Server successfully added!"
        embed.color = interactions.Color.random()
        embed.add_field("Server Name", server_name)
        embed.add_field("Initial", initial)
        await ctx.edit(embed=embed)

    async def get_server_info(self, ctx: PrefixedContext, initial: str, 
                            player_id: Optional[int] = None, 
                            player_name: Optional[str] = None) -> None:
        """Retrieve and display server information with optional player filtering.
        
        Args:
            ctx: Command context
            initial: Server initial identifier
            player_id: Optional player ID filter
            player_name: Optional player name filter
        """
        embed = interactions.Embed(color=interactions.Color.random())

        # Find server by initial
        service = await cfx.get_initial(initial)
        if not service:
            embed.description = "❌ Server not found!"
            embed.color = interactions.Color.random()
            return await ctx.reply(embed=embed)

        # Get player data from server
        cfx_service = CFXService(service.server_address)
        try:
            players_data = await cfx_service.getPlayers()
        except Exception as e:
            embed.description = "❌ Failed to retrieve player data!"
            embed.color = interactions.Color.random()
            return await ctx.reply(embed=embed)

        # Apply filters
        filtered_players = players_data

        # Filter by player ID
        if player_id is not None:
            filtered_players = [p for p in filtered_players if p.get('id') == player_id]

        # Filter by player name
        if player_name:
            name_filtered = []
            for player in filtered_players:
                current_name = player.get('name', '').lower()
                if player_name.lower() in current_name:
                    name_filtered.append({
                        'name': player.get('name', 'Unknown'),
                        'ping': player.get('ping', 0),
                        'id': player.get('id', 0)
                    })
            filtered_players = name_filtered

        # Check if any players found
        if len(filtered_players) < 1:
            embed.description = "❌ No players found matching the criteria!"
            embed.color = interactions.Color.random()
            return await ctx.reply(embed=embed)

        # Create paginated embeds and send
        embeds = self.create_embeds_from_players(service.server_name, filtered_players)
        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        await paginator.reply(ctx)

    @prefixed_command(
        name="fivem",
        help="Display list of players connected to a CFX server with optional filtering",
        usage="<server_initial> [player_id/player_name]"
    )
    async def show_players(self, ctx: PrefixedContext, initial: Optional[str] = None, 
                          *, filter_data: Optional[Union[str, int]] = None) -> None:
        """Show players on a CFX server with optional filtering.
        
        Args:
            ctx: Command context
            initial: Server initial identifier
            filter_data: Optional player ID (int) or name (str) filter
        """
        embed = interactions.Embed(
            description="⏳ Please wait...",
            color=interactions.Color.random()
        )

        # Validate required parameters
        if not initial:
            embed.description = "❌ Usage: `!fivem <server_initial> [player_id/player_name]`"
            embed.color = interactions.Color.random()
            return await ctx.reply(embed=embed)

        # Parse filter data
        player_id = None
        player_name = None

        if filter_data is not None:
            if isinstance(filter_data, str) and filter_data.isdigit():
                player_id = int(filter_data)
            elif isinstance(filter_data, str):
                player_name = filter_data

        await self.get_server_info(ctx, initial, player_id, player_name)
    
    @prefixed_command(
        name="serverlist",
        help="List all registered CFX servers"
    )
    async def list_servers(self, ctx: PrefixedContext) -> None:
        """List all registered CFX servers.

        Args:
            ctx: Command context
        """
        embed = interactions.Embed(color=interactions.Color.random())

        # Retrieve all servers from database
        servers = await cfx.get_multi()
        if not servers:
            embed.description = "❌ No servers registered!"
            embed.color = interactions.Color.random()
            return await ctx.reply(embed=embed)

        # Format server list
        server_lines = []
        for server in servers:
            line = f"`{server.initial}` - {server.server_name}"
            server_lines.append(line)

        embed.title = "Registered CFX Servers"
        embed.description = "\n".join(server_lines)
        embed.footer = f"Total Servers: {len(servers)}"
        await ctx.reply(embed=embed)

    @interactions.slash_command(
        name="delete_server",
        description="Delete a CFX server from the bot"
    )
    @interactions.slash_option(
        "initial",
        "Server initial identifier to delete",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def delete_server(self, ctx: interactions.SlashContext, initial: str) -> None:
        """Delete a server from the database.

        Args:
            ctx: Slash command context
            initial: Server initial identifier
        """
        embed = interactions.Embed(color=interactions.Color.random())

        # Find server by initial
        server = await cfx.get_initial(initial)
        if not server:
            embed.description = f"❌ Server with initial `{initial}` not found!"
            embed.color = interactions.Color.random()
            return await ctx.send(embed=embed)

        # Delete server
        await cfx.delete(server.id)

        embed.description = "✅ Server successfully deleted!"
        embed.color = interactions.Color.random()
        embed.add_field("Server Name", server.server_name)
        embed.add_field("Initial", initial)
        await ctx.send(embed=embed)

    @interactions.slash_command(
        name="update_server",
        description="Update a CFX server's address"
    )
    @interactions.slash_option(
        "initial",
        "Server initial identifier",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    @interactions.slash_option(
        "address",
        "New server address (IP:Port)",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def update_server(self, ctx: interactions.SlashContext, initial: str, address: str) -> None:
        """Update a server's address in the database.

        Args:
            ctx: Slash command context
            initial: Server initial identifier
            address: New server address
        """
        embed = interactions.Embed(
            description="🔍 Updating server...",
            color=interactions.Color.random()
        )
        await ctx.send(embed=embed)

        # Find server by initial
        server = await cfx.get_initial(initial)
        if not server:
            embed.description = f"❌ Server with initial `{initial}` not found!"
            embed.color = interactions.Color.random()
            return await ctx.edit(embed=embed)

        # Test new address
        cfx_service = CFXService(address)
        try:
            server_data = await cfx_service.getInfo()
        except Exception as e:
            embed.description = "❌ Failed to connect to new server address!"
            embed.color = interactions.Color.random()
            return await ctx.edit(embed=embed)

        # Get server name from new address
        server_vars = server_data.get('vars')
        if not server_vars:
            embed.description = "❌ New server address is not accessible or invalid!"
            embed.color = interactions.Color.random()
            return await ctx.edit(embed=embed)

        server_name = server_vars.get('sv_projectName', 'Unknown Server')

        # Update server in database
        await cfx.update(server.id, {
            'server_address': address,
            'server_name': server_name
        })

        embed.description = "✅ Server successfully updated!"
        embed.color = interactions.Color.random()
        embed.add_field("Initial", initial)
        embed.add_field("Old Address", server.server_address)
        embed.add_field("New Address", address)
        embed.add_field("Server Name", server_name)
        await ctx.edit(embed=embed)

    @interactions.slash_command(
        name="test_server",
        description="Test if a CFX server is accessible"
    )
    @interactions.slash_option(
        "initial",
        "Server initial identifier to test",
        required=True,
        opt_type=interactions.OptionType.STRING
    )
    async def test_server(self, ctx: interactions.SlashContext, initial: str) -> None:
        """Test server connectivity and accessibility.

        Args:
            ctx: Slash command context
            initial: Server initial identifier
        """
        embed = interactions.Embed(
            description="🔍 Testing server connection...",
            color=interactions.Color.random()
        )
        await ctx.send(embed=embed)

        # Find server by initial
        server = await cfx.get_initial(initial)
        if not server:
            embed.description = f"❌ Server with initial `{initial}` not found!"
            embed.color = interactions.Color.random()
            return await ctx.edit(embed=embed)

        # Test server connectivity
        cfx_service = CFXService(server.server_address)
        try:
            # Try to get player data
            players_data = await cfx_service.getPlayers()

            # Success - server is accessible
            embed.description = "✅ Server is ONLINE and accessible!"
            embed.color = interactions.Color.random()
            embed.add_field("Server Name", server.server_name)
            embed.add_field("Address", server.server_address)
            embed.add_field("Initial", initial)
            embed.add_field("Players Online", str(len(players_data)))

        except Exception as e:
            # Failed - server is not accessible
            embed.description = "❌ Server is OFFLINE or not accessible!"
            embed.color = interactions.Color.random()
            embed.add_field("Server Name", server.server_name)
            embed.add_field("Address", server.server_address)
            embed.add_field("Initial", initial)
            embed.add_field("Error", f"Connection failed: {type(e).__name__}")

        await ctx.edit(embed=embed)



def setup(bot: interactions.Client) -> None:
    """Set up the CFX extension.
    
    Args:
        bot: The Discord bot client instance
    """
    CfxExtension(bot)