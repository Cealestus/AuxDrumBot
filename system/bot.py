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
runBot = True
runBotLock = threading.Lock()
requestQueue = queue.Queue()

def playAudio(sound):
    try:
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
        chat(twitchSocket, 'Error: File not found')
    

def playFromQueue():
    while True:
        if requestQueue.qsize() != 0:
            soundName = requestQueue.get(block=True)
            newThread = threading.Thread(target=playAudio(sound=soundName))
            newThread.daemon = True
            newThread.start()

def requestFromChat():
    global runBot
    print("Starting thread")
    while True:
        response = twitchSocket.recv(1024).decode("utf-8")
        print(str(response))
        if response == "PING :tmi.twitch.tv\r\n":
            twitchSocket.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            username = re.search(r"\w+", response).group(0)
            message = CHAT_MSG.sub("", response)
            print(message)
            lowerCase = message.lower()
            splitMessage = lowerCase.split()
            if len(splitMessage) == 1:
                with runBotLock:
                    command = splitMessage[0]
                    if command == 'startbot' and username in cfg.allowedOperators:
                        runBot = True
                        chat(twitchSocket, 'Chat drums enabled MAKE SOME NOISE!')
                    elif command == 'stopbot' and username in cfg.allowedOperators:
                        runBot = False
                        chat(twitchSocket, '"Chat drums have been put away, they will be back soon')
                    elif runBot:
                        if command in cfg.commands:
                            requestQueue.put(command)


requestThread = threading.Thread(target=requestFromChat)
requestThread.daemon = True
requestThread.start()

playThread = threading.Thread(target=playFromQueue)
playThread.daemon = True
playThread.start()


chat(twitchSocket, 'Started drumbot')
                        
