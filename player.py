import pygame
from pygame import mixer
import glob
import json
from pprint import pprint


def load_list():
    global song_list

    with open("config.json") as f:
        data = json.load(f)

    storage = data["directory"]

    song_list = glob.glob("{}/**/*.mp3".format(storage), recursive=True)
    print(song_list)


playlist = [
    '/run/media/paco/680E7F690E7F2F66/Users/haech/Music/Speak Now (Deluxe Edition)/Haunted (Acoustic Version).mp3',
    '/run/media/paco/680E7F690E7F2F66/Users/haech/Music/Coldplay - A Rush Of Blood To The Head 2002/Coldplay - 07 - Green Eyes.mp3',
    '/run/media/paco/680E7F690E7F2F66/Users/haech/Music/Tori Kelly - Suit & Tie (Acoustic Cover)/suit & tie (acoustic cover) - tori kelly.mp3',
    '/run/media/paco/680E7F690E7F2F66/Users/haech/Music/Coldplay-X&Y Live 2005/10-coldplay-what if.mp3',
    "/run/media/paco/680E7F690E7F2F66/Users/haech/Music/2013 - Yours Truly (Deluxe Edition)/05. Lovin' It.mp3",
    '/run/media/paco/680E7F690E7F2F66/Users/haech/Music/2013 - Yours Truly (Deluxe Edition)/06. Piano.mp3',
    '/run/media/paco/680E7F690E7F2F66/Users/haech/Music/Speak Now (Deluxe Edition)/Enchanted.mp3'
]

if __name__ == "__main__":
    load_list()

    
    # END_EVENT = pygame.USEREVENT + 1

    # pygame.init()
    # mixer.init()

    # pygame.mixer.music.set_endevent(END_EVENT)


    # mixer.music.load(playlist[0])
    # mixer.music.play(loops=1)

