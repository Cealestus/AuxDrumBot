'''
Created on Jan 13, 2018

@author: meisl
'''
import socket

import cfg

def twitchConnect():
    """
    Creates a socket connection to the twitch channel defined in cfg. returns the socket
    s -- The socket connecting to twitch. Needs to be closed after done using
    """
    s = socket.socket()
    s.connect((cfg.HOST, cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode('utf-8'))
    s.send("NICK {}\r\n".format(cfg.NICK).encode('utf-8'))
    s.send("JOIN {}\r\n".format(cfg.CHAN).encode('utf-8'))
    
    return s