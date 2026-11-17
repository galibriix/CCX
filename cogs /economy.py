
import os
import time
import random
import aiosqlite
import discord

from discord.ext import commands


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.getenv("CCX_DATABASE_PATH", "ccx.db")

    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS economy (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    balance INTEGER DEFAULT 0,
                    daily_claim INTEGER DEFAULT 0,
                    work_claim INTEGER DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

    async def get_balance(self, guild_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT balance FROM economy
                WHERE guild_id = ? AND user_id = ?
            """, (guild_id, user_id)) as cursor:
                row = await cursor.fetchone()

        return row[0] if row else 0

    async def ensure_account(self, db, guild_id, user_id):
        await db.execute("""
            INSERT OR IGNORE INTO economy
            (guild_id, user_id, balance)
            VALUES (?, ?, 0)
        """, (guild_id, user_id))

    # BALANCE

    @commands.hybrid_command(
        name="balance",
        description="Check your Code Coins balance."
    )
    @commands.guild_only()
    async def balance(self, ctx, member: discord.Member = None):

        member = member or ctx.author

        coins = await self.get_balance(
            ctx.guild.id,
            member.id
        )

        embed = discord.Embed(
            title=f"🪙 {member.display_name}'s Wallet",
            description=f"**{coins:,} CC**",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    # DAILY REWARD

    @commands.hybrid_command(
        name="daily",
        description="Claim your daily Code Coins."
    )
    @commands.guild_only()
    async def daily(self, ctx):

        now = int(time.time())
        reward = random.randint(50, 100)

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("BEGIN IMMEDIATE")

            await self.ensure_account(
                db, ctx.guild.id, ctx.author.id
            )

            async with db.execute("""
                SELECT daily_claim FROM economy
                WHERE guild_id = ? AND user_id = ?
            """, (ctx.guild.id, ctx.author.id)) as cursor:
                row = await cursor.fetchone()

            last_claim = row[0]

            if now - last_claim < 86400:
                remaining = 86400 - (now - last_claim)
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60

                await db.rollback()

                return await ctx.send(
                    f"⏳ You've already claimed your daily reward. "
                    f"Try again in {hours}h {minutes}m."
                )

            await db.execute("""
                UPDATE economy
                SET balance = balance + ?, daily_claim = ?
                WHERE guild_id = ? AND user_id = ?
            """, (
                reward, now,
                ctx.guild.id, ctx.author.id
            ))

            await db.commit()

        await ctx.send(
            f"🎁 You received **{reward} CC** as your daily reward!"
        )

    # WORK REWARD

    @commands.hybrid_command(
        name="work",
        description="Complete a virtual job to earn Code Coins."
    )
    @commands.guild_only()
    async def work(self, ctx):

        now = int(time.time())
        cooldown = 3600
        reward = random.randint(20, 60)

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("BEGIN IMMEDIATE")

            await self.ensure_account(
                db, ctx.guild.id, ctx.author.id
            )

            async with db.execute("""
                SELECT work_claim FROM economy
                WHERE guild_id = ? AND user_id = ?
            """, (ctx.guild.id, ctx.author.id)) as cursor:
                row = await cursor.fetchone()

            last_work = row[0]

            if now - last_work < cooldown:
                remaining = cooldown - (now - last_work)
                minutes = remaining // 60
                seconds = remaining % 60

                await db.rollback()

                return await ctx.send(
                    f"⏳ Your next virtual job is available in "
                    f"{minutes}m {seconds}s."
                )

            await db.execute("""
                UPDATE economy
                SET balance = balance + ?, work_claim = ?
                WHERE guild_id = ? AND user_id = ?
            """, (
                reward, now,
                ctx.guild.id, ctx.author.id
            ))

            await db.commit()

        jobs = [
            "fixed a Python bug",
            "built a website",
            "completed a coding task",
            "designed a user interface",
            "helped debug a project"
        ]

        await ctx.send(
            f"💻 You {random.choice(jobs)} "
            f"and earned **{reward} CC**!"
        )

    # TRANSFER COINS

    @commands.hybrid_command(
        name="pay",
        description="Transfer Code Coins to another member."
    )
    @commands.guild_only()
    async def pay(
        self,
        ctx,
        member: discord.Member,
        amount: int
    ):

        if member.bot:
            return await ctx.send(
                "❌ You cannot transfer coins to bots."
            )

        if member.id == ctx.author.id:
            return await ctx.send(
                "❌ You cannot pay yourself."
            )

        if amount <= 0:
            return await ctx.send(
                "❌ Enter an amount greater than zero."
            )

        if amount > 1_000_000:
            return await ctx.send(
                "❌ The maximum transfer is 1,000,000 CC."
            )

        async with aiosqlite.connect(self.db_path) as db:

            await db.execute("BEGIN IMMEDIATE")

            await self.ensure_account(
                db, ctx.guild.id, ctx.author.id
            )

            await self.ensure_account(
                db, ctx.guild.id, member.id
            )

            async with db.execute("""
                SELECT balance FROM economy
                WHERE guild_id = ? AND user_id = ?
            """, (ctx.guild.id, ctx.author.id)) as cursor:
                row = await cursor.fetchone()

            balance = row[0]

            if balance < amount:
                await db.rollback()

                return await ctx.send(
                    f"❌ Insufficient funds. Your balance is "
                    f"**{balance:,} CC**."
                )

            await db.execute("""
                UPDATE economy
                SET balance = balance - ?
                WHERE guild_id = ? AND user_id = ?
            """, (amount, ctx.guild.id, ctx.author.id))

            await db.execute("""
                UPDATE economy
                SET balance = balance + ?
                WHERE guild_id = ? AND user_id = ?
            """, (amount, ctx.guild.id, member.id))

            await db.commit()

        await ctx.send(
            f"💸 {ctx.author.mention} transferred "
            f"**{amount:,} CC** to {member.mention}!"
        )

    # RICHEST MEMBERS

    @commands.hybrid_command(
        name="richest",
        description="View the richest CCX members."
    )
    @commands.guild_only()
    async def richest(self, ctx):

        async with aiosqlite.connect(self.db_path) as db:

            async with db.execute("""
                SELECT user_id, balance
                FROM economy
                WHERE guild_id = ?
                ORDER BY balance DESC
                LIMIT 10
            """, (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        embed = discord.Embed(
            title="💰 CCX Richest Members",
            description="Top 10 Code Coins holders.",
            color=discord.Color.gold()
        )

        if not rows:
            embed.description = "The economy is waiting for its first coins!"

        else:
            lines = []

            for position, (user_id, balance) in enumerate(rows, start=1):

                member = ctx.guild.get_member(user_id)

                name = (
                    member.display_name
                    if member
                    else f"Member {user_id}"
                )

                lines.append(
                    f"**{position}. {name}** | {balance:,} CC"
                )

            embed.description = "\n".join(lines)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
