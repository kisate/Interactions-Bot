from minecraft.networking.packets import serverbound
from minecraft.networking.packets.packet_buffer import PacketBuffer
from minecraft.networking.types import (
    Byte, VarInt, String
)
import os, re
import zipfile, glob, json

class ForgeHandshaker():
    def __init__(self, connection):
        self.connection = connection
        self.state = 0
    
    def make_modlist_packet(self, packet):
        packet.channel = 'FML|HS'
        buffer = PacketBuffer()
        Byte.send(2, buffer)   
        modlist = []
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'modlist5.txt'), 'r') as f:
            mods = f.read().split(',')
            for mod in mods:
                mod_name = mod.split('@')[0]
                mod_version = mod[len(mod_name) + 1:]
                modlist.append([mod_name, mod_version])
        VarInt.send(len(modlist), buffer)
        for mod in modlist:
            String.send(mod[0], buffer)
            String.send(mod[1], buffer)
        buffer.reset_cursor()
        packet.data = buffer.read()
        print(packet.data)

    def feed_packet(self, packet):
        if packet.channel == 'REGISTER':
            _packet = serverbound.play.PluginMessagePacket(self.connection.context)
            _packet.channel = 'REGISTER'
            _packet.data = packet.data
            self.connection.write_packet(_packet)
        elif packet.channel == 'FML|HS':
            if packet.data[0] == 0:
                _packet = serverbound.play.PluginMessagePacket(self.connection.context)
                _packet.channel = 'FML|HS'
                _packet.data = b'\x01\x02'
                self.connection.write_packet(_packet)
                _packet = serverbound.play.PluginMessagePacket(self.connection.context)
                self.make_modlist_packet(_packet)
                self.connection.write_packet(_packet)
            elif packet.data[0] == 2 and self.state == 0:
                _packet = serverbound.play.PluginMessagePacket(self.connection.context)
                _packet.channel = 'FML|HS'
                _packet.data = b'\xFF\x02'
                self.state = 1
                self.connection.write_packet(_packet)
            elif packet.data[0] == 3 and packet.data[1] != 0:
                _packet = serverbound.play.PluginMessagePacket(self.connection.context)
                _packet.channel = 'FML|HS'
                _packet.data = b'\xFF\x03'
                self.connection.write_packet(_packet)
            elif packet.data[0] == 2 and self.state == 1:
                _packet = serverbound.play.PluginMessagePacket(self.connection.context)
                _packet.channel = 'FML|HS'
                _packet.data = b'\xFF\x04'
                self.connection.write_packet(_packet)
                self.state = 2
            elif packet.data[0] == 3 and self.state == 2:
                _packet = serverbound.play.PluginMessagePacket(self.connection.context)
                _packet.channel = 'FML|HS'
                _packet.data = b'\xFF\x05'
                self.connection.write_packet(_packet)

                
    


# modlist = []
# __location__ = os.path.realpath(
#     os.path.join(os.getcwd(), os.path.dirname(__file__)))
# with open(os.path.join(__location__, 'modlist2.txt'), 'r') as f:
# # #     for line in f.readlines():
# # #         mod_name = re.search(r'.*: R', line).group(0)[:-3]
# # #         mod_version = re.search(r'on .* bu', line).group(0)[3:-3]
# # #         # print(f'{mod_name} {mod_version}')
# # #         modlist.append([mod_name, mod_version])
# with open(os.path.join(__location__, 'modlist.txt'), 'r') as f:
#     for line in f.readlines():
#         mod = re.search(r'\)>.*?</', line).group(0)[2:-2]
#         name = re.search(r'.*?-', mod)
#         if name is not None:
#             modlist.append([name.group(0)[:-1], "1"])   

# print(modlist)
# mod
# import zipfile, glob, json
# __location__ = os.path.realpath(
#     os.path.join(os.getcwd(), os.path.dirname(__file__)))
# with open(os.path.join(__location__, 'modlist4.txt'), 'w') as f:
#     for pathname in glob.glob('/home/dumtrii/ftb/FTBInteractions/minecraft/mods/*.jar'):
#         zf = zipfile.ZipFile(pathname, 'r')
#         try:
#             lst = zf.infolist()
#             for zi in lst:
#                 fn = zi.filename
#                 if fn == 'mcmod.info':
#                     info = zf.open(fn)
#                     data = info.read().decode('utf-8')
#                     mod_id = re.search(r'"modid"\s?:\s?".*",', data)
#                     mod_version = re.search(r'"version"\s?:\s?".*",', data)
#                     mod_name = re.search(r'"name"\s?:\s?".*",', data)
#                     if mod_id is not None and mod_version is not None and mod_name is not None: 
#                         mod_id = mod_id.group(0).split('"')[3]
#                         mod_version = mod_version.group(0).split('"')[3]
#                         mod_name = mod_name.group(0).split('"')[3]
#                         f.write(f"{mod_id}:{mod_version}:{mod_name}\n")
#                     else :
#                         print(data)
#         finally:
#             zf.close()