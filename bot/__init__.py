from bot.threads.path_finding_algorithms import StraightForwardAlgorithm, AStarAlgorithm
from bot.threads import MovingThread, FallingThread, MiningThread, MultiMiningThread

import random
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.networking.packets.clientbound.play import PlayerPositionAndLookPacket, JoinGamePacket, SetSlotPacket
from minecraft.networking.types import (
    Position
)

from packets.serverbound.play import DiggingPacket
from world import World
from .inventory import Inventory

import json, time, sys, os
import math

from threading import Thread, Lock, Event
import traceback

from pathlib import Path


class Bot():

    MINING_RADIUS = 5

    def __init__(self, connection):
        with open(os.path.join(str(Path(__file__).absolute().parent), 'block_info.txt'), 'r') as f:
            text = f.read()
            block_info = json.loads(text)
            self.world = World(block_info)
        self.connection = connection
        self.position = [0, 0, 0]
        self.rotation = [0, 0]
        self.lock = Lock()
        self.break_event = Event()
        self.break_event_multi = Event()
        self.dimension = 0
        self.loaded = False
        self.chat_level = 0
        self.inventory = Inventory()
        

    def say(self, message, level=0):
        if level >= self.chat_level:
            packet = serverbound.play.ChatPacket()
            packet.message = message
            self.connection.write_packet(packet)
    
    def update_position(self, new_pos, new_rot=None):
        self.position = new_pos
        if new_rot is not None:
            self.rotation = new_rot
        packet = serverbound.play.PositionAndLookPacket()
        packet.x = self.position[0]
        packet.feet_y = self.position[1]
        packet.z = self.position[2]
        packet.yaw = self.rotation[0]
        packet.pitch = self.rotation[1]
        packet.on_ground = True
        self.connection.write_packet(packet)


    def process_packet(self, packet):
        if type(packet) is clientbound.play.player_position_and_look_packet.PlayerPositionAndLookPacket:
            if not self.loaded:
                self.loaded = True
                self.say('Finished loading')

            self.position[0] = packet.x
            self.position[1] = packet.y
            self.position[2] = packet.z

            self.rotation[0] = packet.yaw
            self.rotation[1] = packet.pitch

            print("--> {}".format(packet))
        
        elif type(packet) is clientbound.play.chunk_data_packet.ChunkDataPacket:
            packet.chunk.read_data(packet.data, self.dimension)
            self.world.chunks.append(packet.chunk)

        elif type(packet) is clientbound.play.block_change_packet.BlockChangePacket:
            
            # print(packet)
            self.world.update_block(*packet.location, packet.blockId, relative=False)

        elif type(packet) is clientbound.play.block_change_packet.MultiBlockChangePacket:
            print(packet)
            self.world.update_block_multi(packet.chunk_x, packet.chunk_z, packet.records)
        
        elif type(packet) is clientbound.play.ChatMessagePacket:
            # print(packet)
            self.process_chat_packet(packet)

        elif type(packet) is JoinGamePacket:
            self.dimension = packet.dimension

        elif type(packet) is SetSlotPacket:
            self.inventory[packet.slot] = packet.slot_data
            print(self.inventory[packet.slot])

        if type(packet) is Packet:
            # This is a direct instance of the base Packet type, meaning
            # that it is a packet of unknown type, so we do not print it.
            return
    def process_chat_packet(self, packet):
        
        json_data = json.loads(packet.json_data)
        if len(json_data['with']) == 2 and type(json_data['with'][1]) is str:
            message = json_data['with'][1].split()    
            if message[0] == '!bot':
                try:
                    if message[1] == 'goto':
                        self.break_event.clear()
                        args = {'start' : [math.floor(x) for x in self.position], 'end' : [int(x) for x in message[2:5]]}
                        for additional_arg in message[5:]:
                                key, value = additional_arg.split('=')
                                if key == 'step_length' or key == 'radius':
                                    args[key] = float(value)
                                else:
                                    args[key] = int(value)
                        if (self.world.get_block(*args['end']) in self.world.block_info['blocks']['passable'] 
                            and self.world.get_block(args['end'][0], args['end'][1] + 1, args['end'][2]) 
                                in self.world.block_info['blocks']['passable']
                                    and self.world.get_block(args['end'][0], args['end'][1] - 1, args['end'][2])
                                        not in self.world.block_info['blocks']['passable']) or 'radius' in args.keys() and args['radius'] > 1:
                            alg = AStarAlgorithm(self.world)
                            
                            thread = MovingThread('moving', self, alg.find_path, args)
                            thread.start()
                        else:
                            self.say('Target is not passable or block under is passable', 2)

                    elif message[1] == 'mine':
                        self.break_event.clear()
                        args = {'start' : [math.floor(x) for x in self.position], 'end' : [int(x) for x in message[2:5]]}
                        for additional_arg in message[5:]:
                            key, value = additional_arg.split('=')
                            if key == 'step_length' or key == 'radius':
                                args[key] = float(value)
                            else:
                                args[key] = int(value)
                        
                        if (self.world.get_block(*args['end']) > 0):
                            alg = AStarAlgorithm(self.world)
                            thread = MiningThread('mining', self, alg.find_path, args)
                            thread.start()
                        else:
                            self.say('Block is air')
                    elif message[1] == 'c_level':
                        self.chat_level = int(message[2])
                        self.say('Chat level is now {}'.format(self.chat_level), 3)

                    elif message[1] == 'mineall':
                        self.break_event.clear()
                        self.break_event_multi.clear()
                        block = int(message[2])
                        args = {}

                        for additional_arg in message[3:]:
                            key, value = additional_arg.split('=')
                            if key == 'step_length' or key == 'radius':
                                args[key] = float(value)
                            else:
                                args[key] = int(value)

                        blocks = []

                        chunk_x, chunk_z = self.world.get_chunk_coords(math.floor(self.position[0]), math.floor(self.position[2]))
                        chunk = self.world.get_chunk_by_chunk_coords(chunk_x, chunk_z)
                        self.say('Searching {} for {}'.format((chunk_x, chunk_z), block))

                        for x in range(16):
                            for y in range(256):
                                for z in range(16):
                                    if chunk.get_block(x, y, z, True) == block:
                                        blocks.append([x + chunk_x*16, y, z + chunk_z*16])
                        
                        self.say('Found {} blocks'.format(len(blocks)))

                        alg = AStarAlgorithm(self.world)
                        thread = MultiMiningThread('multimining', self, alg.find_path, blocks, args)
                        thread.start()

                    elif message[1] == 'break':
                        self.break_event.set()
                        self.break_event_multi.set()

                    else:
                        self.say("I don't get it", 1)

                except Exception as e:
                    self.say("Something's wrong. Check console", 3)
                    traceback.print_exc()
        else:
            print(len(json_data['with']))
            print(json_data['with'])
                    

                

        # if message.startswith('!bot'):
        #     command = message[5:]
        #     if command.startswith('mine'):
        #         target = [int(x) for x in command[5:].split()]
        #         self.mining_thread = Bot.MiningThread('mining', target, self)
        #         self.mining_thread.start()
        #     elif command.startswith('tp'):
        #         coords = [int(x) for x in command[3:].split()]
        #         self.pos['x'] = coords[0]
        #         self.pos['feet_y'] = coords[1]
        #         self.pos['z'] = coords[2]
        #         self.pos['changed'] = True
        #         self.update_pos()
        #     elif command.startswith('mvto'):
        #         coords = [int(x) for x in command[5:].split()]
        #         self.moving_thread = Bot.MovingThread('moving', coords, self)
        #         self.moving_thread.start()
        #     elif command.startswith('query'):
        #         target = [int(x) for x in command[6:].split()]
        #         packet = serverbound.play.ChatPacket()
        #         packet.message = str(self.world.get_block(*target))
        #         self.connection.write_packet(packet)
        #     elif command.startswith('check'):
        #         target = [int(x) for x in command[6:].split()]
        #         chunck_c = self.world.get_chunk_coords(target[0], target[2])
        #         chunck = self.world.get_chunk_by_chunk_coords(*chunck_c)

        #         for x in range(16):
        #                 for z in range(16):
        #                     for y in range(16):
        #                         if chunck.sections[0].blocks[x][y][z] > 0:
        #                             print("{} {}".format((x, y, z), chunck.sections[0].blocks[x][y][z]))

        #     elif command.startswith('find'):
        #         target = int(command[5:])
    
        #         print(self.world.find_chunks_with_block(target))
