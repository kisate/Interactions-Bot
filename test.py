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


import packets.serverbound.play as mplay


address = '25.100.105.39'
port = 25565
name = 'bot{:04d}'.format(random.randint(0, 1000))

pos = {'x' : 0, 'feet_y' : 0, 'z' : 0, 'yaw' : 0, 'pitch' : 0, 'on_ground' : False, 'changed' : False}


def update_pos(connection):

    packet = serverbound.play.PositionAndLookPacket()

    for key in pos.keys():
        if key != 'changed':
            setattr(packet, key, pos[key])
    
    connection.write_packet(packet)
    packet = serverbound.play.TeleportConfirmPacket()
    packet.teleport_id = 2
    connection.write_packet(packet)

    pos['changed'] = False

button_delay = 0.1


def main():
    global pos

    connection = Connection(address, port, username=name)
    def print_incoming(packet):
        
        if type(packet) is clientbound.play.player_position_and_look_packet.PlayerPositionAndLookPacket:
            for key in pos.keys():
                if (key == 'feet_y'):
                    pos[key] = getattr(packet, 'y')
                elif (key != 'changed' and key != 'on_ground'):
                    pos[key] = getattr(packet, key)
                
            print(pos)
        
        # else:
            # This is a direct instance of the base Packet type, meaning
            # that it is a packet of unknown type, so we do not print it.
            # return
        print('--> %s' % packet, file=sys.stderr)

    def print_outgoing(packet):
        print('<-- %s' % packet, file=sys.stderr)

    connection.register_packet_listener(
        print_incoming, Packet, early=True)
    connection.register_packet_listener(
        print_outgoing, Packet, outgoing=True)

    def handle_join_game(join_game_packet):
        print('Connected.')

    connection.register_packet_listener(
        handle_join_game, clientbound.play.JoinGamePacket)

    def print_chat(chat_packet):
        print("Message (%s): %s" % (
            chat_packet.field_string('position'), chat_packet.json_data))

    connection.register_packet_listener(
        print_chat, clientbound.play.ChatMessagePacket)

    connection.connect()    

    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('a'):  # if key 'q' is pressed 
                print("Left pressed")
                pos['x'] += 0.1
                pos['changed'] = True
                update_pos(connection)
                time.sleep(button_delay)
              # finishing the loop
            elif keyboard.is_pressed('d'):
                print("Right pressed")
                pos['x'] -= 0.1
                pos['changed'] = True
                update_pos(connection)
                time.sleep(button_delay)
            elif keyboard.is_pressed('w'):
                print("Up pressed")
                pos['z'] += 0.1
                pos['changed'] = True
                update_pos(connection)
                time.sleep(button_delay)
            elif keyboard.is_pressed('s'):
                print("Down pressed")
                pos['z'] -= 0.1
                pos['changed'] = True
                update_pos(connection)
                time.sleep(button_delay)
            elif keyboard.is_pressed('r'):
                print('Respawning...')
                packet = serverbound.play.ClientStatusPacket()
                packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                connection.write_packet(packet)
                time.sleep(button_delay)
            elif keyboard.is_pressed('t'):
                print('Enter msg:')
                text = input()
                packet = serverbound.play.ChatPacket()
                packet.message = text
                connection.write_packet(packet)
                time.sleep(button_delay)
            elif keyboard.is_pressed('space'):
                print("Space pressed")
                pos['feet_y'] += 0.1
                pos['changed'] = True
                update_pos(connection)
                time.sleep(button_delay)
            elif keyboard.is_pressed('shift'):
                print("Shift pressed")
                pos['feet_y'] -= 0.1
                pos['changed'] = True
                update_pos(connection)
                time.sleep(button_delay)
            elif keyboard.is_pressed('x'):
                print('digging')
                packet = mplay.DiggingPacket()
                packet.location = Position(x=int(pos['x']), y=int(pos['feet_y']) - 1, z=int(pos['z']))
                packet.status = 0
                packet.face = 1
                connection.write_packet(packet)
                packet = mplay.DiggingPacket()
                time.sleep(1)
                packet.location = Position(x=int(pos['x']), y=int(pos['feet_y']) - 1, z=int(pos['z']))
                packet.status = 2
                packet.face = 1
                connection.write_packet(packet)
                time.sleep(button_delay)
                
                
                
            elif keyboard.is_pressed('q'):
                break

            else:
                pass
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
