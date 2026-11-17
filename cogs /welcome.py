
import os
import discord

from discord.ext import commands


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = os.getenv("1564231824148926565")

    def get_welcome_channel(self, guild):

        if self.welcome_channel_id:
            channel = guild.get_channel(int(self.welcome_channel_id))

            if isinstance(channel, discord.TextChannel):
                return channel

        return guild.system_channel

    def create_welcome_embed(self, member):

        embed = discord.Embed(
            title="🚀 Welcome to Code Creators X!",
            description=(
                f"Welcome {member.mention}!\n\n"
                "**WE CODE. WE CREATE. WE BUILD. WE RISE.**\n\n"
                "You've joined a community of developers, "
                "learners, gamers and creative minds.\n\n"
                "Explore, learn, collaborate and showcase "
                "what you can build!"
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="👤 Member",
            value=member.display_name,
            inline=True
        )

        embed.add_field(
            name="📊 Member Count",
            value=str(member.guild.member_count),
            inline=True
        )

        embed.set_footer(
            text="Code Creators X | CCX 2.0"
        )

        return embed

    # AUTOMATIC WELCOME

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if member.bot:
            return

        embed = self.create_welcome_embed(member)
        channel = self.get_welcome_channel(member.guild)

        if channel:
            try:
                await channel.send(
                    embed=embed,
                    allowed_mentions=discord.AllowedMentions(
                        users=True
                    )
                )
            except discord.Forbidden:
                pass

        # PERSONAL WELCOME DM

        try:
            await member.send(
                embed=discord.Embed(
                    title="Welcome to CCX! 🚀",
                    description=(
                        f"Hello {member.display_name}!\n\n"
                        "Welcome to Code Creators X.\n"
                        "We are glad you've joined our community.\n\n"
                        "Explore the server, meet other members "
                        "and start creating!"
                    ),
                    color=discord.Color.green()
                )
            )
        except discord.Forbidden:
            pass

    # TEST WELCOME SYSTEM

    @commands.hybrid_command(
        name="welcome-test",
        description="Test the CCX welcome message."
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def welcome_test(self, ctx):

        channel = self.get_welcome_channel(ctx.guild)

        if channel is None:
            return await ctx.send(
                "⚠️ No welcome channel is configured. "
                "Set WELCOME_CHANNEL_ID or configure a server system channel."
            )

        embed = self.create_welcome_embed(ctx.author)

        await channel.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none()
        )

        await ctx.send(
            f"✅ Welcome message test sent to {channel.mention}."
        )


async def setup(bot):
    await bot.add_cog(Welcome(bot))
