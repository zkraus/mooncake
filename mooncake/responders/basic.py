import random

from mooncake.responses import quotes

def respond_quotes(message):
    return random.choice(quotes)


def respond_mooncake_picture(message):
    return r'https://vignette.wikia.nocookie.net/final-space/images/6/64/Mooncake-MP.png/revision/latest?cb=20180314071330'

