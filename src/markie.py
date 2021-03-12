from sys import exit as sys_exit
from random import randrange
from os.path import abspath
import re
import asyncio
import discord
import markov


m_instance = markov.init()


crit = lambda n: randrange(1, n + 1) == n


async def init_bot(bot_token):
    TRIGGER_PATTERN = re.compile("^(oh (hi|hey|hello)|yo) mark", flags=re.I)
    client = discord.Client()

    @client.event
    async def on_ready():
        print("markie.py is online 🤓 (as: {0.user})\n-----".format(client))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if re.match(TRIGGER_PATTERN, message.content):
            await message.channel.trigger_typing()
            response = markov.random_walk(m_instance)
            print(
                "@{0.author} called Markov in #{0.channel} on '{0.guild.name}'\n(Guild ID: {0.guild.id})\nResponding with this generated message:\n{1}\n-----".format(
                    message, response
                )
            )
            await message.channel.send(response)

    print("Connecting markiepy with token in './BOT_TOKEN'...")
    try:
        await client.login(bot_token)
        await client.connect()
    except:
        print(
            "Wellp, that's not good. Failed to connect bot to Discord with token: {}".format(
                bot_token
            )
        )


if __name__ == "__main__":
    TOKEN = abspath("./BOT_TOKEN")
    with open(TOKEN) as token_file:
        TOKEN = token_file.read().strip()
        if not TOKEN:
            sys_exit(
                "You did it again... place Discord bot token in new file './BOT_TOKEN' before starting."
            )
    asyncio.run(init_bot(TOKEN))
