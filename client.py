#!/usr/bin/env python

"""Client module that contains all the twisted bits to keep clubot alive.

This module contains the CluBot class for IRC actions, CluBotFactory to
set up the clubot protocol, and CluBotContextFactory for ssl support.
"""

from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
from twisted.python import rebuild

#import cmds
import random
from chatter import Chatter


class CluBot(irc.IRCClient):
    """Main bot interface with IRC happenings

    This class hooks into various IRC actions and handles them appropriately.

    """

    @property
    def _get_nickname(self):
        return self.factory.nickname

    nickname = _get_nickname

    def __init__(self):
        self.nicks = []
        self.chat = Chatter()
        self.chat.load_bot("alice")
        
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        for chan in self.factory.channels:
            self.join(chan)

    def joined(self, channel):
        """on channel join, clubot gets everyone's nicks"""
        self.sendLine('NAMES')

    def privmsg(self, user, channel, msg):
        """Handles user messages from channels

        This hooks every privmsg sent to the channel and sends the commands off
        to cmds.dispatch to process, then replies to the channel accordingly.

        The !reload command needs to be handled here though, as it allows edits
        to be made to clubot without disconnecting from IRC. It should get a
        list from cmds.dispatch if it needs to pm someone, otherwise it gets a
        string back and msgs the channel.

        """
        user = user.split('!', 1)[0]
        reply = self.chat.get_reply(msg)
        self.msg(channel, reply)        

class ChatBotFactory(protocol.ClientFactory):
    """Subclass of ClientFactory for clubot protocol"""

    protocol = CluBot

    def __init__(self, channels, nickname):
        self.channels = channels
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print 'connection lost',
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed',


class ChatBotContextFactory(ssl.ClientContextFactory):
    """Subclass of ClientContextFactory for ssl connection"""

    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        return ctx
