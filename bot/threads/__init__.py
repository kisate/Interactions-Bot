from minecraft.networking.packets.serverbound.play import ChatPacket
from minecraft.networking.types import Position, Slot

from packets.serverbound.play import DiggingPacket, ClickWindowPacket
from exceptions import NoToolException, ChunkNotLoadedException

import numpy as np
from threading import Thread, Lock
from time import sleep
from math import floor
import traceback
from .path_finding_algorithm import Algorithm
class MovingThread(Thread):
        def __init__(self, name, bot, args, time_to_wait=0.4):
            Thread.__init__(self)
            self.name = name
            self.bot = bot
            self.args = args
            self.time_to_wait = time_to_wait
            
        def run(self):
            with self.bot.lock:
                try:
                    self.args['break_event'] = self.bot.break_event
                    self.bot.say('Searching path to {}'.format(self.args['end']))
                    result = Algorithm.find_path(self.bot.world, **self.args)
                except ChunkNotLoadedException as e:
                    self.bot.say(f'Chunk {e.chunk_coords} not loaded')
                    print(e)
                    traceback.print_exc()
                    self.bot.say('Exception occured while path-finding. Check console', 1)
                    return
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    self.bot.say('Exception occured while path-finding. Check console', 1)
                    return
                    
                if result is None:
                    if self.bot.break_event.isSet():
                        self.bot.break_event.clear()
                        self.bot.say('Stopped', 1)
                        return
                    self.bot.say("No path found. (Could be too long)", 1)
                    return

                self.bot.say('Moving to {}'.format(result[0][-1]))

                for step in result[0][1:]:
                    interval = self.time_to_wait*result[1]/8

                    for action in step[1]:
                        if action == 0:
                            self.bot.update_position([step[0][0]+0.5, step[0][1], step[0][2]+0.5])
                        elif action == 2:
                            self.bot.lock.release()
                            res = self.bot.mine_with_tool(step[0], setup=True)
                            self.bot.lock.acquire()
                            if not res or res == -1:
                                self.bot.say('Could not do action {} on block {}'.format(action, step[0]), -1)
                                return
                        elif action == 3:
                            self.bot.lock.release()
                            res = self.bot.mine_with_tool(np.sum([[0, 1, 0], step[0]], axis=0), setup=True)
                            self.bot.lock.acquire()
                            if not res or res == -1:
                                self.bot.say('Could not do action {} on block {}'.format(action, step[0]), -1)
                                return

                        if self.bot.break_event.isSet():
                            self.bot.break_event.clear()
                            self.bot.say('Stopped', 1)
                            return
                        sleep(interval)
                    


                if self.bot.world.get_block(floor(self.bot.position[0]), floor(self.bot.position[1]) - 1, floor(self.bot.position[2])) == 0:
                    self.bot.say("I'm falling at {}".format(self.bot.position), 1)

                    thread = FallingThread('falling', self.bot)
                    thread.start()
                    thread.join()

                sleep(0.2)

                self.bot.say('Finished moving. My position is {}'.format(self.bot.position))
                return True

class FallingThread(Thread):
    def __init__(self, name, bot):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
    def run(self):
        self.bot.lock.acquire(False)
        position = [floor(x) for x in self.bot.position]
        while self.bot.world.get_block(position[0], position[1] - 1, position[2]) == 0:
            position = [floor(x) for x in self.bot.position]
            self.bot.update_position([position[0] + 0.5, position[1] - 1, position[2] + 0.5])
            sleep(0.1)
            if self.bot.break_event.isSet():
                    self.bot.break_event.clear()
                    self.bot.say('Stopped', 1)
                    return

class MiningThread(Thread):
    def __init__(self, name, bot, target):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.target = target
    
    def run(self, time_to_wait=0.4):
        with self.bot.lock:
            self.bot.say('Mining {}. It is {}'.format(self.target, self.bot.world.get_block(*self.target)))

            packet = DiggingPacket()
            packet.location = Position(x=self.target[0], y=self.target[1], z=self.target[2])
            packet.status = 0
            packet.face = 1
            self.bot.connection.write_packet(packet)

            while self.bot.world.get_block(*self.target) != 0:
                packet = DiggingPacket()
                packet.location = Position(x=self.target[0], y=self.target[1], z=self.target[2])
                packet.status = 2
                packet.face = 1
                self.bot.connection.write_packet(packet)
                
                sleep(0.05)

                if self.bot.break_event.isSet():
                    self.bot.break_event.clear()
                    self.bot.say('Stopped', 1)
                    return

            self.bot.say('Finished mining')
        
        return True


class MultiMiningThread(Thread):

    @staticmethod
    def clever_comparator(p1, p2, far_distance=10000, same_level=True):
        distance = sum([(p1[i] - p2[i])**2 for i in range(3)])
        if same_level and p2[1] - floor(p1[1]) not in [0, 1]:
            distance += far_distance
        return distance

    def __init__(self, name, bot, blocks, args, with_tool=True, comparator=None):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.blocks = blocks
        self.args = args
        self.with_tool = with_tool
        self.comparator = comparator
        if comparator == None:
            self.comparator = self.clever_comparator
        
    def run(self):

        if self.with_tool and not self.bot.set_up_tools():
            self.bot.say('Could not setup')
            return

        self.bot.say('Starting multi mining')
        if self.bot.chat_level in range(0, 3):
            self.bot.say('Setting chat level to -1 to avoid kicking')
            self.bot.chat_level = -1       
        
        self.blocks.sort(key=lambda x: self.comparator(self.bot.position, x), reverse=True)

        while self.blocks:

            self.blocks.sort(key=lambda x: self.comparator(self.bot.position, x), reverse=True)
            block = self.blocks.pop()
            self.args['start'] = [floor(x) for x in self.bot.position]
            self.args['end'] = block

            if self.with_tool:
                try: 
                    thread = MoveToAndMineThread('mining', self.bot, self.args)
                    result = thread.run(time_to_wait=0.2)
                    if result != -1 and not result:
                        self.blocks.append(block)

                except NoToolException as e:
                    self.bot.chat_level = 0
                    self.bot.say("No tool of {} type, aborting.".format(e.tool), 3)
                    print("No tool of {} type, aborting.".format(e.tool))
                    break
            else:
                thread = MoveToAndMineThread('mining', self.bot, self.args, with_tool=False)
                if not thread.run(time_to_wait=0.2):
                    self.blocks.append(block)

            if self.bot.break_event.isSet() or self.bot.break_event_multi.isSet():
                    self.bot.break_event.clear()
                    self.bot.break_event_multi.clear()
                    self.bot.chat_level = 0
                    self.bot.say('Stopped', 3)
                    return
        self.bot.chat_level = 1
        self.bot.say('Chat level is 1')
        self.bot.say('Finished multi mining')

class ItemSwapThread(Thread):
    def __init__(self, name, bot, first_slot, second_slot):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.first_slot = first_slot
        self.second_slot = second_slot
        print("First : {}, Second : {}".format(first_slot, second_slot))
    
    def get_left_click_packet(self, slot, empty=False):
        packet = ClickWindowPacket()
        packet.window_id = 0
        packet.slot = slot
        packet.button = 0
        packet.action_number = self.bot.inventory.action_number
        packet.mode = 0
        if empty:
            packet.clicked_item = Slot(-1)
        else:
            packet.clicked_item = self.bot.inventory[slot]
        self.bot.inventory.action_number += 1

        return packet

    def run(self):
        packet = self.get_left_click_packet(self.first_slot)
        first_item = packet.clicked_item
        self.bot.connection.write_packet(packet)
        self.bot.inventory[self.first_slot] = Slot(-1)
        sleep(0.1)
        packet = self.get_left_click_packet(self.second_slot)
        self.bot.connection.write_packet(packet)
        second_item = packet.clicked_item
        self.bot.inventory[self.second_slot] = first_item
        sleep(0.1)
        packet = self.get_left_click_packet(self.first_slot, empty=True)
        self.bot.connection.write_packet(packet)
        self.bot.inventory[self.first_slot] = second_item
        sleep(0.1)

class MoveToAndMineThread(Thread):
    def __init__(self, name, bot, args, with_tool=True):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.args = args
        self.with_tool = with_tool
    
    def run(self, time_to_wait=0.4):
        self.args['radius'] = self.bot.MINING_RADIUS
        if 'step_length' not in self.args.keys():
            self.args['step_length'] = 1
        self.args['pivot'] = [0.5, 1.5, 0.5]
        self.args['priority_function'] = 'wmp'
        
        thread = MovingThread('moving', self.bot, self.args, time_to_wait=time_to_wait)
        thread.run()

        if sum((floor(self.bot.position[i]) + self.args['pivot'][i] - self.args['end'][i])**2 for i in range(3))**0.5 > self.bot.MINING_RADIUS:
            print("Distance to block is {}".format(sum((floor(self.bot.position[i]) + self.args['pivot'][i] - self.args['end'][i])**2 for i in range(3))**0.5))
            self.bot.say('Could not get to block {}. My position is {}'.format(self.args['end'], self.bot.position), 2)
            return False
        
        if self.with_tool:
            return self.bot.mine_with_tool(self.args['end'])
        else:
            return MiningThread('mining', self.bot, self.args['end']).run()

class FollowingThread(Thread):
    def __init__(self, name, bot, args, target):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.args = args
        self.target = target
    
    def run(self):
        
        while True:

            target_pos = self.bot.entity_coords[self.target]

            if sum([(target_pos[i] - self.bot.position[i])**2 for i in range(3)])**0.5 > 3:
                block_under_target = self.bot.world.get_block(floor(target_pos[0]), floor(target_pos[1]) - 1, floor(target_pos[2]))
                if block_under_target != 0 and block_under_target not in self.bot.world.info['blocks']['damaging']:
                    args = {'start' : [floor(x) for x in self.bot.position], 'end' : [floor(x) for x in target_pos], 'radius' : 3}
                    thread = MovingThread('moving', self.bot, args)
                    thread.run()
                

            if self.bot.break_event.isSet() or self.bot.break_event_multi.isSet():
                self.bot.break_event.clear()
                self.bot.break_event_multi.clear()
                self.bot.chat_level = 0
                self.bot.say('Stopped', 3)
                return

class GetToChunkThread(Thread):
    def __init__(self, name, bot, args, target):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.args = args
        self.target = target
    def run(self):
        try:
            chunk = self.bot.world.get_chunk_by_chunk_coords(*self.target)
        except ChunkNotLoadedException:
            nearest_chunks = [[self.target[0], self.target[1] - 1], [self.target[0] - 1, self.target[1]], 
                                [self.target[0] + 1, self.target[1]], [self.target[0], self.target[1] + 1]]
            distance_to_chunks = [[(x[0]-self.bot.position[0])**2 + (x[1]-self.bot.position[2])**2] for x in nearest_chunks]
            nearest_chunk_coords = nearest_chunks[distance_to_chunks.index(min(distance_to_chunks))]
            thread = GetToChunkThread(self.name, self.bot, self.args, nearest_chunk_coords)
            thread.run()
        for x in range(16):
            for z in range(16):
                self.args['start'] = [floor(x) for x in self.bot.position]
                self.args['end'] = [self.target[0]*16 + x, 0, self.target[1]*16 + z]
                self.args['ignore_y'] = True
                self.args['drop_after'] = 200
                res = MovingThread('move', self.bot, self.args).run() 
                if res == True:
                    break
        if res:
            return True
        