#!/usr/bin/env python

"""Bot class and main method.

This module contains the Bot class that is chatbotbot and the main method to
connect and join irc channels, then stick around for commands.
"""

from twisted.internet import reactor
from client import ChatBotFactory, ChatBotContextFactory


class Bot:
    """Bot instance for chatbotbot

    This defines the instance and connection parameters for chatbotbot, and
    also contains a method to connect via ssl and start the reactor.
    """

    def __init__(self):
        """chatbotbot info for connecting and joining channels"""
        self.host = 'irc.cat.pdx.edu'
        self.port = 6697
        self.chans = ['#alice-bot']
        self.nick = 'Alice-bot'

    def start(self):
        """connects over ssl to the irc server and starts the reactor"""
        reactor.connectSSL(self.host, self.port,
                           ChatBotFactory(self.chans, self.nick),
                           ChatBotContextFactory())
        reactor.run()


def main():
    """initializes chatbotbot and starts the connection to irc"""

    chatbot = Bot()
    chatbot.start()

if __name__ == "__main__":
    main()
