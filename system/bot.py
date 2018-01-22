'''
Created on Jan 13, 2018

@author: meisl
'''

import os
import queue
import re
import threading
import wave

import pyaudio

import cfg
from utils import twitchConnect, chat


CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

twitchSocket = twitchConnect()
p = pyaudio.PyAudio()
run = True
requestQueue = queue.Queue()

def playFromQueue():
    while True:
        if requestQueue.qsize() != 0:
            try:
                sound = requestQueue.get()
                wf = wave.open(os.environ['HOMEPATH'] + '\\Desktop\ChatDrums\\' + sound + '.wav', 'rb')
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                channels=wf.getnchannels(),
                                rate=wf.getframerate(),
                                output=True)
                data = wf.readframes(cfg.CHUNK)
                while len(data) > 0:
                    stream.write(data)
                    data = wf.readframes(cfg.CHUNK)
                    stream.stop_stream()
                    stream.close()
            except FileNotFoundError:
                pass

def requestFromChat():
    while True:
        response = twitchSocket.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            twitchSocket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            lowerCase = message.lower()
            splitMessage = lowerCase.split()
            if len(splitMessage) == 1:
                command = splitMessage[0]
            if command == 'startbot' and username in cfg.allowedOperators:
                run = True
                chat(twitchSocket, 'Started drumbot by user command')
            elif command == 'stopbot' and username in cfg.allowedOperators:
                run = False
                chat(twitchSocket, 'Stopped drumbot by user command')
            elif run:
                if command in cfg.commands:
                    requestQueue.put(command)

requestThread = threading.Thread(target=requestFromChat)
requestThread.daemon = True
requestThread.start()

playThread = threading.Thread(target=playFromQueue)
playThread.daemon = True
playThread.start()

chat(twitchSocket, 'Started drumbot')
                        