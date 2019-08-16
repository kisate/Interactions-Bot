from minecraft.networking.packets.serverbound.play import ChatPacket

from threading import Thread, Lock
from time import sleep
from math import floor

class MovingThread(Thread):
        def __init__(self, name, path, bot):
            Thread.__init__(self)
            self.name = name
            self.path = path
            self.bot = bot
            
        def run(self):
            self.bot.lock.acquire()
            if self.path is None:
                packet = ChatPacket()
                packet.message = "No path found. (Could be too long)"
                self.bot.connection.write_packet(packet)
                self.bot.lock.release()
                return
            for step in self.path:
                for action in step[1]:
                    if action == 0:
                        self.bot.update_position([step[0][0]+0.5, step[0][1], step[0][2]+0.5])
                        sleep(0.5)
            
            if self.bot.world.get_block(floor(self.bot.position[0]), floor(self.bot.position[1]) - 1, floor(self.bot.position[2])) == 0:
                packet = ChatPacket()
                packet.message = "I'm falling at {}".format(self.bot.position)
                self.bot.connection.write_packet(packet)

                thread = FallingThread('falling', self.bot)
                thread.start()
            if self.bot.lock.locked():
                self.bot.lock.release()

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
        if self.bot.lock.locked():
            self.bot.lock.release()