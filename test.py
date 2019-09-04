#!/usr/bin/env python

from __future__ import print_function

import getpass
import re
import random
import sys, termios, tty, os, time
import keyboard
from optparse import OptionParser

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.compat import input
from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias
)

from world import World
from bot import Bot

import packets.serverbound.play as my_svbnd_play


# address = '25.100.105.39\0FML\0'
address = '25.100.105.39'
port = 25565

button_delay = 0.1


def main():
    username = 'test_bot5'
    # connection = Connection(address, port, username='bot{:04d}'.format(random.randint(0, 1000)))
    connection = Connection(address, port, username=username)
    bot = Bot(connection, username)
    
    def print_outgoing(packet):
        if type(packet) is not my_svbnd_play.DiggingPacket:
            print('<-- %s' % packet, file=sys.stderr)

    connection.register_packet_listener(
        bot.process_packet, Packet)
    connection.register_packet_listener(
        print_outgoing, Packet, outgoing=True)

    def handle_join_game(join_game_packet, early=True):
        print('Connected.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)

    connection.connect()    

    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            a = input()
        except Exception as e:
            # print(e)
            pass  #

    

    # while True:
    #     try:
    #         text = input()
    #         if text == "/respawn":
    #             print("respawning...")
    #             packet = serverbound.play.ClientStatusPacket()
    #             packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
    #             connection.write_packet(packet)
    #         elif text.startswith('/move'):
    #             packet = serverbound.play.PositionAndLookPacket()
                
    #             l = text.split()
                
    #             packet.x = int(l[1])
    #             packet.feet_y = int(l[2])
    #             packet.z = int(l[3])
    #             packet.yaw = 100
    #             packet.pitch = 100
    #             packet.on_ground = True
    #             connection.write_packet(packet)
    #             packet = serverbound.play.TeleportConfirmPacket()
    #             packet.teleport_id = 2
    #             connection.write_packet(packet)

    #         else:
    #             packet = serverbound.play.ChatPacket()
    #             packet.message = text
    #             connection.write_packet(packet)
    #     except KeyboardInterrupt:
    #         print("Bye!")
    #         sys.exit()


if __name__ == "__main__":
    main()
