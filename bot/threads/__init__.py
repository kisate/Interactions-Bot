from minecraft.networking.packets.serverbound.play import ChatPacket
from minecraft.networking.types import Position, Slot

from packets.serverbound.play import DiggingPacket, ClickWindowPacket


from threading import Thread, Lock
from time import sleep
from math import floor
import traceback

class MovingThread(Thread):
        def __init__(self, name, bot, algorithm, args):
            Thread.__init__(self)
            self.name = name
            self.bot = bot
            self.args = args
            self.algorithm = algorithm
            
        def run(self):
            with self.bot.lock:
                try:
                    self.bot.say('Searching path to {}'.format(self.args['end']))
                    result = self.algorithm(**self.args)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    self.bot.say('Exception occured while path-finding. Check console', 1)
                    return
                    
                if result is None:
                    self.bot.say("No path found. (Could be too long)", 1)

                    return

                self.bot.say('Moving to {}'.format(result[0][-1]))

                for step in result[0][1:]:
                    interval = 0.4*result[1]/8

                    for action in step[1]:
                        if action == 0:
                            self.bot.update_position([step[0][0]+0.5, step[0][1], step[0][2]+0.5])
                            sleep(interval)

                        if self.bot.break_event.isSet():
                            self.bot.break_event.clear()
                            self.bot.say('Stopped', 1)
                            return
                    


                if self.bot.world.get_block(floor(self.bot.position[0]), floor(self.bot.position[1]) - 1, floor(self.bot.position[2])) == 0:
                    self.bot.say("I'm falling at {}".format(self.bot.position), 1)

                    thread = FallingThread('falling', self.bot)
                    thread.start()
                    thread.join()

                sleep(0.5)

                self.bot.say('Finished moving. My position is {}'.format(self.bot.position))

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
    def __init__(self, name, bot, algorithm, args):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.algorithm = algorithm
        self.args = args
    
    def run(self):
        self.args['radius'] = self.bot.MINING_RADIUS
        if 'step_length' not in self.args.keys():
            self.args['step_length'] = 1
            self.args['pivot'] = [0, 1.5, 0]
        
        thread = MovingThread('moving', self.bot, self.algorithm, self.args)
        thread.run()

        if sum((self.bot.position[i] + self.args['pivot'][i] - self.args['end'][i])**2 for i in range(3))**0.5 > self.bot.MINING_RADIUS:
            # print("Distance to block is {}".format(sum((self.bot.position[i] + self.args['pivot'][i] - self.args['end'][i])**2 for i in range(3))**0.5))
            self.bot.say('Could not get to block. My position is {}'.format(self.bot.position), 2)
            return
        
        with self.bot.lock:
            self.bot.say('Mining {}. It is {}'.format(self.args['end'], self.bot.world.get_block(*self.args['end'])))

            packet = DiggingPacket()
            packet.location = Position(x=self.args['end'][0], y=self.args['end'][1], z=self.args['end'][2])
            packet.status = 0
            packet.face = 1
            self.bot.connection.write_packet(packet)

            while self.bot.world.get_block(*self.args['end']) != 0:
                packet = DiggingPacket()
                packet.location = Position(x=self.args['end'][0], y=self.args['end'][1], z=self.args['end'][2])
                packet.status = 2
                packet.face = 1
                self.bot.connection.write_packet(packet)
                
                sleep(0.1)

                if self.bot.break_event.isSet():
                    self.bot.break_event.clear()
                    self.bot.say('Stopped', 1)
                    return

            self.bot.say('Finished mining')


class MultiMiningThread(Thread):

    @staticmethod
    def clever_comparator(p1, p2, far_distance=10000):
        distance = sum([(p1[i] - p2[i])**2 for i in range(3)])
        if p2[1] - floor(p1[1]) not in [0, 1]:
            distance += far_distance
        return distance

    def __init__(self, name, bot, algorithm, blocks, args, with_tool=True, comparator=None):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.algorithm = algorithm
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
        self.bot.say('Setting chat level to 2 to avoid kicking')
        self.bot.chat_level = 2        

        while self.blocks:

            self.blocks.sort(key=lambda x: self.comparator(self.bot.position, x), reverse=True)
            block = self.blocks.pop()
            self.args['start'] = [floor(x) for x in self.bot.position]
            self.args['end'] = block

            if self.with_tool:
                self.bot.mine_with_tool(self.algorithm, self.args)
            else:
                thread = MiningThread('mining', self.bot, self.algorithm, self.args)
                thread.run()

            if self.bot.break_event.isSet() or self.bot.break_event_multi.isSet():
                    self.bot.break_event.clear()
                    self.bot.break_event_multi.clear()
                    self.bot.chat_level = 0
                    self.bot.say('Stopped', 3)
                    return
        self.bot.chat_level = 0
        self.bot.say('Chat level is 0')
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
