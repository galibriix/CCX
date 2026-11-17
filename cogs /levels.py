
import os
import time
import random
import math
import aiosqlite
import discord

from discord.ext import commands


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.getenv("CCX_DATABASE_PATH", "ccx.db")
        self.cooldowns = {}

    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    xp INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

    def calculate_level(self, xp):
        return math.isqrt(xp // 100)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot or not message.guild:
            return

        if not message.content.strip() or len(message.content.strip()) < 5:
            return

        # Do not reward prefix commands.
        if message.content.startswith("!"):
            return

        if self.bot.user and (
            message.content.startswith(f"<@{self.bot.user.id}>")
            or message.content.startswith(f"<@!{self.bot.user.id}>")
        ):
            return

        key = (message.guild.id, message.author.id)
        now = time.monotonic()

        # One XP reward per member every 60 seconds.
        if now - self.cooldowns.get(key, 0) < 60:
            return

        self.cooldowns[key] = now
        earned_xp = random.randint(10, 20)

        async with aiosqlite.connect(self.db_path) as db:

            async with db.execute(
                """
                SELECT xp FROM levels
                WHERE guild_id = ? AND user_id = ?
                """,
                key
            ) as cursor:
                row = await cursor.fetchone()

            old_xp = row[0] if row else 0
            old_level = self.calculate_level(old_xp)
            new_xp = old_xp + earned_xp
            new_level = self.calculate_level(new_xp)

            await db.execute(
                """
                INSERT INTO levels (guild_id, user_id, xp)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id, user_id)
                DO UPDATE SET xp = excluded.xp
                """,
                (message.guild.id, message.author.id, new_xp)
            )

            await db.commit()

        if new_level > old_level:
            await message.channel.send(
                f"🎉 {message.author.mention}, you've reached "
                f"**Level {new_level}**!\n"
                f"Keep coding, creating and building!"
            )

    # RANK COMMAND

    @commands.hybrid_command(
        name="rank",
        description="Check your CCX XP and level."
    )
    @commands.guild_only()
    async def rank(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        async with aiosqlite.connect(self.db_path) as db:

            async with db.execute(
                """
                SELECT xp FROM levels
                WHERE guild_id = ? AND user_id = ?
                """,
                (ctx.guild.id, member.id)
            ) as cursor:
                row = await cursor.fetchone()

            if row is None:
                xp = 0
            else:
                xp = row[0]

            async with db.execute(
                """
                SELECT COUNT(*) + 1 FROM levels
                WHERE guild_id = ? AND xp > ?
                """,
                (ctx.guild.id, xp)
            ) as cursor:
                position = (await cursor.fetchone())[0]

        level = self.calculate_level(xp)
        next_level_xp = 100 * (level + 1) ** 2
        progress = xp - (100 * level ** 2)
        needed = next_level_xp - (100 * level ** 2)

        embed = discord.Embed(
            title=f"🏆 {member.display_name}'s CCX Rank",
            color=discord.Color.blurple()
        )

        embed.add_field(name="Level", value=str(level))
        embed.add_field(name="Total XP", value=f"{xp:,}")
        embed.add_field(name="Server Position", value=f"#{position}")
        embed.add_field(
            name="Next Level",
            value=f"{progress}/{needed} XP"
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    # LEADERBOARD COMMAND

    @commands.hybrid_command(
        name="leaderboard",
        description="View the top CCX members by XP."
    )
    @commands.guild_only()
    async def leaderboard(self, ctx):

        async with aiosqlite.connect(self.db_path) as db:

            async with db.execute(
                """
                SELECT user_id, xp FROM levels
                WHERE guild_id = ?
                ORDER BY xp DESC
                LIMIT 10
                """,
                (ctx.guild.id,)
            ) as cursor:
                rows = await cursor.fetchall()

        embed = discord.Embed(
            title="🏆 CCX XP Leaderboard",
            description="The top 10 members in this server.",
            color=discord.Color.gold()
        )

        if not rows:
            embed.description = "No members have earned XP yet."

        else:
            lines = []

            for position, (user_id, xp) in enumerate(rows, start=1):
                member = ctx.guild.get_member(user_id)

                name = (
                    member.display_name
                    if member
                    else f"Member {user_id}"
                )

                level = self.calculate_level(xp)

                lines.append(
                    f"**{position}. {name}**"
                    f" | Level {level} | {xp:,} XP"
                )

            embed.description = "\n".join(lines)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Levels(bot))
