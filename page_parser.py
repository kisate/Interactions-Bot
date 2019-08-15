import urllib.request
from html.parser import HTMLParser

types_dict = {
    'Unsigned Byte' : 'Byte'
}

def process_field_type(f_type):
    if f_type.startswith('String'):
        return 'String'
    
    if f_type in types_dict.keys():
        return types_dict[f_type]

    f_type = f_type.replace(' Enum', '')
    f_type = f_type.replace(' enum', '')


    return f_type
    

class Parser(HTMLParser):

    def __init__(self):
        
        self.reading_sb_packets = False
        self.reading_cb_packets = False
        self.print_now = False
        self.read_td = False
        self.packet = {}
        self.state = 0
        self.cb_packets = []
        self.sb_packets = []

        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == 'span':
            if next((x for x in attrs if x[0] == 'id' and x[1] == 'Clientbound_2'), False):
                self.reading_cb_packets = True
            elif next((x for x in attrs if x[0] == 'id' and x[1] == 'Serverbound_2'), False):
                self.reading_sb_packets = True
                self.reading_cb_packets = False
            elif next((x for x in attrs if x[0] == 'id' and x[1] == 'Status'), False):
                self.reading_sb_packets = False
        if self.reading_sb_packets or self.reading_cb_packets:
            if tag == 'h4':
                self.state = 1
                
                if self.reading_cb_packets:
                    if len(self.packet.keys()) > 0:
                        self.cb_packets.append(self.packet)
                else:
                    self.sb_packets.append(self.packet)

                self.packet = {}
            elif tag == 'span':
                if self.state == 1:
                    self.packet['packet_name'] = next(x for x in attrs if x[0] == 'id')[1].replace(' ', '')
                    self.packet['packet_name'] = self.packet['packet_name'].replace('_.28serverbound.29', '')
                    self.packet['packet_name'] = self.packet['packet_name'].replace('_.28clientbound.29', '')
                    self.packet['packet_name'] = self.packet['packet_name'].replace('-', '_')
                    self.state = 2
                    self.state = 2
            elif tag == 'tr':
                if self.state == 2:
                    self.state = 3
                    self.packet['definition'] = []
                
            elif tag == 'td':
                # self.print_now = True
                if self.state == 3:
                    self.state = 4
                elif self.state < 12 and self.state > 3:
                    self.state += 1
                elif self.state == 12:
                    self.state = 8

    def handle_data(self, data):
        if self.state == 4:
            self.packet['id'] = data[:-1]
            self.state = 5
        elif self.state == 8:
            self.field_name = data[1:-1].lower().replace(' ', '_')
            self.state = 9
        elif self.state == 10:
            self.field_value = data[1:-1]
            self.packet['definition'].append((self.field_name , process_field_type(self.field_value)))
            self.state = 11
    def handle_endtag(self, tag):
        if self.state == 12 and tag == 'table':
            self.state = 0

            

fp = urllib.request.urlopen("https://wiki.vg/index.php?title=Protocol&oldid=14204")
response = fp.read()

parser = Parser()
parser.feed(response.decode('utf-8'))

# print(response.decode('utf-8'))
# print(parser.sb_packets)
# print(parser.cb_packets)

with open('__init__(gen_cb).py', 'w') as f:
    f.write('''\
from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias
)    

''')

    for packet in parser.cb_packets:
        f.write('''\
class {}(Packet):
    @staticmethod
    def get_id(context):
        return {}

    packet_name = "{}"
    definition = [         
'''.format(packet['packet_name'], packet['id'], packet['packet_name']))
        for i, field in enumerate(packet['definition']):
            if i < len(packet['definition']) - 1:
                f.write("       {{'{}': {}}},\n".format(field[0], field[1]))
        f.write("       {{'{}': {}}}]\n\n".format(packet['definition'][-1][0], packet['definition'][-1][1]))
    