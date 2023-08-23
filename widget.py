import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import threading
# from ttkthemes import themed_tk as tk

import imageio
# from scipy import ndimage, spatial
from PIL import Image, ImageDraw
import PIL as pillow
import requests
from io import BytesIO
import numpy as np
from colorthief import ColorThief

import time


username = ""
scope = 'user-read-private user-read-playback-state user-modify-playback-state'
clientID = ''
clientSecret = ''
redirectURI = 'https://www.google.com/'

try:
    token = util.prompt_for_user_token(username, scope, clientID, clientSecret, redirectURI)
except (AttributeError, JSONDecodeError):
    # os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, clientID, clientSecret, redirectURI)


spotifyObj = spotipy.Spotify(auth = token)
devices = spotifyObj.devices()
# print(json.dumps(devices, sort_keys = True, indent = 4))
deviceID = devices['devices'][0]['id']




user = spotifyObj.current_user()
displayName = user['display_name']

root = tk.Tk()
# root.get_themes()
# root.set_theme('vista')

# root.geometry('300x400')
root.resizable(False, False)
root.title('Amy\'s Spotify Widget')
root.configure(background="white")

menubar = Menu(root)
root.config(menu=menubar)






# Front end

topFrame = Frame(root, background='white')
topFrame.pack(side=TOP, padx=24)

middleFrame = Frame(root, background='white')
middleFrame.pack(side=TOP, padx=24)

bottomFrame = Frame(root, background='white')
bottomFrame.pack(side=TOP, padx=24)

creditbar = Label(root, text="Icons made by Darius Dan from www.flaticon.com", font=("Lexend Deca", 11), background='white')
creditbar.pack(side=BOTTOM, fill=X)

class Labels():

    def __init__(self, parent):

        self.user_label = Label(topFrame, text="Welcome\n" + displayName, font=("Lexend Deca", 20), background='white')
        self.user_label.pack(pady=5)

        self.song_label = Label(middleFrame, text='Name', font=("Lexend Deca", 18), background='white')
        self.song_label.pack()

        self.artist_label = Label(middleFrame, text='Artist', font=("Lexend Deca", 16), background='white')
        self.artist_label.pack()

        self.album_label = Label(middleFrame, text='Album', font=("Lexend Deca", 16), background='white',wraplength=300, justify="center")
        self.album_label.pack()

        self.previous_image = PhotoImage(file='previous_image.png')
        self.previous_button = Button(bottomFrame, image=self.previous_image, command=self.previousTrack, background='white')
        self.previous_button.grid(row=0, column=0, pady=2)

        self.play_image = PhotoImage(file="play_image.png")
        self.pause_image = PhotoImage(file="pause_image.png")
        self.playPause_button = Button(bottomFrame, image=self.pause_image, command=self.pauseSong, background='white')
        self.playPause_button.grid(row=0, column=1, padx=10, pady=10)

        self.next_image = PhotoImage(file='next_image.png')
        self.next_button = Button(bottomFrame, image=self.next_image, command=self.nextTrack, background='white')
        self.next_button.grid(row=0, column=2, pady=2)

        image = PhotoImage(file="albumArtPhoto.png")
        self.albumArt_label = Label(topFrame, image=image, background='white')
        self.albumArt_label.image = image
        self.albumArt_label.pack(pady=2)


        self.playingNow = False
        self.currentTrackID = 0

        self.song_label.after(10, self.checkForSongChange())

    def rgbToHex(self, rgb):
        return '%02x%02x%02x' % rgb

    def checkForSongChange(self):
        currPlaying = spotifyObj.currently_playing()
        if(currPlaying['item']['id'] != self.currentTrackID):
            self.getSongDetails()

    def getSongDetails(self):
        self.track = spotifyObj.current_user_playing_track()
        self.playingNow = spotifyObj.currently_playing()["is_playing"]
        try:
            self.currentTrackID = self.track['item']['id']
            self.artist = self.track['item']['artists'][0]['name']
            self.album = self.track['item']['album']['name']
            self.albumArt = self.track['item']['album']['images'][0]['url']
            self.track = self.track['item']['name']
            print(spotifyObj.audio_features(self.currentTrackID))

            labelThread = threading.Thread(target=self.updateLabels,
                                           args=(self.track, self.playingNow, self.artist, self.album, self.albumArt))
            labelThread.start()
        except:
            print("no track")


        self.song_label.after(10, self.checkForSongChange())

    def updateLabels(self, songTrack, songPlayingNow, songArtist, songAlbum, songAlbumArt):
        # self.track = spotifyObj.current_user_playing_track()
        # self.playingNow = spotifyObj.currently_playing()["is_playing"]
        # self.currentTrackID = self.track['item']['id']
        # self.artist = self.track['item']['artists'][0]['name']
        # self.album = self.track['item']['album']['name']
        # self.albumArt = self.track['item']['album']['images'][0]['url']
        # self.track = self.track['item']['name']

        if songPlayingNow:
            self.playPause_button['image'] = self.pause_image
        else:
            self.playPause_button['image'] = self.play_image

        response = requests.get(songAlbumArt)
        img = Image.open(BytesIO(response.content))
        img = img.resize((250, 250), Image.ANTIALIAS)
        imageio.imwrite('albumArtPhoto.png', img)
        colour = ColorThief('albumArtPhoto.png')
        colour = colour.get_color(quality=1)
        colour = self.rgbToHex(colour)
        colour = "#" + str(colour)

        # root.configure(background=colour)
        # topFrame.config(background=colour)
        # middleFrame.config(background=colour)
        # bottomFrame.config(background=colour)
        self.user_label.config(foreground=colour)
        # self.albumArt_label.config(background=colour)
        # self.song_label.config(background=colour)
        # self.artist_label.config(background=colour)
        # self.album_label.config(background=colour)
        # self.previous_button.config(background=colour)
        # self.playPause_button.config(background=colour)
        # self.playPause_button.config(foreground=colour)
        # self.next_button.config(background=colour)

        try:
            image = PhotoImage(file='albumArtPhoto.png')
            self.albumArt_label['image'] = image
            self.albumArt_label.image = image
            self.albumArt_label.pack()
        except:
            print("no photo")

        self.song_label['text'] = songTrack
        self.artist_label['text'] = songArtist
        self.album_label['text'] = songAlbum

        self.song_label.after(100, self.getSongDetails())

    

    def pauseSong(self):
        if self.playingNow:
            spotifyObj.pause_playback(deviceID)
            self.playPause_button['image'] = self.play_image
        else:
            spotifyObj.start_playback(deviceID)
            self.playPause_button['image'] = self.pause_image

    def nextTrack(self):
        spotifyObj.next_track(deviceID)
        self.getSongDetails()

    def previousTrack(self):
        spotifyObj.previous_track(deviceID)
        self.getSongDetails()

    def darkMode(self):

        colour = "black"
        textColour = "white"

        root.configure(background=colour)
        topFrame.configure(background=colour)
        middleFrame.configure(background=colour)
        bottomFrame.configure(background=colour)
        creditbar.configure(background=colour)

        self.user_label.config(foreground=textColour)
        self.albumArt_label.config(background=colour)
        self.song_label.config(background=colour)
        self.song_label.config(foreground=textColour)
        self.artist_label.config(background=colour)
        self.artist_label.config(foreground=textColour)
        self.album_label.config(background=colour)
        self.album_label.config(foreground=textColour)
        self.previous_button.config(background=colour)
        self.playPause_button.config(background=colour)
        self.playPause_button.config(foreground=colour)
        self.next_button.config(background=colour)

def on_closing():
    root.destroy()

labels = Labels(root)


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()



