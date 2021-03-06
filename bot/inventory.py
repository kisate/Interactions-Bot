from minecraft.networking.packets.clientbound.play.inventory_packets import Slot
import numpy

class Inventory():
    def __init__(self, size=46):
        self.slots = numpy.full([size], Slot(-1)).tolist()
        self.action_number = 1
    
    def get_slot_index_by_id(self, id):
        for i, slot in enumerate(self.slots):
            if slot.item_id == id:
                return i
        return -1

    def get_slot_by_id(self, id):
        for slot in self.slots:
            if id == slot.item_id:
                return slot
        return Slot(-1)

    def get_slots_by_id(self, id):
        slots = []
        for slot in self.slots:
            if slot.item_id == id:
                slots.append(slot)
        return slots

    def get_slot_index_by_slot(self, slot : Slot):
        for i, x in enumerate(self.slots):
            if x == slot:
                return i
        return Slot(-1)

    def __setitem__(self, key, value : Slot):
        if value.item_id == -1:
            self.slots[key] = Slot(-1)
        else:
            self.slots[key] = value

    def __getitem__(self, key):
        return self.slots[key]

    def __repr__(self):
        return "Slots : {}, action number : {}".format(list(enumerate(self.slots)), self.action_number)