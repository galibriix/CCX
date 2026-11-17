
import os
import aiosqlite
import discord

from discord.ext import commands


class Ranking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.getenv("CCX_DATABASE_PATH", "ccx.db")

    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS activity (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    messages INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot or not message.guild:
            return

        content = message.content.strip()

        if not content or content.startswith("!"):
            return

        if self.bot.user and (
            content.startswith(f"<@{self.bot.user.id}>")
            or content.startswith(f"<@!{self.bot.user.id}>")
        ):
            return

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO activity (guild_id, user_id, messages)
                VALUES (?, ?, 1)
                ON CONFLICT(guild_id, user_id)
                DO UPDATE SET messages = messages + 1
            """, (message.guild.id, message.author.id))

            await db.commit()

    # TOP MEMBERS

    @commands.hybrid_command(
        name="topmembers",
        description="View the most active CCX members."
    )
    @commands.guild_only()
    async def topmembers(self, ctx):

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT user_id, messages
                FROM activity
                WHERE guild_id = ?
                ORDER BY messages DESC
                LIMIT 10
            """, (ctx.guild.id,)) as cursor:

                rows = await cursor.fetchall()

        embed = discord.Embed(
            title="👑 CCX Activity Rankings",
            description="Top 10 members by recorded message count.",
            color=discord.Color.blurple()
        )

        if not rows:
            embed.description = "No activity has been recorded yet."

        else:
            ranking = []

            for position, (user_id, messages) in enumerate(rows, start=1):
                member = ctx.guild.get_member(user_id)

                name = (
                    member.display_name
                    if member
                    else f"Member {user_id}"
                )

                ranking.append(
                    f"**{position}. {name}** | {messages:,} messages"
                )

            embed.description = "\n".join(ranking)

        await ctx.send(embed=embed)

    # MEMBER STATISTICS

    @commands.hybrid_command(
        name="mystats",
        description="View your CCX activity statistics."
    )
    @commands.guild_only()
    async def mystats(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        async with aiosqlite.connect(self.db_path) as db:

            async with db.execute("""
                SELECT messages FROM activity
                WHERE guild_id = ? AND user_id = ?
            """, (ctx.guild.id, member.id)) as cursor:

                row = await cursor.fetchone()

            async with db.execute("""
                SELECT COUNT(*) + 1
                FROM activity
                WHERE guild_id = ?
                AND messages > COALESCE((
                    SELECT messages FROM activity
                    WHERE guild_id = ? AND user_id = ?
                ), 0)
            """, (
                ctx.guild.id,
                ctx.guild.id,
                member.id
            )) as cursor:

                position = (await cursor.fetchone())[0]

        messages = row[0] if row else 0

        embed = discord.Embed(
            title=f"📊 {member.display_name}'s CCX Statistics",
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="Recorded Messages",
            value=f"{messages:,}",
            inline=True
        )

        embed.add_field(
            name="Activity Position",
            value=f"#{position}",
            inline=True
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Ranking(bot))
