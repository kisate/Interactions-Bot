from bot.threads.path_finding_algorithms import StraightForwardAlgorithm, AStarAlgorithm
from bot.threads import *

import random
from minecraft.networking.packets import Packet, clientbound, serverbound
from minecraft.networking.packets.clientbound.play import PlayerPositionAndLookPacket, JoinGamePacket, SetSlotPacket, WindowItemsPacket
from minecraft.networking.types import (
    Position
)

from packets.serverbound.play import *
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
        with open(os.path.join(str(Path(__file__).absolute().parent), 'id_info.txt'), 'r') as f:
            text = f.read()
            info = json.loads(text)
            self.world = World(info)
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
        self.held_slot = 0

    def say(self, message, level=0):
        if level >= 0 and level >= self.chat_level:
            packet = serverbound.play.ChatPacket()
            packet.message = message
            self.connection.write_packet(packet)
        elif level == -1:
            print("Redirecting say to console: {}".format(message))
    
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
            # print("{} {}".format(packet.number_of_entities, packet.chunk.entities))

        elif type(packet) is clientbound.play.block_change_packet.BlockChangePacket:
            
            self.world.update_block(*packet.location, packet.block_state_id, relative=False)

        elif type(packet) is clientbound.play.block_change_packet.MultiBlockChangePacket:
            self.world.update_block_multi(packet.chunk_x, packet.chunk_z, packet.records)
        
        elif type(packet) is clientbound.play.ChatMessagePacket:
            # print(packet)
            self.process_chat_packet(packet)

        elif type(packet) is JoinGamePacket:
            self.dimension = packet.dimension

        elif type(packet) is SetSlotPacket:
            if packet.window_id in [0, -2]:
                self.inventory[packet.slot] = packet.slot_data
            print(packet)

        elif type(packet) is WindowItemsPacket:
            if packet.window_id == 0:
                for i, slot in enumerate(packet.slots):
                    self.inventory[i] = slot

        elif type(packet) is clientbound.play.inventory_packets.ConfirmTransactionPacket:
            if not packet.accepted:
                response = ConfirmTransactionPacket()
                response.window_id = packet.window_id
                response.action_number = packet.action_number
                response.accepted = packet.accepted
                self.connection.write_packet(response)
            # print(packet)

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
                        if (self.world.get_block(*args['end']) in self.world.info['blocks']['passable'] 
                            and self.world.get_block(args['end'][0], args['end'][1] + 1, args['end'][2]) 
                                in self.world.info['blocks']['passable']
                                    and self.world.get_block(args['end'][0], args['end'][1] - 1, args['end'][2])
                                        not in self.world.info['blocks']['passable']) or 'radius' in args.keys() and args['radius'] > 1:
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

                    elif message[1] == 'list':
                        print(self.inventory)

                    elif message[1] == 'swap':
                        slots = [int(x) for x in message[2:4]]
                        thread = ItemSwapThread('item swap', self, *slots)
                        thread.start()

                    elif message[1] == 'hold':
                        self.hold(int(message[2]))
                    
                    elif message[1] == 'setup':
                        Thread(target=self.set_up_tools).start()

                    elif message[1] == 'minechunk':
                        self.break_event.clear()
                        self.break_event_multi.clear()
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

                        for x in range(16):
                            for y in range(256):
                                for z in range(16):
                                    block = chunk.get_block(x, y, z, True)
                                    if block != 0 and self.world.info['blocks']['tool'][str(block)] >= 0:
                                        blocks.append([x + chunk_x*16, y, z + chunk_z*16])
                        
                        self.say('Found {} blocks'.format(len(blocks)))

                        alg = AStarAlgorithm(self.world)
                        thread = MultiMiningThread('multimining', self, alg.find_path, blocks, args)
                        thread.start()

                    elif message[1] == 'minerect':
                        p1, p2 = [int(x) for x in message[2:5]], [int(x) for x in message[5:8]]
                        p1, p2 = [min(p1[i], p2[i]) for i in range(3)], [max(p1[i], p2[i]) for i in range(3)] 

                        args = {}

                        for additional_arg in message[3:]:
                            key, value = additional_arg.split('=')
                            if key == 'step_length' or key == 'radius':
                                args[key] = float(value)
                            else:
                                args[key] = int(value)

                        blocks = []

                        for x in range(p1[0], p2[0]):
                            for y in range(p1[1], p2[1]):
                                for z in range(p1[2], p2[2]):
                                    
                                    blocks.append([x, y, z])

                        self.say('Found {} blocks'.format(len(blocks)))

                        alg = AStarAlgorithm(self.world)
                        thread = MultiMiningThread('multimining', self, alg.find_path, blocks, args)
                        thread.start()

                    else:
                        self.say("Wrong command", 1)

                except Exception as e:
                    self.say("Something's wrong. Check console", 3)
                    traceback.print_exc()
        else:
            print(len(json_data['with']))
            print(json_data['with'])

    def hold(self, slot):
        packet = HeldItemChangePacket()
        packet.slot = slot
        self.held_slot = slot
        self.connection.write_packet(packet)
             
    def set_up_tools(self):
        tools = {
            'pickaxe' : None,
            'axe' : None,
            'shovel' : None
        }

        self.inventory.action_number = 1

        for j, key in enumerate(tools.keys()):
            for i, slot in enumerate(self.inventory.slots):
                if slot.item_id in self.world.info['items']['{}s'.format(key)]:
                    tools[key] = (i, slot)
                    break

            if tools[key] is None:
                self.say("No {}".format(key), 1)
                return False
            
            if tools[key][0] != 36 + j:
                thread = ItemSwapThread('item swap', self, 36 + j, tools[key][0])
                thread.run()

        return True

    def mine_with_tool(self, algorithm, args, setup=False):
        if setup and not self.set_up_tools():
            return
        
        tool_slots = {
            0 : 3,
            1 : 0,
            2 : 1,
            3 : 2
        }

        tool = self.world.info['blocks']['tool'][str(self.world.get_block(*args['end']))]

        if tool == -1:
            self.say('{} is unbreakable'.format(args['end']), 1)
            return
        if tool not in tool_slots.keys():
            self.say("Don't have {} slot".format(self.world.info['items']['tool_ids'][str(tool)]), 1)
            return
        
        tool_slot = tool_slots[tool]

        self.hold(tool_slot)

        thread = MiningThread('mining', self, algorithm, args)
        thread.run()

        



        
