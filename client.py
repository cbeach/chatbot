#!/usr/bin/env python

"""Client module that contains all the twisted bits to keep clubot alive.

This module contains the CluBot class for IRC actions, CluBotFactory to
set up the clubot protocol, and CluBotContextFactory for ssl support.
"""

from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
from twisted.python import rebuild

#import cmds
import voice
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
        self.msg(channel, random.choice(voice.joined))

    def irc_RPL_NAMREPLY(self, prefix, params):
        """unions NAMES and nicks from nicks.log to avoid greeting flappers

        This method is called whenever a reply to NAMES is sent back from the
        IRC server. It puts those names in a list, stripping the voices/ops
        characters, then unions that list with a list of saved nicks. This
        new list is then stored so whenever people join that have already been
        in the channel, clubot doesn't greet them again.

        """

        from_split = params[3].split()
        for e in from_split:
            if e[0] in '+@':
                e = e[1:]
            self.nicks.append(e)

        nick_file = open('./nicks.log', 'a+')
        nick_file.seek(0, 0)
        from_file = nick_file.readlines()
        from_file = [l[:-1] for l in from_file]

        self.nicks = list(set(self.nicks) | set(from_file))

        to_write = [e + '\n' for e in self.nicks]
        nick_file.seek(0, 0)
        nick_file.writelines(to_write)
        nick_file.close()

    def irc_NICK(self, prefix, params):
        """adds the new nick to the list of nicks not to greet"""
        if params:
            self.nicks.append(params[0])
            nick_file = open('./nicks.log', 'a+')
            nick_file.write(params[0] + '\n')
            nick_file.close()

    def userKicked(self, kickee, channel, kicker, message):
        self.msg(channel, kicker + random.choice(voice.saw_kick))

    def userJoined(self, user, channel):
        """greets a new user to the channel"""
        if user not in self.nicks:
            self.msg(channel, user + random.choice(voice.user_joined[channel]))
            self.nicks.append(user)
            nick_file = open('./nicks.log', 'a+')
            nick_file.write(user + '\n')
            nick_file.close()

    def userLeft(self, user, channel):
        self.msg(channel, random.choice(voice.user_left))

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

    def modeChanged(self, user, channel, set, modes, args):
        """responds is clubot is given a mode"""
        if args and args[0] == self.nickname:
            self.msg(channel, random.choice(voice.mode_set))


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
