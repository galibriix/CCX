
import random
import discord

from discord.ext import commands


class Coding(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.active_challenges = {}

        self.challenges = [
            {
                "title": "The Even Number Detector",
                "difficulty": "Beginner",
                "language": "Python",
                "description": (
                    "Write a Python program that accepts an integer "
                    "and determines whether it is even or odd."
                ),
                "hint": "Think about the modulo operator: %."
            },
            {
                "title": "The Palindrome Checker",
                "difficulty": "Intermediate",
                "language": "Python",
                "description": (
                    "Write a function that checks whether a word "
                    "reads the same forwards and backwards."
                ),
                "hint": "Compare the original string with its reversed version."
            },
            {
                "title": "The Maximum Finder",
                "difficulty": "Beginner",
                "language": "JavaScript",
                "description": (
                    "Write a function that receives an array of numbers "
                    "and returns the largest number."
                ),
                "hint": "Loop through the array and keep track of the largest value."
            },
            {
                "title": "The Vowel Counter",
                "difficulty": "Beginner",
                "language": "Python",
                "description": (
                    "Create a function that counts the vowels "
                    "in a given string."
                ),
                "hint": "Check each character against a collection of vowels."
            },
            {
                "title": "The Array Reverser",
                "difficulty": "Intermediate",
                "language": "JavaScript",
                "description": (
                    "Write a function that reverses an array "
                    "without using the built-in reverse() method."
                ),
                "hint": "Consider using two pointers or a loop."
            },
            {
                "title": "The FizzBuzz Challenge",
                "difficulty": "Beginner",
                "language": "Python",
                "description": (
                    "Print numbers from 1 to 100. Print Fizz for "
                    "multiples of 3, Buzz for multiples of 5, and "
                    "FizzBuzz for multiples of both."
                ),
                "hint": "Check divisibility by 15 before checking 3 or 5."
            }
        ]

        self.languages = {
            "python": "A versatile language used in automation, AI, backend development and more.",
            "javascript": "A major web programming language used for interactive websites and applications.",
            "html": "A markup language used to structure web pages.",
            "css": "A stylesheet language used to design and style web pages.",
            "php": "A server-side scripting language commonly used for web development.",
            "java": "An object-oriented programming language used in applications and backend systems.",
            "c": "A general-purpose programming language known for low-level control and performance.",
            "cpp": "C++ extends C with features such as classes and templates.",
            "csharp": "C# is a modern programming language commonly used with the .NET platform.",
            "sql": "SQL is used to query and manage relational databases."
        }

        self.debug_tips = [
            "Read the full error message before changing your code.",
            "Check variable names for spelling mistakes.",
            "Use print statements or a debugger to inspect unexpected values.",
            "Test small sections of your program independently.",
            "Check array indexes and loop boundaries.",
            "Make sure functions return the values you expect.",
            "Verify that your database queries use the correct parameters.",
            "Check for missing brackets, quotation marks and indentation."
        ]

    # CODING CHALLENGE

    @commands.hybrid_command(
        name="challenge",
        description="Get a programming challenge."
    )
    @commands.guild_only()
    async def challenge(self, ctx):

        challenge = random.choice(self.challenges)

        self.active_challenges[
            (ctx.guild.id, ctx.author.id)
        ] = challenge

        embed = discord.Embed(
            title=f"💻 {challenge['title']}",
            description=challenge["description"],
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Difficulty",
            value=challenge["difficulty"],
            inline=True
        )

        embed.add_field(
            name="Language",
            value=challenge["language"],
            inline=True
        )

        embed.set_footer(
            text="Use /hint or !hint if you need help."
        )

        await ctx.send(embed=embed)

    # CHALLENGE HINT

    @commands.hybrid_command(
        name="hint",
        description="Get a hint for your current coding challenge."
    )
    @commands.guild_only()
    async def hint(self, ctx):

        challenge = self.active_challenges.get(
            (ctx.guild.id, ctx.author.id)
        )

        if challenge is None:
            return await ctx.send(
                "You don't have an active challenge. "
                "Start one with `/challenge`."
            )

        await ctx.send(
            f"💡 **Hint:** {challenge['hint']}"
        )

    # PROGRAMMING LANGUAGES

    @commands.hybrid_command(
        name="languages",
        description="See the programming languages supported by CCX."
    )
    @commands.guild_only()
    async def languages(self, ctx):

        names = [
            "Python", "JavaScript", "HTML", "CSS", "PHP",
            "Java", "C", "C++", "C#", "SQL"
        ]

        embed = discord.Embed(
            title="🌐 CCX Programming Languages",
            description="\n".join(f"• {name}" for name in names),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    # LANGUAGE INFORMATION

    @commands.hybrid_command(
        name="codeinfo",
        description="Get information about a programming language."
    )
    @commands.guild_only()
    async def codeinfo(self, ctx, *, language: str):

        language = language.lower().strip()

        aliases = {
            "js": "javascript",
            "c++": "cpp",
            "c#": "csharp"
        }

        language = aliases.get(language, language)

        information = self.languages.get(language)

        if information is None:
            return await ctx.send(
                "I don't have information about that language yet. "
                "Try `/languages`."
            )

        embed = discord.Embed(
            title=f"📚 {language.upper()}",
            description=information,
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed)

    # DEBUGGING TIP

    @commands.hybrid_command(
        name="debugtip",
        description="Get a useful programming debugging tip."
    )
    @commands.guild_only()
    async def debugtip(self, ctx):

        tip = random.choice(self.debug_tips)

        embed = discord.Embed(
            title="🐛 CCX Debugging Tip",
            description=tip,
            color=discord.Color.orange()
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Coding(bot))
