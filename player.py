import curses
import glob
import json
import os
from random import shuffle
import time
from urllib.parse import urlparse
import vlc

# list of options and actions
options = ["q:", "h:", "l:", u"\u2b98:", u"\u2b9a:", "s:"]
actions = ["quit", "previous song", "next song", "-5s", "+5s", "shuffle"]

# list of index numbers that each options and actions
# should be placed in the status bar
options_index = [0]
actions_index = [3]


# load a list of songs
def load_list():
    global playlist

    with open("config.json") as f:
        data = json.load(f)

    storage = data["root"]

    # get all file paths that ends with mp3
    playlist = glob.glob("{}/**/*.mp3".format(storage), recursive=True)

    # calculate starting indexes for all options and actions
    # using dynamic programming
    for i in range(1, len(actions)):
        options_index.append(2 + options_index[i - 1] + len(options[i - 1]) + len(actions[i - 1]))
        actions_index.append(2 + actions_index[i - 1] + len(actions[i - 1]) + len(options[i - 1]))

    # DEBUGGING
    f = open("list.txt", "w+")
    for e in playlist:
        f.write(get_song_title(e) + "\n")
    f.close()


# extract title from file url
def get_song_title(url):
    return os.path.basename(urlparse(url).path)[:-4]


# convert an integer milisecond time to formatted time
# ex> convert 117 -> 1:57
def formatted_time(ms: int):
    if ms == -1:
        return " "

    ms //= 1000
    m = str(ms // 60)
    s = str(ms % 60).rjust(2, '0')
    return "{}:{}".format(m, s)


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

    # current song length
    cur_song_length = 0

    shuffle_waiting = False

    # remove delay, to display song time
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
                cur_song_length = player.get_length()
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

        elif key == ord('s'):
            pass
            tmp = playlist[song_count]
            playlist.remove(tmp)
            shuffle(playlist)
            playlist.insert(0, tmp)
            song_count = 0
            # shuffle(playlist)

        # play again only when previous or next song is selected
        if key == ord('h') or key == ord('l'):
            paused = False
            player = vlc.MediaPlayer(playlist[song_count])
            player.play()
            cur_song_length = player.get_length()

        # extract song name from url
        song_name = get_song_title(playlist[song_count])

        stdscr.attron(curses.color_pair(1))

        # place options in their respective places but not
        # add them if their index is larger than terminal width
        for opt, index in zip(options, options_index):
            if index + len(opt) < width:
                stdscr.addstr(height - 2, index, opt)
        stdscr.attroff(curses.color_pair(1))

        # place actions in their respective places but not
        # add them if their index is larger than terminal width
        for act, index in zip(actions, actions_index):
            if index + len(act) < width:
                stdscr.addstr(height - 2, index, act)

        # calculate song title position
        if width >= len(song_name):
            title_x = (width // 2) - (len(song_name) // 2)
        else:
            title_x = 0  # if song name larger than width, x -> 0
        title_y = height // 2

        # render song name
        stdscr.attron(curses.color_pair(2))  # add attributes
        stdscr.attron(curses.A_BOLD)

        stdscr.addstr(title_y, title_x, song_name[:width - 1])  # add title

        # if song name length exceeds width of terminal, wrap it to next line
        if width < len(song_name):
            stdscr.addstr(title_y + 1, 0, song_name[width-1:])

        stdscr.attroff(curses.A_BOLD)  # reset
        stdscr.attroff(curses.color_pair(2))

        """

        0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
        q: quit h: previous song l: next song -: +5s -: -5s

        """

        # while loop until key input, and keep updating
        key = stdscr.getch()
        while key == -1:
            status_time = player.get_time() if not paused else paused_time
            status_len = player.get_length() if not paused else cur_song_length

            # set status bar message
            status = "Paco's Music Player | STATUS BAR | {} / {} | {} / {}  | {}"\
                .format(
                    song_count + 1,
                    len(playlist),
                    formatted_time(status_time),
                    formatted_time(status_len),
                    player.get_state(),
                )

            # render status bar
            stdscr.attron(curses.color_pair(1))     # attribute on
            """
            string index slicing is used to not add
            characters exceeding the width of terminal
            """
            stdscr.addstr(height-1, 0, status[:(width-1)])
            if len(status) < width:
                stdscr.addstr(height-1, len(status), " " * (width - len(status)-1))
            stdscr.attroff(curses.color_pair(1))    # attribute off

            key = stdscr.getch()

            # for a split second when the song is starting, player is not
            # recognized as playing. so when time is above 0 -> press l
            if player.get_state() == vlc.State.Ended:
                key = ord('l')


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
