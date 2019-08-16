from bot.threads.path_finding_algorithms import StraightForwardAlgorithm, AStarAlgorithm
from bot.threads import MovingThread, FallingThread

import random
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.networking.packets.clientbound.play import PlayerPositionAndLookPacket, JoinGamePacket
from minecraft.networking.types import (
    Position
)

from packets.serverbound.play import DiggingPacket
from world import World
import json
import sys
import time
import math
from threading import Thread, Lock
class Bot():
    class MiningThread(Thread):
        def __init__(self, name, target_block, bot):
            Thread.__init__(self)
            self.name = name
            self.target_block = target_block
            self.bot = bot

        def get_to_block(self):
            dist = ((self.target_block[0] - self.bot.pos['x'])**2 + (self.target_block[1] - self.bot.pos['feet_y'] - 1.5)**2 + (self.target_block[2] - self.bot.pos['z'])**2)**0.5
            if dist >= 4:
                good_coords = []

                for x in range(self.target_block[0] - 4, self.target_block[0] + 5):
                    for y in range(self.target_block[1], self.target_block[1] + 1):
                        for z in range(self.target_block[2] - 4, self.target_block[2] + 5):
                            if (self.target_block[0] - x)**2 + (self.target_block[1] - y - 1.5)**2 + (self.target_block[2] - z)**2 < 16 and self.bot.world.get_block(x, y, z) == 0 and self.bot.world.get_block(x, y+1, z) == 0 and not (x == self.target_block[0] and y == self.target_block[1] and z == self.target_block[2]):
                                good_coords.append((x, y, z))
                                print((self.target_block[0] - x)**2 + (self.target_block[1] - y - 1.5)**2 + (self.target_block[2] - z)**2)
                
                new_pos = ()

                for coord in good_coords:
                    if (self.bot.world.get_block(*coord) == 0) and (self.bot.world.get_block(coord[0], coord[1] + 1, coord[2]) == 0):
                        new_pos = coord
                        break
                
                if not new_pos:
                    packet = serverbound.play.ChatPacket()
                    packet.message = "No valid blocks nearby"
                    self.bot.connection.write_packet(packet)
                    self.bot.lock.release()
                    return False

                print(new_pos)

                while dist >= 4:
                    r = (new_pos[0] - self.bot.pos['x'], new_pos[1] - self.bot.pos['feet_y'], new_pos[2] - self.bot.pos['z'])
                            
                    delta = [int(a/dist*4) for a in r]
                    print(dist)
                    self.bot.pos['x'] += delta[0]
                    self.bot.pos['feet_y'] += delta[1]
                    self.bot.pos['z'] += delta[2]
                    self.bot.pos['changed'] = True
                
                    self.bot.update_pos()
                    dist =  ((self.bot.pos['x'] - new_pos[0])**2 + (self.bot.pos['feet_y'] - new_pos[1])**2 + (self.bot.pos['z'] - new_pos[2])**2)**0.5
                    time.sleep(0.5)
                
                self.bot.pos['x'] = new_pos[0]
                self.bot.pos['feet_y'] = new_pos[1]
                self.bot.pos['z'] = new_pos[2]
                self.bot.pos['changed'] = True
        
                self.bot.update_pos()
            
            while self.bot.world.get_block(math.trunc(self.bot.pos['x']), math.trunc(self.bot.pos['feet_y']) - 1, math.trunc(self.bot.pos['z'])) == 0:
                self.bot.pos['feet_y'] -= 1
                self.bot.pos['changed'] = True
                print('falling {}'.format(self.bot.pos['feet_y']))
                self.bot.update_pos()
                time.sleep(0.5)

        def run(self):
            self.bot.lock.acquire()
            if self.bot.world.get_block(*self.target_block) == 0:
                packet = serverbound.play.ChatPacket()
                packet.message = "{} is air".format(self.target_block)
                self.bot.connection.write_packet(packet)
                self.bot.lock.release()
                return True
            
            self.get_to_block()
            

            time.sleep(0.1)

            packet = DiggingPacket()
            packet.location = Position(x=self.target_block[0], y=self.target_block[1], z=self.target_block[2])
            packet.status = 0
            packet.face = 1
            self.bot.connection.write_packet(packet)
            
            while self.bot.world.get_block(*self.target_block) != 0:

                dist = ((self.target_block[0] - self.bot.pos['x'])**2 + (self.target_block[1] - self.bot.pos['feet_y'] - 1.5)**2 + (self.target_block[2] - self.bot.pos['z'])**2)**0.5
                if dist >= 4:
                    self.get_to_block()
                packet = DiggingPacket()
                packet.location = Position(x=self.target_block[0], y=self.target_block[1], z=self.target_block[2])
                packet.status = 2
                packet.face = 1
                self.bot.connection.write_packet(packet)
                
                time.sleep(0.1)
            
            self.bot.lock.release()
            return True

    def __init__(self, connection):
        self.world = World()
        self.connection = connection
        self.position = [0, 0, 0]
        self.rotation = [0, 0]
        self.lock = Lock()
        self.dimension = 0
    
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
            self.world.update_block(*packet.location, packet.blockId)

        elif type(packet) is clientbound.play.block_change_packet.MultiBlockChangePacket:
            print(packet)
            self.world.update_block_multi(packet.chunk_x, packet.chunk_z, packet.records)
        
        elif type(packet) is clientbound.play.ChatMessagePacket:
            # print(packet)
            self.process_chat_packet(packet)

        elif type(packet) is JoinGamePacket:
            self.dimension = packet.dimension

        if type(packet) is Packet:
            # This is a direct instance of the base Packet type, meaning
            # that it is a packet of unknown type, so we do not print it.
            return
    def process_chat_packet(self, packet):
        json_data = json.loads(packet.json_data)
        message = json_data['with'][-1].split()

        if message[0] == '!bot':
            if message[1] == 'goto':
                target = [int(x) for x in message[2:5]]

                alg = AStarAlgorithm(self.world)
                if len(message) > 5:
                    path = alg.find_path([int(x) for x in self.position], target, max_distance=int(message[5]))[1:]
                else:
                    path = alg.find_path([int(x) for x in self.position], target)[1:]
                thread = MovingThread('moving', path, self)
                thread.start()
                

                

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
