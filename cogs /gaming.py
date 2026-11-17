
import random
import discord

from discord.ext import commands


class Gaming(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ROCK PAPER SCISSORS

    @commands.hybrid_command(
        name="rps",
        description="Play Rock, Paper, Scissors against CCX."
    )
    @commands.guild_only()
    async def rps(self, ctx, choice: str):

        choice = choice.lower()

        choices = ["rock", "paper", "scissors"]

        if choice not in choices:
            return await ctx.send(
                "Choose: `rock`, `paper`, or `scissors`."
            )

        bot_choice = random.choice(choices)

        if choice == bot_choice:
            result = "🤝 It's a draw!"

        elif (
            (choice == "rock" and bot_choice == "scissors")
            or (choice == "paper" and bot_choice == "rock")
            or (choice == "scissors" and bot_choice == "paper")
        ):
            result = "🎉 You win!"

        else:
            result = "🤖 CCX wins!"

        embed = discord.Embed(
            title="🎮 Rock, Paper, Scissors",
            description=(
                f"You chose: **{choice.title()}**\n"
                f"CCX chose: **{bot_choice.title()}**\n\n"
                f"{result}"
            ),
            color=discord.Color.blurple()
        )

        await ctx.send(embed=embed)

    # NUMBER GUESSING

    @commands.hybrid_command(
        name="guess",
        description="Guess a number between 1 and 10."
    )
    @commands.guild_only()
    async def guess(self, ctx, number: int):

        if not 1 <= number <= 10:
            return await ctx.send(
                "Choose a number between 1 and 10."
            )

        answer = random.randint(1, 10)

        if number == answer:
            result = "🎉 Correct! You guessed it!"

        else:
            result = f"Not quite! The number was **{answer}**."

        await ctx.send(result)

    # COIN FLIP

    @commands.hybrid_command(
        name="coinflip",
        description="Flip a virtual coin."
    )
    @commands.guild_only()
    async def coinflip(self, ctx):

        result = random.choice(["Heads", "Tails"])

        await ctx.send(
            f"🪙 The coin landed on **{result}**!"
        )

    # DICE ROLL

    @commands.hybrid_command(
        name="dice",
        description="Roll a six-sided dice."
    )
    @commands.guild_only()
    async def dice(self, ctx):

        result = random.randint(1, 6)

        await ctx.send(
            f"🎲 You rolled a **{result}**!"
        )


async def setup(bot):
    await bot.add_cog(Gaming(bot))
