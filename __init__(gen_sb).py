from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias
)    

class Entity_Effect(Packet):
    @staticmethod
    def get_id(context):
        return  0x4F

    packet_name = "Entity_Effect"
    definition = [         
       {'entity_id': VarInt},
       {'effect_id': Byte},
       {'amplifier': Byte},
       {'duration': VarInt},
       {'flags': Byte}]

class Teleport_Confirm(Packet):
    @staticmethod
    def get_id(context):
        return  0x00

    packet_name = "Teleport_Confirm"
    definition = [         
       {'teleport_id': VarInt}]

class Tab_Complete(Packet):
    @staticmethod
    def get_id(context):
        return  0x01

    packet_name = "Tab_Complete"
    definition = [         
       {'text': String},
       {'assume_command': Boolean},
       {'has_position': Boolean},
       {'looked_at_block': Optional Position}]

class Chat_Message(Packet):
    @staticmethod
    def get_id(context):
        return  0x02

    packet_name = "Chat_Message"
    definition = [         
       {'message': String}]

class Client_Status(Packet):
    @staticmethod
    def get_id(context):
        return  0x03

    packet_name = "Client_Status"
    definition = [         
       {'action_id': VarInt}]

class Client_Settings(Packet):
    @staticmethod
    def get_id(context):
        return  0x04

    packet_name = "Client_Settings"
    definition = [         
       {'locale': String},
       {'view_distance': Byte},
       {'chat_mode': VarInt},
       {'chat_colors': Boolean},
       {'displayed_skin_parts': Unsigned Byte},
       {'main_hand': VarInt}]

class Confirm_Transaction(Packet):
    @staticmethod
    def get_id(context):
        return  0x05

    packet_name = "Confirm_Transaction"
    definition = [         
       {'window_id': Byte},
       {'action_number': Short},
       {'accepted': Boolean}]

class Enchant_Item(Packet):
    @staticmethod
    def get_id(context):
        return  0x06

    packet_name = "Enchant_Item"
    definition = [         
       {'window_id': Byte},
       {'enchantment': Byte}]

class Click_Window(Packet):
    @staticmethod
    def get_id(context):
        return  0x07

    packet_name = "Click_Window"
    definition = [         
       {'window_id': Unsigned Byte},
       {'slot': Short},
       {'button': Byte},
       {'action_number': Short},
       {'mode': VarInt},
       {'clicked_item': }]

class Close_Window(Packet):
    @staticmethod
    def get_id(context):
        return  0x08

    packet_name = "Close_Window"
    definition = [         
       {'window_id': Unsigned Byte}]

class Plugin_Message(Packet):
    @staticmethod
    def get_id(context):
        return  0x09

    packet_name = "Plugin_Message"
    definition = [         
       {'channel': String},
       {'data': Byte Array}]

class Use_Entity(Packet):
    @staticmethod
    def get_id(context):
        return  0x0A

    packet_name = "Use_Entity"
    definition = [         
       {'target': VarInt},
       {'type': VarInt},
       {'target_x': Optional Float},
       {'target_y': Optional Float},
       {'target_z': Optional Float},
       {'hand': Optional VarInt}]

class Keep_Alive(Packet):
    @staticmethod
    def get_id(context):
        return  0x0B

    packet_name = "Keep_Alive"
    definition = [         
       {'keep_alive_id': Long}]

class Player(Packet):
    @staticmethod
    def get_id(context):
        return  0x0C

    packet_name = "Player"
    definition = [         
       {'on_ground': Boolean}]

class Player_Position(Packet):
    @staticmethod
    def get_id(context):
        return  0x0D

    packet_name = "Player_Position"
    definition = [         
       {'x': Double},
       {'feet_y': Double},
       {'z': Double},
       {'on_ground': Boolean}]

class Player_Position_And_Look(Packet):
    @staticmethod
    def get_id(context):
        return  0x0E

    packet_name = "Player_Position_And_Look"
    definition = [         
       {'x': Double},
       {'feet_y': Double},
       {'z': Double},
       {'yaw': Float},
       {'pitch': Float},
       {'on_ground': Boolean}]

class Player_Look(Packet):
    @staticmethod
    def get_id(context):
        return  0x0F

    packet_name = "Player_Look"
    definition = [         
       {'yaw': Float},
       {'pitch': Float},
       {'on_ground': Boolean}]

class Vehicle_Move(Packet):
    @staticmethod
    def get_id(context):
        return  0x10

    packet_name = "Vehicle_Move"
    definition = [         
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'yaw': Float},
       {'pitch': Float}]

class Steer_Boat(Packet):
    @staticmethod
    def get_id(context):
        return  0x11

    packet_name = "Steer_Boat"
    definition = [         
       {'right_paddle_turning': Boolean},
       {'left_paddle_turning': Boolean}]

class Craft_Recipe_Request(Packet):
    @staticmethod
    def get_id(context):
        return  0x12

    packet_name = "Craft_Recipe_Request"
    definition = [         
       {'window_id': Byte},
       {'recipe': VarInt},
       {'make_all': Boolean}]

class Player_Abilities(Packet):
    @staticmethod
    def get_id(context):
        return  0x13

    packet_name = "Player_Abilities"
    definition = [         
       {'flags': Byte},
       {'flying_speed': Float},
       {'walking_speed': Float}]

class Player_Digging(Packet):
    @staticmethod
    def get_id(context):
        return  0x14

    packet_name = "Player_Digging"
    definition = [         
       {'status': VarInt},
       {'location': Position},
       {'face': Byte}]

class Entity_Action(Packet):
    @staticmethod
    def get_id(context):
        return  0x15

    packet_name = "Entity_Action"
    definition = [         
       {'entity_id': VarInt},
       {'action_id': VarInt},
       {'jump_boost': VarInt}]

class Steer_Vehicle(Packet):
    @staticmethod
    def get_id(context):
        return  0x16

    packet_name = "Steer_Vehicle"
    definition = [         
       {'sideways': Float},
       {'forward': Float},
       {'flags': Unsigned Byte}]

class Crafting_Book_Data(Packet):
    @staticmethod
    def get_id(context):
        return  0x17

    packet_name = "Crafting_Book_Data"
    definition = [         
       {'type': VarInt},
       {'0:_displayed_recipe': Recipe ID},
       {'the_internal_id_of_the_displayed_recipe.': 1: Crafting Book Status},
       {'boolean': Whether the player has the crafting book currently opened/active.},
       {'boolean': Whether the player has the crafting filter option currently active.}]

class Resource_Pack_Status(Packet):
    @staticmethod
    def get_id(context):
        return  0x18

    packet_name = "Resource_Pack_Status"
    definition = [         
       {'result': VarInt}]

class Advancement_Tab(Packet):
    @staticmethod
    def get_id(context):
        return  0x19

    packet_name = "Advancement_Tab"
    definition = [         
       {'action': VarInt},
       {'tab_id': Optional identifier}]

class Held_Item_Change(Packet):
    @staticmethod
    def get_id(context):
        return  0x1A

    packet_name = "Held_Item_Change"
    definition = [         
       {'slot': Short}]

class Creative_Inventory_Action(Packet):
    @staticmethod
    def get_id(context):
        return  0x1B

    packet_name = "Creative_Inventory_Action"
    definition = [         
       {'slot': Short},
       {'clicked_item': }]

class Update_Sign(Packet):
    @staticmethod
    def get_id(context):
        return  0x1C

    packet_name = "Update_Sign"
    definition = [         
       {'location': Position},
       {'line_1': String},
       {'line_2': String},
       {'line_3': String},
       {'line_4': String}]

class Animation(Packet):
    @staticmethod
    def get_id(context):
        return  0x1D

    packet_name = "Animation"
    definition = [         
       {'hand': VarInt}]

class Spectate(Packet):
    @staticmethod
    def get_id(context):
        return  0x1E

    packet_name = "Spectate"
    definition = [         
       {'target_player': UUID}]

class Player_Block_Placement(Packet):
    @staticmethod
    def get_id(context):
        return  0x1F

    packet_name = "Player_Block_Placement"
    definition = [         
       {'location': Position},
       {'face': VarInt},
       {'hand': VarInt},
       {'cursor_position_x': Float},
       {'cursor_position_y': Float},
       {'cursor_position_z': Float}]

