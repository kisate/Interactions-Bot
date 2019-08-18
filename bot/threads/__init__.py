from minecraft.networking.packets.serverbound.play import ChatPacket
from minecraft.networking.types import Position
from packets.serverbound.play import DiggingPacket


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
    def __init__(self, name, bot, algorithm, blocks, args):
        Thread.__init__(self)
        self.name = name
        self.bot = bot
        self.algorithm = algorithm
        self.blocks = blocks
        self.args = args
        
    
    def run(self):
        
        self.bot.say('Starting multi mining')
        self.bot.say('Setting chat level to 2 to avoid kicking')
        self.bot.chat_level = 2

        for block in self.blocks:
            self.args['start'] = [floor(x) for x in self.bot.position]
            self.args['end'] = block

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


        