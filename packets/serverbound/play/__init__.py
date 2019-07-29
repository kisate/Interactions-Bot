from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias
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