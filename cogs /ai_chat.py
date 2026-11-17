
import os
import aiohttp
import discord

from discord.ext import commands


class AIChat(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("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")
        self.model = os.getenv("openai/gpt-4o-mini")
        self.semaphore = __import__("asyncio").Semaphore(3)

        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    @commands.hybrid_command(
        name="ask",
        description="Ask the CCX AI assistant a question."
    )
    @commands.guild_only()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):

        if not self.api_key or not self.model:
            return await ctx.send(
                "⚠️ The AI system is not configured yet."
            )

        if len(question) > 1500:
            return await ctx.send(
                "Your question is too long. Maximum: 1,500 characters."
            )

        await ctx.send("🤖 CCX AI is thinking...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "CCX 2.0"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the CCX AI assistant, part of "
                        "Code Creators X. You help members with "
                        "programming, science, technology, education "
                        "and general questions. Be accurate, friendly "
                        "and clear. Explain code step by step when useful."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            async with self.semaphore:
                timeout = aiohttp.ClientTimeout(total=60)

                async with aiohttp.ClientSession(
                    timeout=timeout
                ) as session:

                    async with session.post(
                        self.api_url,
                        headers=headers,
                        json=payload
                    ) as response:

                        if response.status != 200:
                            return await ctx.send(
                                "⚠️ The AI provider returned an error. "
                                "Please try again later."
                            )

                        data = await response.json()

            answer = data["choices"][0]["message"]["content"]

            if not answer:
                return await ctx.send(
                    "The AI returned an empty response. Try again."
                )

            # Discord messages have a 2,000-character limit.
            for start in range(0, len(answer), 1900):
                await ctx.send(
                    answer[start:start + 1900],
                    allowed_mentions=discord.AllowedMentions.none()
                )

        except aiohttp.ClientError:
            await ctx.send(
                "⚠️ Could not connect to the AI service."
            )

        except (KeyError, IndexError, TypeError):
            await ctx.send(
                "⚠️ The AI returned an unexpected response."
            )

        except TimeoutError:
            await ctx.send(
                "⏳ The AI took too long to respond. Try again."
            )

    @ask.error
    async def ask_error(self, ctx, error):

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Please wait {error.retry_after:.1f} seconds."
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(AIChat(bot))
