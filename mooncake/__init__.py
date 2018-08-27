import datetime
import pprint

import discord

from discord.ext import tasks

import mooncake.responders.basic
from mooncake import responders

from collections import namedtuple
import re

Responder = namedtuple('Responder', ['name', 'matcher', 'handler', 'help'])

CHANNEL_ID = 1172226335985381397 # Terminal DMGers/reminders
# CHANNEL_ID = 482629422181122051  # l.k.n/general
# CHANNEL_ID = 1109390991217143928  # kentus.net/#2-dirty


class Mooncake(discord.Client):
    response_map = [
        Responder(
            name='hello',
            matcher=re.compile(r'.*hello.*'),
            handler=responders.basic.respond_quotes,
            help='Greeting.',
        ),
        Responder(
            name='who',
            matcher=re.compile(r'.*who.*'),
            handler=responders.basic.respond_mooncake_picture,
            help='A nice picture of me.',
        ),
        Responder(
            name='rally',
            matcher=re.compile(r'.*rally.*'),
            handler=responders.calendar.respond_rally,
            help='Currently existing DiRT Rally 2.0 events.',
        ),
        Responder(
            name='help',
            matcher=re.compile(r'.*help.*'),
            handler=lambda x: respond_help(Mooncake, x),
            help='What I can do.',
        )
    ]

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def setup_hook(self) -> None:
        self.announce_rally.start()

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        mention = f'<@{self.user.id}>'

        # print(mention)
        # pprint.pprint(message)
        # pprint.pprint(message.content)

        if mention in message.content:
            for responder in self.response_map:
                if responder.matcher.match(message.content):
                    await message.reply(responder.handler(message) or 'I have nothing to say.', mention_author=True)

    @tasks.loop(minutes=5)
    async def announce_rally(self):
        if datetime.datetime.utcnow().hour == 8:  # 8 UTC == 10 CEST
            message = [responders.calendar.announce_rally_next(), responders.calendar.announce_rally_end()]
            if any(message):
                message = '\n'.join(message)
                message_channel = self.get_channel(CHANNEL_ID)
                await message_channel.send(message)

    @announce_rally.before_loop
    async def announce_rally_before(self):
        await self.wait_until_ready()


def respond_help(self, message):
    result = ["I can do:"]
    for responder in self.response_map:
        result.append(f'* {responder.name} -- {responder.help}')
    result.append(mooncake.responders.basic.respond_quotes(message))
    return '\n'.join(result)


intents = discord.Intents.default()
intents.message_content = True
