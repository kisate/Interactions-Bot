from minecraft.networking.packets import (
    Packet, AbstractKeepAlivePacket, AbstractPluginMessagePacket
)

from minecraft.networking.types import (
    Double, Float, Boolean, VarInt, String, Byte, Position, Enum,
    RelativeHand, BlockFace, Vector, Direction, PositionAndLook,
    multi_attribute_alias, UUID, Angle, Short, Integer as Int, Long
)    

class Spawn_Object(Packet):
    @staticmethod
    def get_id(context):
        return  0x00

    packet_name = "Spawn_Object"
    definition = [         
       {'entity_id': VarInt},
       {'object_uuid': UUID},
       {'type': Byte},
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'pitch': Angle},
       {'yaw': Angle},
       {'data': Int},
       {'velocity_x': Short},
       {'velocity_y': Short}]

class Spawn_Experience_Orb(Packet):
    @staticmethod
    def get_id(context):
        return  0x01

    packet_name = "Spawn_Experience_Orb"
    definition = [         
       {'entity_id': VarInt},
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'count': Short}]

class Spawn_Global_Entity(Packet):
    @staticmethod
    def get_id(context):
        return  0x02

    packet_name = "Spawn_Global_Entity"
    definition = [         
       {'entity_id': VarInt},
       {'type': Byte},
       {'x': Double},
       {'y': Double},
       {'z': Double}]

class Spawn_Mob(Packet):
    @staticmethod
    def get_id(context):
        return  0x03

    packet_name = "Spawn_Mob"
    definition = [         
       {'entity_id': VarInt},
       {'entity_uuid': UUID},
       {'type': VarInt},
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'yaw': Angle},
       {'pitch': Angle},
       {'head_pitch': Angle},
       {'velocity_x': Short},
       {'velocity_y': Short},
       {'velocity_z': Short},
       #{'metadata': } TODO
        ]

class Spawn_Painting(Packet):
    @staticmethod
    def get_id(context):
        return  0x04

    packet_name = "Spawn_Painting"
    definition = [         
       {'entity_id': VarInt},
       {'entity_uuid': UUID},
       {'title': String},
       {'location': Position},
       {'direction': Byte}]

class Spawn_Player(Packet):
    @staticmethod
    def get_id(context):
        return  0x05

    packet_name = "Spawn_Player"
    definition = [         
       {'entity_id': VarInt},
       {'player_uuid': UUID},
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'yaw': Angle},
       {'pitch': Angle},
       #{'metadata': } TODO
        ]

class Animation(Packet):
    @staticmethod
    def get_id(context):
        return  0x06

    packet_name = "Animation"
    definition = [         
       {'entity_id': VarInt},
       {'animation': Byte}]

# class Statistics(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x07

#     packet_name = "Statistics"
#     definition = [         
#        {'count': VarInt},
#        {'statistic': Name},
#        {'string_(32767)': },
#        {'varint': The amount to set it to}]

class Block_Break_Animation(Packet):
    @staticmethod
    def get_id(context):
        return  0x08

    packet_name = "Block_Break_Animation"
    definition = [         
       {'entity_id': VarInt},
       {'location': Position},
       {'destroy_stage': Byte}]

# class Update_Block_Entity(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x09

#     packet_name = "Update_Block_Entity"
#     definition = [         
#        {'location': Position},
#        {'action': Byte},
#        {'nbt_data': }]

class Block_Action(Packet):
    @staticmethod
    def get_id(context):
        return  0x0A

    packet_name = "Block_Action"
    definition = [         
       {'location': Position},
       {'action_id_(byte_1)': Byte},
       {'action_param_(byte_2)': Byte},
       {'block_type': VarInt}]

class Block_Change(Packet):
    @staticmethod
    def get_id(context):
        return  0x0B

    packet_name = "Block_Change"
    definition = [         
       {'location': Position},
       {'block_id': VarInt}]

# class Boss_Bar(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x0C

#     packet_name = "Boss_Bar"
#     definition = [         
#        {'uuid': UUID},
#        {'action': VarInt},
#        {'0:_add': Title},
#        {'': Health},
#        {'from_0_to_1._values_greater_than_1_do_not_crash_a_notchian_client,_and_start': Color},
#        {'color_id_(see_below)': Division},
#        {'type_of_division_(see_below)': Flags},
#        {'bit_mask._0x1:_should_darken_sky,_0x2:_is_dragon_bar_(used_to_play_end_music)': 1: remove},
#        {'': Removes this boss bar},
#        {'health': Float},
#        {'3:_update_title': Title},
#        {'': 4: update style},
#        {'varint_enum': Color ID (see below)},
#        {'varint_enum': as above},
#        {'flags': Byte}]

class Server_Difficulty(Packet):
    @staticmethod
    def get_id(context):
        return  0x0D

    packet_name = "Server_Difficulty"
    definition = [         
       {'difficulty': Byte}]

# class Tab_Complete(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x0E

#     packet_name = "Tab_Complete"
#     definition = [         
#        {'count': VarInt},
#        {'matches': Array of String (32767)}]

# class Chat_Message(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x0F

#     packet_name = "Chat_Message"
#     definition = [         
#        {'json_data': },
#        {'position': Byte}]

# class Multi_Block_Change(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x10

#     packet_name = "Multi_Block_Change"
#     definition = [         
#        {'chunk_x': Int},
#        {'chunk_z': Int},
#        {'record_count': VarInt},
#        {'record': Horizontal Position},
#        {'unsigned_byte': The 4 most significant bits },
#        {'unsigned_byte': Y coordinate of the block},
#        {'varint': The new block state ID for the block as given in the}]

class Confirm_Transaction(Packet):
    @staticmethod
    def get_id(context):
        return  0x11

    packet_name = "Confirm_Transaction"
    definition = [         
       {'window_id': Byte},
       {'action_number': Short},
       {'accepted': Boolean}]

class Close_Window(Packet):
    @staticmethod
    def get_id(context):
        return  0x12

    packet_name = "Close_Window"
    definition = [         
       {'window_id': Byte}]

# class Open_Window(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x13

#     packet_name = "Open_Window"
#     definition = [         
#        {'window_id': Byte},
#        {'window_type': String},
#        {'window_title': },
#        {'number_of_slots': Byte},
#        {'entity_id': Optional Int}]

# class Window_Items(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x14

#     packet_name = "Window_Items"
#     definition = [         
#        {'window_id': Byte},
#        {'count': Short},
#        {'slot_data': Array of}]

class Window_Property(Packet):
    @staticmethod
    def get_id(context):
        return  0x15

    packet_name = "Window_Property"
    definition = [         
       {'window_id': Byte},
       {'property': Short},
       {'value': Short}]

# class Set_Slot(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x16

#     packet_name = "Set_Slot"
#     definition = [         
#        {'window_id': Byte},
#        {'slot': Short},
#        {'slot_data': }]

class Set_Cooldown(Packet):
    @staticmethod
    def get_id(context):
        return  0x17

    packet_name = "Set_Cooldown"
    definition = [         
       {'item_id': VarInt},
       {'cooldown_ticks': VarInt}]

# class Plugin_Message(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x18

#     packet_name = "Plugin_Message"
#     definition = [         
#        {'channel': String},
#        {'data': Byte Array}]

class Named_Sound_Effect(Packet):
    @staticmethod
    def get_id(context):
        return  0x19

    packet_name = "Named_Sound_Effect"
    definition = [         
       {'sound_name': String},
       {'sound_category': VarInt},
       {'effect_position_x': Int},
       {'effect_position_y': Int},
       {'effect_position_z': Int},
       {'volume': Float},
       {'pitch': Float}]

# class Disconnect(Packet): TODO
#     @staticmethod
#     def get_id(context):
#         return  0x1A

#     packet_name = "Disconnect_.28play.29"
#     definition = [         
#        {'reason': }]

class Entity_Status(Packet):
    @staticmethod
    def get_id(context):
        return  0x1B

    packet_name = "Entity_Status"
    definition = [         
       {'entity_id': Int},
       {'entity_status': Byte}]

# class Explosion(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x1C

#     packet_name = "Explosion"
#     definition = [         
#        {'x': Float},
#        {'y': Float},
#        {'z': Float},
#        {'radius': Float},
#        {'record_count': Int},
#        {'records': Array of (Byte, Byte, Byte)},
#        {'player_motion_x': Float},
#        {'player_motion_y': Float},
#        {'player_motion_z': Float}]

class Unload_Chunk(Packet):
    @staticmethod
    def get_id(context):
        return  0x1D

    packet_name = "Unload_Chunk"
    definition = [         
       {'chunk_x': Int},
       {'chunk_z': Int}]

class Change_Game_State(Packet):
    @staticmethod
    def get_id(context):
        return  0x1E

    packet_name = "Change_Game_State"
    definition = [         
       {'reason': Byte},
       {'value': Float}]

class Keep_Alive(Packet):
    @staticmethod
    def get_id(context):
        return  0x1F

    packet_name = "Keep_Alive"
    definition = [         
       {'keep_alive_id': Long}]

# class Chunk_Data(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x20

#     packet_name = "Chunk_Data"
#     definition = [         
#        {'chunk_x': Int},
#        {'chunk_z': Int},
#        {'ground-up_continuous': Boolean},
#        {'primary_bit_mask': VarInt},
#        {'size': VarInt},
#        {'data': Byte array},
#        {'number_of_block_entities': VarInt},
#        {'block_entities': Array of}]

class Effect(Packet):
    @staticmethod
    def get_id(context):
        return  0x21

    packet_name = "Effect"
    definition = [         
       {'effect_id': Int},
       {'location': Position},
       {'data': Int},
       {'disable_relative_volume': Boolean}]

# class Particle_2(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x22

#     packet_name = "Particle_2"
#     definition = [         
#        {'particle_id': Int},
#        {'long_distance': Boolean},
#        {'x': Float},
#        {'y': Float},
#        {'z': Float},
#        {'offset_x': Float},
#        {'offset_y': Float},
#        {'offset_z': Float},
#        {'particle_data': Float},
#        {'particle_count': Int},
#        {'data': Array of VarInt}]

class JoinGamePacket(Packet):
    @staticmethod
    def get_id(context):
        return  0x23

    packet_name = "join_game"
    definition = [         
       {'entity_id': Int},
       {'gamemode': Byte},
       {'dimension': Int},
       {'difficulty': Byte},
       {'max_players': Byte},
       {'level_type': String},
       {'reduced_debug_info': Boolean}]

# class Map(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x24

#     packet_name = "Map"
#     definition = [         
#        {'item_damage': VarInt},
#        {'scale': Byte},
#        {'tracking_position': Boolean},
#        {'icon_count': VarInt},
#        {'icon': Direction And Type},
#        {'byte': 0xF0 = Type, 0x0F = Direction},
#        {'byte': },
#        {'byte': },
#        {'byte': Number of columns updated},
#        {'optional_byte': Only if Columns is more than 0; number of rows updated},
#        {'optional_byte': Only if Columns is more than 0; x offset of the westernmost column},
#        {'optional_byte': Only if Columns is more than 0; z offset of the northernmost row},
#        {'optional_varint': Only if Columns is more than 0; length of the following array},
#        {'optional_array_of_unsigned_byte': Only if Columns is more than 0; see},
#        {'white_arrow_(players)': 1},
#        {'2': Red arrow},
#        {'blue_arrow': 4},
#        {'5': Red pointer},
#        {'white_circle_(off-map_players)': 7},
#        {'8': Mansion},
#        {'temple': 10-15}]

class Entity(Packet):
    @staticmethod
    def get_id(context):
        return  0x25

    packet_name = "Entity"
    definition = [         
       {'entity_id': VarInt}]

class Entity_Relative_Move(Packet):
    @staticmethod
    def get_id(context):
        return  0x26

    packet_name = "Entity_Relative_Move"
    definition = [         
       {'entity_id': VarInt},
       {'delta_x': Short},
       {'delta_y': Short},
       {'delta_z': Short},
       {'on_ground': Boolean}]

class Entity_Look_And_Relative_Move(Packet):
    @staticmethod
    def get_id(context):
        return  0x27

    packet_name = "Entity_Look_And_Relative_Move"
    definition = [         
       {'entity_id': VarInt},
       {'delta_x': Short},
       {'delta_y': Short},
       {'delta_z': Short},
       {'yaw': Angle},
       {'pitch': Angle},
       {'on_ground': Boolean}]

class Entity_Look(Packet):
    @staticmethod
    def get_id(context):
        return  0x28

    packet_name = "Entity_Look"
    definition = [         
       {'entity_id': VarInt},
       {'yaw': Angle},
       {'pitch': Angle},
       {'on_ground': Boolean}]

class Vehicle_Move(Packet):
    @staticmethod
    def get_id(context):
        return  0x29

    packet_name = "Vehicle_Move"
    definition = [         
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'yaw': Float},
       {'pitch': Float}]

class Open_Sign_Editor(Packet):
    @staticmethod
    def get_id(context):
        return  0x2A

    packet_name = "Open_Sign_Editor"
    definition = [         
       {'location': Position}]

class Craft_Recipe_Response(Packet):
    @staticmethod
    def get_id(context):
        return  0x2B

    packet_name = "Craft_Recipe_Response"
    definition = [         
       {'window_id': Byte},
       {'recipe': VarInt}]

class Player_Abilities(Packet):
    @staticmethod
    def get_id(context):
        return  0x2C

    packet_name = "Player_Abilities"
    definition = [         
       {'flags': Byte},
       {'flying_speed': Float},
       {'field_of_view_modifier': Float}]

# class Combat_Event(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x2D

#     packet_name = "Combat_Event"
#     definition = [         
#        {'event': VarInt},
#        {'0:_enter_combat': },
#        {'': 1: end combat},
#        {'varint': },
#        {'int': },
#        {'player_id': VarInt},
#        {'entity_id': Int},
#        {'message': }]

# class Player_List_Item(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x2E

#     packet_name = "Player_List_Item"
#     definition = [         
#        {'action': VarInt},
#        {'number_of_players': VarInt},
#        {'player': UUID},
#        {'uuid': },
#        {'name': String},
#        {'number_of_properties': VarInt},
#        {'property': Name},
#        {'string_(32767)': },
#        {'string_(32767)': },
#        {'boolean': },
#        {'optional_string_(32767)': Only if Is Signed is true},
#        {'varint': },
#        {'varint': Measured in milliseconds},
#        {'boolean': },
#        {'optional': Only if Has Display Name is true},
#        {'gamemode': VarInt},
#        {'2:_update_latency': Ping},
#        {'measured_in_milliseconds': 3: update display name},
#        {'boolean': },
#        {'optional': Only send if Has Display Name is true},
#        {'': }]

class Player_Position_And_Look(Packet):
    @staticmethod
    def get_id(context):
        return  0x2F

    packet_name = "Player_Position_And_Look"
    definition = [         
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'yaw': Float},
       {'pitch': Float},
       {'flags': Byte},
       {'teleport_id': VarInt}]

class Use_Bed(Packet):
    @staticmethod
    def get_id(context):
        return  0x30

    packet_name = "Use_Bed"
    definition = [         
       {'entity_id': VarInt},
       {'location': Position}]

# class Unlock_Recipes(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x31

#     packet_name = "Unlock_Recipes"
#     definition = [         
#        {'action': VarInt},
#        {'crafting_book_open': Boolean},
#        {'filtering_craftable': Boolean},
#        {'array_size_1': VarInt},
#        {'recipe_ids': Array of VarInt},
#        {'array_size_2': Optional VarInt},
#        {'recipe_ids': Optional Array of VarInt, only present if mode is 0 (init)}]

# class Destroy_Entities(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x32

#     packet_name = "Destroy_Entities"
#     definition = [         
#        {'count': VarInt},
#        {'entity_ids': Array of VarInt}]

class Remove_Entity_Effect(Packet):
    @staticmethod
    def get_id(context):
        return  0x33

    packet_name = "Remove_Entity_Effect"
    definition = [         
       {'entity_id': VarInt},
       {'effect_id': Byte}]

class Resource_Pack_Send(Packet):
    @staticmethod
    def get_id(context):
        return  0x34

    packet_name = "Resource_Pack_Send"
    definition = [         
       {'url': String},
       {'hash': String}]

class Respawn(Packet):
    @staticmethod
    def get_id(context):
        return  0x35

    packet_name = "Respawn"
    definition = [         
       {'dimension': Int},
       {'difficulty': Byte},
       {'gamemode': Byte},
       {'level_type': String}]

class Entity_Head_Look(Packet):
    @staticmethod
    def get_id(context):
        return  0x36

    packet_name = "Entity_Head_Look"
    definition = [         
       {'entity_id': VarInt},
       {'head_yaw': Angle}]

class Select_Advancement_Tab(Packet):
    @staticmethod
    def get_id(context):
        return  0x37

    packet_name = "Select_Advancement_Tab"
    definition = [         
       {'has_id': Boolean},
       {'optional_identifier': String}]

# class World_Border(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x38

#     packet_name = "World_Border"
#     definition = [         
#        {'action': VarInt},
#        {'0:_set_size': Diameter},
#        {'length_of_a_single_side_of_the_world_border,_in_meters': 1: lerp size},
#        {'double': Current length of a single side of the world border, in meters},
#        {'double': Target length of a single side of the world border, in meters},
#        {'varlong': Number of real-time},
#        {'x': Double},
#        {'z': Double},
#        {'3:_initialize': X},
#        {'': Z},
#        {'': Old Diameter},
#        {'current_length_of_a_single_side_of_the_world_border,_in_meters': New Diameter},
#        {'target_length_of_a_single_side_of_the_world_border,_in_meters': Speed},
#        {'number_of_real-time': Portal Teleport Boundary},
#        {'resulting_coordinates_from_a_portal_teleport_are_limited_to_±value._usually_29999984.': Warning Time},
#        {'in_seconds_as_set_by': Warning Blocks},
#        {'in_meters': 4: set warning time},
#        {'varint': In seconds as set by},
#        {'warning_blocks': VarInt}]

class Camera(Packet):
    @staticmethod
    def get_id(context):
        return  0x39

    packet_name = "Camera"
    definition = [         
       {'camera_id': VarInt}]

class Held_Item_Change(Packet):
    @staticmethod
    def get_id(context):
        return  0x3A

    packet_name = "Held_Item_Change"
    definition = [         
       {'slot': Byte}]

class Display_Scoreboard(Packet):
    @staticmethod
    def get_id(context):
        return  0x3B

    packet_name = "Display_Scoreboard"
    definition = [         
       {'position': Byte},
       {'score_name': String}]

# class Entity_Metadata(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x3C

#     packet_name = "Entity_Metadata"
#     definition = [         
#        {'entity_id': VarInt},
#        {'metadata': }]

class Attach_Entity(Packet):
    @staticmethod
    def get_id(context):
        return  0x3D

    packet_name = "Attach_Entity"
    definition = [         
       {'attached_entity_id': Int},
       {'holding_entity_id': Int}]

class Entity_Velocity(Packet):
    @staticmethod
    def get_id(context):
        return  0x3E

    packet_name = "Entity_Velocity"
    definition = [         
       {'entity_id': VarInt},
       {'velocity_x': Short},
       {'velocity_y': Short},
       {'velocity_z': Short}]

# class Entity_Equipment(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x3F

#     packet_name = "Entity_Equipment"
#     definition = [         
#        {'entity_id': VarInt},
#        {'slot': VarInt},
#        {'item': }]

class Set_Experience(Packet):
    @staticmethod
    def get_id(context):
        return  0x40

    packet_name = "Set_Experience"
    definition = [         
       {'experience_bar': Float},
       {'level': VarInt},
       {'total_experience': VarInt}]

class Update_Health(Packet):
    @staticmethod
    def get_id(context):
        return  0x41

    packet_name = "Update_Health"
    definition = [         
       {'health': Float},
       {'food': VarInt},
       {'food_saturation': Float}]

# class Scoreboard_Objective(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x42

#     packet_name = "Scoreboard_Objective"
#     definition = [         
#        {'objective_name': String},
#        {'mode': Byte},
#        {'objective_value': Optional String (32)},
#        {'type': Optional String (16)}]

# class Set_Passengers(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x43

#     packet_name = "Set_Passengers"
#     definition = [         
#        {'entity_id': VarInt},
#        {'passenger_count': VarInt},
#        {'passengers': Array of VarInt}]

# class Teams(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x44

#     packet_name = "Teams"
#     definition = [         
#        {'team_name': String},
#        {'mode': Byte},
#        {'0:_create_team': Team Display Name},
#        {'': Team Prefix},
#        {'displayed_before_the_names_of_players_that_are_part_of_this_team': Team Suffix},
#        {'displayed_after_the_names_of_players_that_are_part_of_this_team': Friendly Flags},
#        {'bit_mask._0x01:_allow_friendly_fire,_0x02:_can_see_invisible_players_on_same_team': Name Tag Visibility},
#        {'': Collision Rule},
#        {'': Color},
#        {'for_colors,_the_same': Entity Count},
#        {'number_of_elements_in_the_following_array': Entities},
#        {'identifiers_for_the_entities_in_this_team.__for_players,_this_is_their_username;_for_other_entities,_it_is_their_uuid.': 1: remove team},
#        {'': },
#        {'team_display_name': String},
#        {'team_prefix': String},
#        {'team_suffix': String},
#        {'friendly_flags': Byte},
#        {'name_tag_visibility': String},
#        {'collision_rule': String},
#        {'color': Byte},
#        {'3:_add_players_to_team': Entity Count},
#        {'number_of_elements_in_the_following_array': Entities},
#        {'identifiers_for_the_entities_added.__for_players,_this_is_their_username;_for_other_entities,_it_is_their_uuid.': 4: remove players from team},
#        {'varint': Number of elements in the following array},
#        {'array_of_string_(40)': Identifiers for the entities removed.  For players, this is their username; for other entities, it is their UUID.}]

# class Update_Score(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x45

#     packet_name = "Update_Score"
#     definition = [         
#        {'entity_name': String},
#        {'action': Byte},
#        {'objective_name': String},
#        {'value': Optional VarInt}]

class Spawn_Position(Packet):
    @staticmethod
    def get_id(context):
        return  0x46

    packet_name = "Spawn_Position"
    definition = [         
       {'location': Position}]

class Time_Update(Packet):
    @staticmethod
    def get_id(context):
        return  0x47

    packet_name = "Time_Update"
    definition = [         
       {'world_age': Long},
       {'time_of_day': Long}]

# class Title(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x48

#     packet_name = "Title"
#     definition = [         
#        {'action': VarInt},
#        {'0:_set_title': Title Text},
#        {'': 1: set subtitle},
#        {'': },
#        {'action_bar_text': },
#        {'3:_set_times_and_display': Fade In},
#        {'ticks_to_spend_fading_in': Stay},
#        {'ticks_to_keep_the_title_displayed': Fade Out},
#        {'ticks_to_spend_out,_not_when_to_start_fading_out': 4: hide},
#        {'': },
#        {'': }]

class Sound_Effect(Packet):
    @staticmethod
    def get_id(context):
        return  0x49

    packet_name = "Sound_Effect"
    definition = [         
       {'sound_id': VarInt},
       {'sound_category': VarInt},
       {'effect_position_x': Int},
       {'effect_position_y': Int},
       {'effect_position_z': Int},
       {'volume': Float},
       {'pitch': Float}]

# class Player_List_Header_And_Footer(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x4A

#     packet_name = "Player_List_Header_And_Footer"
#     definition = [         
#        {'header': },
#        {'footer': }]

class Collect_Item(Packet):
    @staticmethod
    def get_id(context):
        return  0x4B

    packet_name = "Collect_Item"
    definition = [         
       {'collected_entity_id': VarInt},
       {'collector_entity_id': VarInt},
       {'pickup_item_count': VarInt}]

class Entity_Teleport(Packet):
    @staticmethod
    def get_id(context):
        return  0x4C

    packet_name = "Entity_Teleport"
    definition = [         
       {'entity_id': VarInt},
       {'x': Double},
       {'y': Double},
       {'z': Double},
       {'yaw': Angle},
       {'pitch': Angle},
       {'on_ground': Boolean}]

# class Advancements(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x4D

#     packet_name = "Advancements"
#     definition = [         
#        {'reset/clear': Boolean},
#        {'mapping_size': VarInt},
#        {'advancement_mapping': Key},
#        {'identifier': The identifier of the advancement},
#        {'advancement': See below},
#        {'varint': Size of the following array},
#        {'array_of_identifier': The identifiers of the advancements that should be removed},
#        {'varint': Size of the following array},
#        {'key': Array},
#        {'the_identifier_of_the_advancement': Value},
#        {'see_below': Has parent},
#        {'indicates_whether_the_next_field_exists.': Parent id},
#        {'the_identifier_of_the_parent_advancement.': Has display},
#        {'indicates_whether_the_next_field_exists': Display data},
#        {'see_below.': Number of criteria},
#        {'size_of_the_following_array': Criteria},
#        {'array': Identifier},
#        {'value': },
#        {'array_length': VarInt},
#        {'requirements': Array length 2},
#        {'varint': Number of elements in the following array},
#        {'array_of_string': Array of required criteria},
#        {'chat': },
#        {'chat': },
#        {'': },
#        {'varint_enum': 0 =},
#        {'integer': 0x1: has background texture; 0x2:},
#        {'optional_identifier': Background texture location.  Only if flags indicates it.},
#        {'float': },
#        {'float': },
#        {'varint': Size of the following array},
#        {'criterion_identifier': Array},
#        {'the_identifier_of_the_criterion.': Criterion progress},
#        {'': Achieved},
#        {'if_true,_next_field_is_present': Date of achieving}]

# class Entity_Properties(Packet):
#     @staticmethod
#     def get_id(context):
#         return  0x4E

#     packet_name = "Entity_Properties"
#     definition = [         
#        {'entity_id': VarInt},
#        {'number_of_properties': Int},
#        {'property': Key},
#        {'string_(64)': See below},
#        {'double': See below},
#        {'varint': Number of elements in the following array},
#        {'array_of_modifier_data': See},
#        {'20.0': 0.0},
#        {'max_health': generic.followRange},
#        {'0.0': 2048.0},
#        {'generic.knockbackresistance': 0.0},
#        {'1.0': Knockback Resistance},
#        {'0.699999988079071': 0.0},
#        {'movement_speed': generic.attackDamage},
#        {'0.0': 2048.0},
#        {'generic.attackspeed': 4.0},
#        {'1024.0': Attack Speed},
#        {'0.4000000059604645': 0.0},
#        {'flying_speed': horse.jumpStrength},
#        {'0.0': 2.0},
#        {'zombie.spawnreinforcements': 0.0},
#        {'1.0': Spawn Reinforcements Chance},
#        {'5.0': 0.0},
#        {'player_reach_distance_(forge_only)': forge.swimSpeed},
#        {'0.0': 1024.0}]

