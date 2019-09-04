import inspect
import math
import re

from exceptions import TooManyArgumentsException
from bot.threads import MovingThread, MoveToAndMineThread, MultiMiningThread, ItemSwapThread, Thread, FollowingThread, GetToChunkThread
# from bot import command, commands, use_json, use_json_data
from minecraft.networking.packets import serverbound
from minecraft.networking.types import Position


commands = {}
use_json_data = []

def command(func):
    '''
    decorator for saving functions into commands set
    '''
    commands[func.__name__] = func
    return func

def use_json(func):
    '''
    decorator for saving functions that use json data
    '''
    use_json_data.append(func)
    return func

def parse_message(bot, message, json_data):
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
            func(bot, *args)
        else:
            raise mydong
    else:
        func(bot, *args, kwargs)


@command
def goto(bot, x: int, y: int, z: int, kwargs):
    bot.break_event.clear()
    kwargs['start'] = bot.get_int_position()
    kwargs['end'] = (x, y, z)

    if (True):
        thread = MovingThread('moving', bot, kwargs)
        thread.start()
    else:
        bot.say('Target is not passable or block under is passable', 2)


@command
def mine(bot, x: int, y: int, z: int, kwargs):
    bot.break_event.clear()
    kwargs['start'] = bot.get_int_position()
    kwargs['end'] = (x, y, z)

    if (bot.world.get_block(*kwargs['end']) > 0):
        thread = MoveToAndMineThread('move to and mine', bot, kwargs)
        thread.start()
    else:
        bot.say('Block is air')


@command
def c_level(bot, level: int):
    bot.chat_level = level
    bot.say('Chat level is now {}'.format(bot.chat_level), 3)


@command
def mineall(bot, block_id: int):
    bot.break_event.clear()
    bot.break_event_multi.clear()
    args = {}

    blocks = []

    chunk_x, chunk_z = bot.world.get_chunk_coords(
        bot.get_int_position()[0], bot.get_int_position()[2])
    chunk = bot.world.get_chunk_by_chunk_coords(chunk_x, chunk_z)
    bot.say('Searching {} for {}'.format((chunk_x, chunk_z), block_id))

    for x in range(16):
        for y in range(256):
            for z in range(16):
                if chunk.get_block(x, y, z, True) == block_id:
                    blocks.append([x + chunk_x*16, y, z + chunk_z*16])

    bot.say('Found {} blocks'.format(len(blocks)))

    thread = MultiMiningThread('multimining', bot, blocks, args)
    thread.start()

@command
def stop(bot):
    bot.break_event.set()
    bot.break_event_multi.set()

@command
def lst(bot):
    print(bot.inventory)

@command
def swap(bot, slot1: int, slot2: int):
    thread = ItemSwapThread('item swap', bot, slot1, slot2)
    thread.start()

@command
def hold(bot, slot: int):
    bot.hold(slot)

@command
def setup(bot):
    thread = Thread(target=bot.set_up_tools)
    thread.start()

@command
def minechunk(bot, kwargs):
    bot.break_event.clear()
    bot.break_event_multi.clear()

    blocks = []

    chunk_x, chunk_z = bot.world.get_chunk_coords(bot.get_int_position()[0], bot.get_int_position()[2])
    chunk = bot.world.get_chunk_by_chunk_coords(chunk_x, chunk_z)

    for x in range(16):
        for y in range(256):
            for z in range(16):
                block = chunk.get_block(x, y, z, True)
                if block != 0 and bot.world.info['blocks']['tool'][str(block)] >= 0:
                    blocks.append([x + chunk_x*16, y, z + chunk_z*16])
    
    bot.say('Found {} blocks'.format(len(blocks)))

    thread = MultiMiningThread('multimining', bot, blocks, kwargs)
    thread.start()

@command
def minerect(bot, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, kwargs):
    p1, p2 = [x1, y1, z1], [x2, y2, z2]
    p1, p2 = [min(p1[i], p2[i]) for i in range(3)], [max(p1[i], p2[i]) for i in range(3)]

    blocks = []

    for x in range(p1[0], p2[0]):
        for y in range(p1[1], p2[1]):
            for z in range(p1[2], p2[2]):
                
                blocks.append([x, y, z])

    bot.say('Found {} blocks'.format(len(blocks)))

    thread = MultiMiningThread('multimining', bot, blocks, kwargs)
    thread.start()

@command
def respawn(bot):
    packet = serverbound.play.ClientStatusPacket()
    packet.action_id = serverbound.play.ClientStatusPacket.RESPAWN
    bot.connection.write_packet(packet)

@command
def place(bot, x: int, y: int, z: int):
    location = [x, y, z]
    face = 1
    hand = 0
    cursor_x = 0
    cursor_y = 0
    cursor_z = 0

    bot.hold(0)
    packet = serverbound.PlayerBlockPlacementPacket()
    packet.location = Position(x=location[0], y=location[1], z=location[2])
    packet.face = face
    packet.hand = hand
    packet.cursor_x = cursor_x
    packet.cursor_y = cursor_y
    packet.cursor_z = cursor_z
    bot.connection.write_packet(packet)

@command
@use_json
def tome(bot, player_id, kwargs):
    entity_id = bot.player_UUIDs[player_id]
    kwargs['start'] = bot.get_int_position()
    kwargs['end'] = [math.floor(x) for x in bot.entity_coords[entity_id]]
    thread = MovingThread('ZALUPA', bot, kwargs)
    thread.start()

@command
@use_json
def followme(bot, player_id):
    entity_id = bot.player_UUIDs[player_id]
    args = {}
    thread = FollowingThread('follow', bot, args, entity_id)
    thread.start()

@command
def tochunk(bot, x: int, z: int):
    target = [x, z]
    thread = GetToChunkThread('get to chunk', bot, {}, target)
    thread.start()


# parse_message(None, '!bot mineall 16'.split())
