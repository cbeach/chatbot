#!/usr/bin/env python

"""the voice of clubot

This module contains all the replies clubot can send to a channel,
organized into the various contexts that clubot should say something.

By pulling all the fun replies out of client.py and cmds.py, more responses
can be added and reloaded without disconnecting from IRC. Help is also in
this module to minimize the code in cmds.py.

"""

user_joined = {'#clubot': [", welcome to the testing grounds"],
               '#movies': [", welcome to the grid, where i am imdb",
                           ", welcome user"]}

user_left = ["one less user, excellent",
             "guess someone didn't want to be here",
             "looks like the end of line for them"]

joined = ["i will create the perfect system",
          "let's see if i work this time around",
          "i'm back"]

saw_kick = [", we're closer to a perfect system",
            ", you get to have all the fun"]

bad_cmd = ["you know nothing of my commands, try '!help'",
           "not sure what you're trying to do there",
           "user error detected"]

missing_arg = ["close to perfection, try '!help [cmd]'",
               "i sense a flaw in your command"]

no_match = ["i have no idea where that is",
            "not in the cards, not for you",
            "no results with that information"]

no_more = ["nothing else to say user",
           "i have no more to say to you"]

help = {'': "link | plot | seen | quote | rate | another | more | source " \
            "| todo | help [cmd]",
        'link': "link <title>: returns a link to the imdb page for the " \
            "first matching movie title",
        'plot': "plot <title>: returns a plot summary of the first movie " \
            "to match <title>. if the plot summary is too long, use '!more' " \
            "to see the rest.",
        'seen': "seen <person>: displays a list of movies you may have seen " \
            "the person in. the list is ordered newest to oldest and the " \
            "person can be an actress, actor, or director.",
        'quote': "quote <title>: returns a random quote from the first movie " \
            "that matches <title>. !another means another quote, and clubot " \
            "will say a line for each line of conversation in the quote.",
        'rate': "rate <title>: get a rating out of ten for the matching " \
            "<title> and the number of votes that got it rated. !another " \
            "gives the rating of another match.",
        'another': "another: if the first matching movie for your last " \
            "command wasn't right, repeat the last command with another " \
            "match (up to 4 more times)",
        'more': "more: see the rest of whatever text was last returned",
        'source': "source: gives the github link for my bits and pieces",
        'todo': "todo <thing>: if anyone has any bright ideas, add them " \
            "here and the user might get around to them. if <thing> is " \
            "'show', i'll show you the current todo list."}

addressed = [", all my commands start with '!'",
             ", you know nothing of what i can do, see '!help'",
             ", that's not how to issue commands, see '!help'"]

karma_up = ["++, maybe users aren't that bad...",
            "++, you've now avoided deresolution",
            "++ is exempt from deresolution"]

karma_down = ["--, somebody kick the user",
              "-- is not worth my time",
              "-- is subject to immediate deresolution"]

mode_set = ["i feel... different"]
