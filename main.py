# This example requires the 'message_content' privileged intent to function.
import asyncio
import os
import json

from mooncake import Mooncake, intents

discord_secret_path = os.path.abspath('credentials/mooncake_discord_secret.json')


def load_discord_secret(filename):
    data = None
    with open(filename) as f:
        data = json.load(f)

    if not data:
        raise Exception('Cannot load discord secret')

    discord_bot_secret = data['discord_bot_secret']

    return discord_bot_secret


def main():
    token = load_discord_secret(discord_secret_path)
    client = Mooncake(intents=intents)
    client.run(token)


if __name__ == '__main__':
    main()
