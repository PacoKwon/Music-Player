import curses
import glob
import json
import os
import time
from urllib.parse import urlparse
import vlc

options = ["q:", "h:", "l:", u"\u2b98:", u"\u2b9a:"]
actions = ["quit", "previous song", "next song", "-5s", "+5s"]
options_index = [0]
actions_index = [3]


# load a list of songs
def load_list():
    global playlist

    with open("config.json") as f:
        data = json.load(f)

    storage = data["directory"]

    playlist = glob.glob("{}/**/*.mp3".format(storage), recursive=True)

    for i in range(1, len(actions)):
        options_index.append(2 + options_index[i - 1] + len(options[i - 1]) + len(actions[i - 1]))
        actions_index.append(2 + actions_index[i - 1] + len(actions[i - 1]) + len(options[i - 1]))


# extract title from file url
def get_song_title(url):
    return os.path.basename(urlparse(url).path)[:-4]


# convert an integer milisecond time to formatted time like 0:57
def formatted_time(ms: int):
    if ms == -1:
        return " "

    ms //= 1000
    m = str(ms // 60)
    s = str(ms % 60).rjust(2, '0')
    return "{}:{}".format(m, s)


def turn_on(stdscr, num):
    stdscr.attron(curses.color_pair(num))


def turn_off(stdscr, num):
    stdscr.attroff(curses.color_pair(num))


def paco_player(stdscr):
    global player

    load_list()

    # input key
    key = 0
    # variable to store number of songs played
    song_count = 0
    # is this song currently paused?
    paused = False
    # variable to store pause time
    paused_time = 0
    # is current song newly started?
    new_song = False

    stdscr.nodelay(True)

    stdscr.clear()
    stdscr.refresh()

    # initialize colors
    curses.start_color()

    # initialize gray color.
    # id -> 0
    curses.init_color(0, 70, 70, 70)

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, 0)

    # stdscr.attron(curses.color_pair(3))

    player = vlc.MediaPlayer(playlist[song_count])
    player.play()

    # loop until 'q' is pressed
    while key != ord('q'):
        stdscr.clear()
        height, width = stdscr.getmaxyx()  # get width & height

        # decrement song_count
        if key == ord('h'):
            song_count = song_count - 1 if song_count > 0 else 0
            new_song = True
            player.stop()
        # increment song_count
        elif key == ord('l'):
            song_count = song_count + 1 if song_count < len(playlist) - 1 \
                                        else 0
            new_song = True
            player.stop()
        # pause
        elif key == ord(' '):
            # player.pause()
            # stop if playing, play if paused
            if not paused:
                # get paused time when pausing
                paused_time = player.get_time()
                player.stop()
            else:
                player.play()

                if new_song:
                    # for a new song -> no ending lag
                    # so no extra miliseconds
                    player.set_time(paused_time)
                    new_song = False
                else:
                    # there is an ending lag when stopping,
                    # so just adding some miliseconds
                    # 250ms is a fine-tuned constant. so don't change!
                    player.set_time(paused_time + 250)

            # reverse paused variable
            paused = not paused

        # move 5s backwards only if song is played more than 5s
        elif key == curses.KEY_LEFT:
            if player.get_time() >= 5000:
                player.set_time(player.get_time() - 5000)

        # move 5s forwards only if song is left more than 5s
        elif key == curses.KEY_RIGHT:
            if player.get_time() + 5000 <= player.get_length():
                player.set_time(player.get_time() + 5000)

        # play again only when previous or next song is selected
        if key == ord('h') or key == ord('l'):
            player = vlc.MediaPlayer(playlist[song_count])
            player.play()

        # extract song name from url
        song_name = get_song_title(playlist[song_count])

        stdscr.attron(curses.color_pair(1))

        for opt, index in zip(options, options_index):
            stdscr.addstr(height - 2, index, opt)
        # stdscr.addstr(height - 2, 0, "q:")
        # stdscr.addstr(height - 2, 8, "h:")
        # stdscr.addstr(height - 2, 25, "l:")
        # stdscr.addstr(height - 2, 38, u"\u2b98:")  # left arrow unicode
        # stdscr.addstr(height - 2, 45, u"\u2b9a:")  # right arrow unicode

        stdscr.attroff(curses.color_pair(1))

        stdscr.addstr(height - 2, 3, "quit")
        stdscr.addstr(height - 2, 11, "previous song")
        stdscr.addstr(height - 2, 28, "next song")
        stdscr.addstr(height - 2, 41, "-5s")
        stdscr.addstr(height - 2, 48, "+5s")

        # calculate song title position
        title_x = (width // 2) - (len(song_name) // 2)
        title_y = height // 2

        # render song name
        stdscr.attron(curses.color_pair(2))         # add attributes
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(title_y, title_x, song_name)  # add title
        stdscr.attroff(curses.color_pair(2))        # reset
        stdscr.attroff(curses.A_BOLD)

        """

        0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
        q: quit h: previous song l: next song -: +5s -: -5s

        """

        # while loop until key input, and keep updating
        key = stdscr.getch()
        while key == -1:
            # set status bar message
            status = "Paco's Music Player | STATUS BAR | {} / {} | {} / {}"\
                .format(
                    song_count + 1,
                    len(playlist),
                    formatted_time(player.get_time()),
                    formatted_time(player.get_length())
                )

            # render status bar
            stdscr.attron(curses.color_pair(1))     # attribute on
            stdscr.addstr(height-1, 0, status)      # add string
            stdscr.addstr(height-1, len(status), " " * (width - len(status)-1))
            stdscr.attroff(curses.color_pair(1))    # attribute off

            key = stdscr.getch()

            # for a split second when the song is starting, player is not
            # recognized as playing. so when time is above 0 -> press l
            if not player.is_playing() and player.get_time() > 0:
                key = ord('l')
    # stdscr.attroff(curses.color_pair(3))


def main():
    if os.path.ismount('/mnt/WindowsDrive/'):
        curses.wrapper(paco_player)
    else:
        print("Music Driver not mounted.\nTerminating...")

# playlist = [
#     '/mnt/WindowsDrive/Users/haech/Music/
#   Speak Now (Deluxe Edition)/Haunted (Acoustic Version).mp3',
#     '/mnt/WindowsDrive/Users/haech/Music/
#   Coldplay - A Rush Of Blood To The Head 2002/Coldplay - 07 - Green Eyes.mp3'
#     '/mnt/WindowsDrive/Users/haech/Music/
#   Coldplay-X&Y Live 2005/10-coldplay-what if.mp3',
#     "/mnt/WindowsDrive/Users/haech/Music/
#   2013 - Yours Truly (Deluxe Edition)/05. Lovin' It.mp3",
#     '/mnt/WindowsDrive/Users/haech/Music/
#   2013 - Yours Truly (Deluxe Edition)/06. Piano.mp3',
#     '/mnt/WindowsDrive/Users/haech/Music/
#   Speak Now (Deluxe Edition)/Enchanted.mp3'
# ]

if __name__ == "__main__":
    main()
    # load_list()
    # for act, index in zip(actions, actions_index):
    #     print(act, end=': ')
    #     print(index)
