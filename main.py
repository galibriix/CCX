

import os
import logging
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MTU0MjQ4NTIxNTkyNDk4MTg1MQ.GH2XaA.fB4N4LzYfEleBg4NaaSk4I2R40lgwh109V6d9c")
GUILD_ID = os.getenv("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")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing!")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | CCX 2.0 | %(levelname)s | %(message)s"
)

logger = logging.getLogger("CCX")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class CCXBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):

        extensions = [
            "cogs.moderation",
            "cogs.ai_chat",
            "cogs.levels",
            "cogs.ranking",
            "cogs.gaming",
            "cogs.coding",
            "cogs.welcome",
            "cogs.economy",
            "cogs.administration",
        ]

        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info("Loaded: %s", extension)

            except Exception:
                logger.exception(
                    "Could not load extension: %s",
                    extension
                )

        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

        logger.info("CCX commands synchronized.")

    async def on_ready(self):
        logger.info("CCX 2.0 online as %s", self.user)

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Code Creators X | /help"
            )
        )


bot = CCXBot()


if __name__ == "__main__":
    bot.run(TOKEN)
