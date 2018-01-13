'''
Created on Jan 13, 2018

@author: meisl
'''

import re
import pyaudio
import os

from cfg import cfg
from system.utils import twitchConnect
import wave

CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

twitchSocket = twitchConnect()
p = pyaudio.PyAudio()
run = True

for i in range(p.get_device_count()):
    print (p.get_device_info_by_index(i))

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
            elif command == 'stopbot' and username in cfg.allowedOperators:
                run = False
            elif run:
                if command in cfg.commands:
                    try:
                        wf = wave.open(os.environ['HOMEPATH'] + '\\Desktop\ChatDrums\\' + command + '.wav', 'rb')
                        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                        channels=wf.getnchannels(),
                                        rate=wf.getframerate(),
                                        output=True,
                                        input_device_index=1)
                        data = wf.readframes(cfg.CHUNK)
                        while len(data) > 0:
                            stream.write(data)
                            data = wf.readframes(cfg.CHUNK)
                        stream.stop_stream()
                        stream.close()
                    except FileNotFoundError:
                        pass