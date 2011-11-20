#!/usr/bin/env python

"""The meat and bones of clubot functionality.

This is where most of the work was put in on clubot to process all the
commands and return appropriate replies. The class is used through the
dispatch method, which calls the proper command function

"""

import re
import voice
import random

import imdb
from imdb.Movie import Movie
from imdb.Person import Person

import inspect
import locale

MSG_LEN = 300
MSG_SPLIT = 297

class CluCmds(object):
    """class containing methods for clubot commands

    This is where the magic happens, and with all the commands in a class,
    clubot can now save last queries, leading to an eventual !more method.

    """

    def __init__(self):
        """initializes clubot workings

        This will start the clubot cmds going by starting an imdb instance,
        list of commands, and soon to be cool features for pagination.

        """
        self.cmdlist = []
        self._update_cmdlist()
        self.portal = imdb.IMDb()
        self.portal.do_adult_search(False)
        self.results = {}
        self.max_results = 5
        self.bookmark = ""

    def _update_cmdlist(self):
        """called to update the list of callable commands"""
        self.cmdlist = []
        for name in inspect.getmembers(self):
            if inspect.ismethod(name[1]):
                if not name[0].startswith('_') and not name[0] == "dispatch":
                    self.cmdlist += [name[0]]

    def _break_msg(self, msg):
        """breaks reply into parts if too long, sets bookmark accordingly"""
        reply = ''
        if len(msg) > MSG_LEN:
            # break on whitespace
            index = -1
            while msg[:MSG_SPLIT][index] is not ' ':
                index -= 1
            index += MSG_SPLIT
            reply = msg[:index] + "..."
            self.bookmark = "..." + msg[index + 1:]
        else:
            self.bookmark = ""
        return reply

    def _set_results(self, results, key):
        """sets self.results to four more results for !another"""
        if key == 'quote':
            pop_index = random.randint(0, len(results)) - 1
        else:
            pop_index = 0
        first = results.pop(pop_index)

        if len(results) <= self.max_results:
            self.results = {key: results}
        else:
            self.results = {key: results[1:self.max_results]}

        return first

    def link(self, *args):
        """gives title and link to first matching movie

        This takes a movie title as an arg and returns a link to the IMDb page.
        First, self.results is checked if this method was called from another,
        then assigns the movie properly.

        """

        response = ''

        if args and not args[0]:
            return random.choice(voice.missing_arg)
        args = args[0]
        movie = args

        # check if call is from dispatch or another, then assign movie
        if not isinstance(args, Movie):
            movie_results = self.portal.search_movie(args)
            movie = self._set_results(movie_results, 'link')

        title = movie['long imdb title']
        response = title.encode('ascii', 'ignore') + ": " \
            + self.portal.get_imdbURL(movie)

        return response

    def plot(self, *args):
        """takes a movie title and returns the first match's plot summary

        This method finds the plot of the first matching movie and returns it.
        First, self.results is checked if this method was called from another,
        then assigns the movie properly.

        It also saves the text that won't fit in a message to self.bookmark,
        which can be called later. Because imdb changed some things on their
        end, i have to default to 'plot outline' if 'plot' is not found.

        '...' is used to denote more text at the end of a plot response.

        """

        response = ''

        if args and not args[0]:
            return random.choice(voice.missing_arg)
        args = args[0]
        movie = args

        # check if call is from dispatch or another, then assign movie
        if not isinstance(args, Movie):
            movie_results = self.portal.search_movie(args)
            movie = self._set_results(movie_results, 'plot')

        title = movie['long imdb title'].encode("ascii", "ignore")
        movie_id = self.portal.get_imdbID(movie)
        movie_plot = self.portal.get_movie_plot(movie_id)
        plot_data = movie_plot['data']

        # check 'plot' versus 'plot outline'
        try:
            if plot_data:
                plot = plot_data['plot'][0]
            else:
                main = self.portal.get_movie_main(movie_id)
                plot = main['data']['plot outline']
        except KeyError:
            response = random.choice(voice.no_match)
        else:
            # format response
            plot = title + ": " + plot.encode('ascii', 'ignore')
            plot = plot.replace(" (qv)", "").rsplit('::', 1)[0]
            response = self._break_msg(plot)

        return response

    def seen(self, *args):
        """returns a list of movies that the person in args was in

        This method takes an actor, actress, or director and returns a list
        of movies, from newest to oldest, that the person was involved in.
        Up to five people are stored for !another, and !more is used with
        self.bookmark.

        """

        response = ''

        if args and not args[0]:
            return random.choice(voice.missing_arg)
        args = args[0]
        person = args

        # check if call is from dispatch or another, then assign movie
        if not isinstance(args, Person):
            person_results = self.portal.search_person(args)
            person = self._set_results(person_results, 'seen')

        person_id = self.portal.get_imdbID(person)
        filmography = self.portal.get_person_filmography(person_id)['data']

        try:
            if filmography:
                # ladies first
                if 'actress' in filmography.keys():
                    movies = filmography['actress']
                elif 'actor' in filmography.keys():
                    movies = filmography['actor']
                elif 'director' in filmography.keys():
                    movies = filmography['director']
                else:
                    movies = filmography['self']
        except KeyError:
            response = random.choice(voice.no_match)
        else:
            # format response
            movies = [movie['long imdb title'] for movie in movies]
            seen = [movie.encode("ascii", "ignore") for movie in movies]
            reply = person['name'].encode("ascii", "ignore") + \
                ": " + ", ".join(seen)
            response = self._break_msg(reply)

        return response

    def quote(self, *args):
        """returns random quotes from first matching movie

        This method takes in a movie title argument and returns a list
        containing the quote strings, since it could be a conversation.

        !another in this case gives another quote, not another matching
        movie, so arguments need to be precise. There are several hacks
        that needed to happen to reformat the quotes for displaying.

        clubot will give a line to the channel for each line of the quote,
        so this may mean more spam than !plot.

        """

        if args and not args[0]:
            return random.choice(voice.missing_arg)
        args = args[0]
        quote = args

        # check if called from !another
        if not isinstance(args, list):
            movie = self.portal.search_movie(args)[0]
            movie_id = self.portal.get_imdbID(movie)
            quotes = self.portal.get_movie_quotes(movie_id)
            
            try:
                quotes = quotes['data']['quotes']
                # keep long quotes out
                quotes = filter(lambda x: len(x) <= 10, quotes)
                quote = self._set_results(quotes, 'quote')
            except KeyError:
                return random.choice(voice.no_match)

        # clean up quote formatting
        quote = [line.encode("ascii", "ignore") for line in quote]
        quote = [line.replace(" (qv)", "") for line in quote]
        quote[-1] = quote[-1].replace("Share this quote", "")
        if quote[-1].endswith(' '):
            quote[-1] = quote[-1][:-1]

        return quote

    def rate(self, *args):
        """displays the rating of the matching movie out of ten

        This command fetches the out-of-ten rating for a matching movie and
        returns it formatted with the title. !another will rate another match.

        """
        response = ''

        if args and not args[0]:
            return random.choice(voice.missing_arg)
        args = args[0]
        movie = args

        # check if call is from dispatch or another, then assign movie
        if not isinstance(args, Movie):
            movie_results = self.portal.search_movie(args)
            movie = self._set_results(movie_results, 'rate')

        title = movie['long imdb title'].encode("ascii", "ignore")
        movie_id = self.portal.get_imdbID(movie)
        movie_votes = self.portal.get_movie_vote_details(movie_id)
        vote_data = movie_votes['data']

        # check if movie has rating
        if vote_data:
            rating = vote_data['rating']
            locale.setlocale(locale.LC_ALL, 'en_US')
            total = locale.format("%d", vote_data['votes'], grouping=True)
            response = title + " is rated " + str(rating) + "/10 after " \
                + str(total) + " votes."
        else:
            response = random.choice(voice.no_match)

        return response

    def another(self, *args):
        """repeats the last command with the next matching movie

        self.results saves the last command and a list of matching movies.
        This method is called when the first movie didn't satisfy the user
        and repeats whatever the last command was with another match.

        """

        if self.results and self.results.values()[0]:
            if self.results.keys()[0] == 'quote':
                movie = self.results.values()[0].pop(
                    random.randint(0, len(self.results.values()[0])) - 1)
            else:
                movie = self.results.values()[0].pop(0)
            return getattr(self, self.results.keys()[0])(movie)
        else:
            return random.choice(voice.no_more)

    def more(self, *args):
        """sends more info from last_query to channel

        This sends more text from self.bookmark to the channel if self.bookmark
        has left over text from previous calls.

        """

        response = ''

        if self.bookmark:
            if len(self.bookmark) > MSG_LEN:
                # break on whitespace
                index = -1
                while self.bookmark[:MSG_SPLIT][index] is not ' ':
                    index -= 1
                index += MSG_SPLIT
                response = self.bookmark[:index] + "..."
                self.bookmark = "..." + self.bookmark[index + 1:]
            else:
                response = self.bookmark
                self.bookmark = ""
        else:
            response = random.choice(voice.no_more)

        return response

    def help(self, *args):
        """displays all help information available

        This is the main help function for commands available in clubot. With
        no arguments, it returns a list of commands. If a specific command is
        given as an argument, it will return a more detailed explanation of the
        command and parameters that it requires.

        """

        response = ''

        if not args:
            return response
        args = args[0]

        if args and args not in self.cmdlist:
            response = random.choice(voice.bad_cmd)
        else:
            response = voice.help[args]
        return response

    def source(self, *args):
        """returns a link to the clubot repo on github"""
        return 'https://github.com/dzhurley/clubot | see #botgrounds'

    def todo(self, *args):
        """keeps track of todo items, gives list when args is 'show'"""
        response = ""

        if args and not args[0]:
            return random.choice(voice.missing_arg)
        args = args[0]

        f = open("./todo.txt", "a+")
        if args == "show":
            lines = f.readlines()
            lines = [l[:-1] for l in lines]
            response = "current todo's: " + ", ".join(lines)
        else:
            f.write(args + "\n")
            response = "new todo: " + "'" + args + "'"
        f.close()

        return response

    def dispatch(self, user, msg):
        """calls the command function in the msg

        This is called from client.py in privmsg to process commands. If clubot
        is addressed directly, a response is returned to check clubot's help.

        The command function is then dispatched with a globals() call with the
        args given. By implementing each command function with *args, the
        actual dispatch of the function is done in one line, which is nice.

        """

        reply = None

        if msg[0] == '!':
            msg = msg[1:]
            cmd = msg.rsplit()[0]
            args = ' '.join(msg.rsplit()[1:])

            if cmd not in self.cmdlist:
                reply = user + ", " + random.choice(voice.bad_cmd)
            else:
                reply = getattr(self, cmd)(args)
        elif 'clubot++' in msg:
            if user == 'd-_-b':
                user = '(' + user + ')'
            reply = user + random.choice(voice.karma_up)
        elif 'clubot--' in msg:
            if user == 'd-_-b':
                user = '(' + user + ')'
            reply = user + random.choice(voice.karma_down)
        elif re.match(r'clubot[ ,:]', msg):
            reply = user + random.choice(voice.addressed)
        else:
            reply = ''

        return reply
