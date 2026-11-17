
import discord
from discord.ext import commands
from datetime import timedelta


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def check_target(self, ctx, target):
        """Check whether the moderator and bot can act on the target."""

        if target.id == ctx.author.id:
            return "You cannot moderate yourself."

        if target.id == ctx.guild.owner_id:
            return "You cannot moderate the server owner."

        if ctx.author.id != ctx.guild.owner_id:
            if target.top_role >= ctx.author.top_role:
                return "You cannot moderate someone with an equal or higher role."

        bot_member = ctx.guild.me

        if target.top_role >= bot_member.top_role:
            return "My role must be higher than the target's role."

        return None

    # TIMEOUT

    @commands.hybrid_command(
        name="timeout",
        description="Temporarily timeout a member."
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.guild_only()
    async def timeout(
        self,
        ctx,
        member: discord.Member,
        minutes: int,
        *,
        reason: str = "No reason provided"
    ):

        if not 1 <= minutes <= 40320:
            return await ctx.send(
                "Duration must be between 1 and 40,320 minutes."
            )

        error = await self.check_target(ctx, member)

        if error:
            return await ctx.send(error)

        until = discord.utils.utcnow() + timedelta(minutes=minutes)

        await member.timeout(until, reason=reason)

        await ctx.send(
            f"⏱️ **{member}** has been timed out for "
            f"**{minutes} minutes**.\nReason: {reason}"
        )

        try:
            await member.send(
                f"You have been timed out in **{ctx.guild.name}** "
                f"for {minutes} minutes.\nReason: {reason}"
            )
        except discord.Forbidden:
            pass

    # REMOVE TIMEOUT

    @commands.hybrid_command(
        name="untimeout",
        description="Remove a member's timeout."
    )
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @commands.guild_only()
    async def untimeout(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        error = await self.check_target(ctx, member)

        if error:
            return await ctx.send(error)

        await member.timeout(None, reason=reason)

        await ctx.send(
            f"✅ Timeout removed for **{member}**.\n"
            f"Reason: {reason}"
        )

    # KICK

    @commands.hybrid_command(
        name="kick",
        description="Kick a member from CCX."
    )
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        error = await self.check_target(ctx, member)

        if error:
            return await ctx.send(error)

        try:
            await member.send(
                f"You have been kicked from **{ctx.guild.name}**.\n"
                f"Reason: {reason}"
            )
        except discord.Forbidden:
            pass

        await member.kick(reason=reason)

        await ctx.send(
            f"👢 **{member}** has been kicked.\nReason: {reason}"
        )

    # BAN

    @commands.hybrid_command(
        name="ban",
        description="Ban a member from CCX."
    )
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "No reason provided"
    ):

        error = await self.check_target(ctx, member)

        if error:
            return await ctx.send(error)

        try:
            await member.send(
                f"You have been banned from **{ctx.guild.name}**.\n"
                f"Reason: {reason}"
            )
        except discord.Forbidden:
            pass

        await member.ban(
            reason=reason,
            delete_message_seconds=0
        )

        await ctx.send(
            f"🔨 **{member}** has been banned.\nReason: {reason}"
        )

    # COMMAND ERROR HANDLING

    async def cog_command_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ You do not have permission to use this command."
            )

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "❌ CCX 2.0 is missing the required server permissions."
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ A required argument is missing. Check the command usage."
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ I couldn't find that member.")

        else:
            raise error


async def setup(bot):
    await bot.add_cog(Moderation(bot))

