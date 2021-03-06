from bot.threads.path_finding_algorithm import Algorithm
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
from exceptions import NoToolException, TooManyArgumentsException
from .forge_handshaker import ForgeHandshaker

import json, os, re
import math
import inspect
from .chat_commands import *

from threading import Thread, Lock, Event
import traceback

from pathlib import Path
import pickle


class Bot():
    MINING_RADIUS = 5
    def __init__(self, connection, name):
        with open(os.path.join(str(Path(__file__).absolute().parent), 'id_info.txt'), 'r') as f:
            text = f.read()
            info = json.loads(text)
            self.world = World(info)
        self.connection = connection
        self.name = name
        self.position = [0, 0, 0]
        self.rotation = [0, 0]
        self.lock = Lock()
        self.break_event = Event()
        self.break_event_multi = Event()
        self.dimension = 0
        self.loaded = False
        self.loaded_health = False
        self.chat_level = 2
        self.inventory = Inventory()
        self.held_slot = 0
        self.health = 20
        self.food = 20
        self.forge_handshaker = ForgeHandshaker(self.connection)
        self.players = {}
        self.player_UUIDs = {}
        self.entity_coords = {}

    def say(self, message, level=0):
        if level == -1 or self.chat_level == -1:
            print("Redirecting say to console: {}".format(message))
    
        elif level >= 0 and level >= self.chat_level:
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
                self.say('Finished loading', 3)
                # with open('world.data', 'wb') as f:
                #     pickle.dump(self.world, f)

            self.position[0] = packet.x
            self.position[1] = packet.y
            self.position[2] = packet.z

            self.rotation[0] = packet.yaw
            self.rotation[1] = packet.pitch

            print("--> {}".format(packet))
        
        elif type(packet) is clientbound.play.chunk_data_packet.ChunkDataPacket:
            packet.chunk.read_data(packet.data, self.dimension)
            # self.world.chunks.append(packet.chunk)
            self.world.add_chunk(packet.chunk)
            if self.loaded :
                print(type(packet))
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

        elif type(packet) is clientbound.play.UpdateHealthPacket:
            
            if self.health > packet.health and self.loaded_health:
                _packet = serverbound.play.ChatPacket()
                _packet.message = f'/teleport {self.name} ~ 100 ~'
                self.connection.write_packet(_packet)
                self.say(f"I've been hurt. My health is {packet.health}", 4)

            self.health = packet.health
            self.food = packet.food
            self.loaded_health = True

        elif type(packet) is clientbound.login.LoginSuccessPacket:
            print(packet)

        elif type(packet) is clientbound.play.PluginMessagePacket:
            print(packet)
            self.forge_handshaker.feed_packet(packet)

        # elif type(packet) is clientbound.play.EntityVelocityPacket:
        #     print(packet)
        
        # elif type(packet) is clientbound.play.EntityLookPacket:
        #     print(packet)
        elif type(packet) is clientbound.play.EntityLookAndRelativeMovePacket:
            if packet.entity_id in self.entity_coords.keys():
                delta = [packet.delta_x / 4096, packet.delta_y / 4096, packet.delta_z / 4096]
                self.entity_coords[packet.entity_id] = [self.entity_coords[packet.entity_id][i] + delta[i] for i in range(3)]
                # print(f"{packet} {delta}")
        elif type(packet) is clientbound.play.EntityRelativeMovePacket:
            if packet.entity_id in self.entity_coords.keys():
                delta = [packet.delta_x / 4096, packet.delta_y / 4096, packet.delta_z / 4096]
                self.entity_coords[packet.entity_id] = [self.entity_coords[packet.entity_id][i] + delta[i] for i in range(3)]
                # print(f"{packet} {delta}")
        elif type(packet) is clientbound.play.EntityTeleportPacket:
            if packet.entity_id in self.entity_coords.keys():
                self.entity_coords[packet.entity_id] = [packet.x, packet.y, packet.z]
            # print(packet)

        elif type(packet) is clientbound.play.SpawnPlayerPacket:
            print(packet)
            self.players[packet.entity_id] = packet.player_UUID
            self.player_UUIDs[packet.player_UUID] = packet.entity_id
            self.entity_coords[packet.entity_id] = [packet.x, packet.y, packet.z]
        

        if type(packet) is Packet:
            # This is a direct instance of the base Packet type, meaning
            # that it is a packet of unknown type, so we do not print it.
            return
    def process_chat_packet(self, packet):
        
        json_data = json.loads(packet.json_data)
        if 'with' in json_data.keys() and len(json_data['with']) == 2 and type(json_data['with'][1]) is str:
            message = json_data['with'][1].split()    
            if message[0] == '!bot':
                self.break_event.clear()
                self.break_event_multi.clear()
                try:
                    command = message[1]
                    func = commands[command]
                    func_arg_names = inspect.getfullargspec(func)[0][1:]
                    # print(func.__annotations__)

                    args = []
                    kwargs = {}
                    argument_idx = 0
                    for arg in message[2:]:
                        if '=' in arg:
                            key, value = arg.split('=')
                            kwargs[key] = value
                        else:
                            if argument_idx < len(func.__annotations__):
                                # cast the argument to the annotated type
                                args.append(func.__annotations__[
                                            func_arg_names[argument_idx]](arg))
                                argument_idx += 1
                            else:
                                raise TooManyArgumentsException(message)

                    if func in use_json_data:
                        args.append(re.search(r'id:".*"', json_data['with'][0]['hoverEvent']['value']['text']).group(0)[4:-1])
                    # call the appropriate command
                    print(f'Calling {command} with normal arguments: {args}, keyword arguments: {kwargs}')
                    if 'kwargs' not in func_arg_names:
                        if len(kwargs) == 0:
                            func(self, *args)
                        else:
                            raise mydong
                    else:
                        func(self, *args, kwargs)

                    """ if message[1] == 'goto':
                        self.break_event.clear()
                        args = {'start' : [math.floor(x) for x in self.position], 'end' : [int(x) for x in message[2:5]]}
                        for additional_arg in message[5:]:
                            key, value = additional_arg.split('=')
                            args[key] = value
                                # if key == 'step_length' or key == 'radius':
                                #     args[key] = float(value)
                                # else:
                                #     args[key] = int(value)
                        # if (self.world.get_block(*args['end']) in self.world.info['blocks']['passable'] 
                        #     and self.world.get_block(args['end'][0], args['end'][1] + 1, args['end'][2]) 
                        #         in self.world.info['blocks']['passable']
                        #             and self.world.get_block(args['end'][0], args['end'][1] - 1, args['end'][2])
                        #                 not in self.world.info['blocks']['passable']) or 'radius' in args.keys() and args['radius'] > 1:
                        if (True):
                            thread = MovingThread('moving', self, args)
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
                            thread = MoveToAndMineThread('move to and mind', self, args)
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

                        thread = MultiMiningThread('multimining', self, blocks, args)
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

                        thread = MultiMiningThread('multimining', self, blocks, args)
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

                        thread = MultiMiningThread('multimining', self, blocks, args)
                        thread.start()

                    elif message[1] == 'respawn':
                        packet = serverbound.play.ClientStatusPacket()
                        packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
                        self.connection.write_packet(packet)

                    elif message[1] == 'place':
                        location = [int(x) for x in message[2:5]]
                        face = 1
                        hand = 0
                        cursor_x = 0
                        cursor_y = 0
                        cursor_z= 0

                        self.hold(0)
                        packet = PlayerBlockPlacementPacket()
                        packet.location = Position(x=location[0], y=location[1], z=location[2])
                        packet.face = face
                        packet.hand = hand
                        packet.cursor_x = cursor_x
                        packet.cursor_y = cursor_y
                        packet.cursor_z = cursor_z
                        self.connection.write_packet(packet)

                    elif message[1] == 'tome':
                        player_id = re.search(r'id:".*"', json_data['with'][0]['hoverEvent']['value']['text']).group(0)[4:-1]
                        entity_id = self.player_UUIDs[player_id]
                        args = {'start' : [math.floor(x) for x in self.position], 'end' : [math.floor(x) for x in self.entity_coords[entity_id]]}
                        print(args['end'])
                        thread = MovingThread('moving', self, args)
                        
                        thread.start()
 
                    elif message[1] == 'followme':
                        player_id = re.search(r'id:".*"', json_data['with'][0]['hoverEvent']['value']['text']).group(0)[4:-1]
                        entity_id = self.player_UUIDs[player_id]
                        args = {}
                        thread = FollowingThread('follow', self, args, entity_id)
                        thread.start()

                    elif message[1] == 'tochunk':
                        target = [int(x) for x in message[2:4]]
                        GetToChunkThread('get to chunk', self, {}, target).start() """
                    # else:
                    #     self.say("Wrong command", 1)

                except Exception as e:
                    self.say("Something's wrong. Check console", 3)
                    traceback.print_exc()
        else:
            print(json_data)

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

    def mine_with_tool(self, target, setup=False):
        if setup and not self.set_up_tools():
            return -1
        
        print('target is {}'.format(target))

        tool_slots = {
            0 : 3,
            1 : 0,
            2 : 1,
            3 : 2
        }

        tool = self.world.info['blocks']['tool'][str(self.world.get_block(*target))]

        if tool == -1:
            self.say('{} is unbreakable'.format(target), 1)
            return -1
        if tool not in tool_slots.keys():
            self.say("Don't have {} slot".format(self.world.info['items']['tool_ids'][str(tool)]), 1)
            return -1
        
        tool_slot = tool_slots[tool]

        if self.held_slot != tool_slot:
            self.hold(tool_slot)

        if tool != 0 and self.inventory[36 + self.held_slot].item_id not in self.world.info['items'][self.world.info['items']['tool_ids'][str(tool)]]:
            self.set_up_tools()
            if self.inventory[36 + self.held_slot].item_id not in self.world.info['items'][self.world.info['items']['tool_ids'][str(tool)]]:
                raise NoToolException(self.world.info['items']['tool_ids'][str(tool)])

        thread = MiningThread('mining', self, target)
        return thread.run()

    def get_int_position(self):
        return [math.floor(x) for x in self.position]