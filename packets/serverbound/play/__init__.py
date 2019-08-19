from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias, Slot, UnsignedByte, Short
)

class DiggingPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x14

    packet_name = "digging"
    definition = [
        {'status': VarInt},
        {'location' : Position},
        {'face': Byte}]

class ClickWindowPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x07
    packet_name = 'click window'

    definition = [
        {'window_id' : UnsignedByte},
        {'slot' : Short},
        {'button' : Byte},
        {'action_number' : Short},
        {'mode' : VarInt},
        {'clicked_item' : Slot}
    ]   

class ConfirmTransactionPacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x05

    packet_name = 'confirm transaction sb'
    definition = [
        {'window_id' : Byte},
        {'action_number' : Short},
        {'accepted' : Boolean}
    ]

class HeldItemChangePacket(Packet):
    @staticmethod
    def get_id(context):
        return 0x1A
    
    packet_name = 'held item change sb'
    definition = [
        {'slot' : Short}
    ]