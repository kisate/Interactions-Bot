from heapq import heappush, heappop
from math import ceil
import numpy as np

class Algorithm():
    @staticmethod
    def walk_priority(world, current, target, end, start, traveled_distance, step_length, max_distance, pivot):
        blocks = [world.get_block(*np.sum([current, [0, i, 0]], axis=0)) for i in range(-1, 2)]

        if not (blocks[1] in world.info['blocks']['passable']
            and blocks[2] in world.info['blocks']['passable']
                and not (blocks[0] in world.info['blocks']['passable'] 
                    and world.get_block(*np.sum([target, [0, -1, 0]], axis=0)) in world.info['blocks']['passable'])):    
            return -1

        if (blocks[0] in world.info['blocks']['damaging'] 
            or blocks[1] in world.info['blocks']['damaging'] 
            or blocks[2] in world.info['blocks']['damaging']):

            return -1 

        distance_to_travel = np.linalg.norm(np.array(current)-np.array(target))
        if distance_to_travel <= step_length or (current[1] != target[1] and distance_to_travel <= step_length*2 and distance_to_travel <= 9):
            distance_to_end = np.linalg.norm(np.array(np.sum([current, pivot], axis=0))-np.array(end))
            if distance_to_end <= max_distance:
                priority = [traveled_distance + distance_to_travel + distance_to_end, traveled_distance + distance_to_travel]
                return priority
        
        return -1

    @staticmethod
    def walk_and_mine_priority(world, current, target, end, start, traveled_distance, step_length, max_distance, pivot):

        blocks = [world.get_block(*np.sum([current, [0, i, 0]], axis=0)) for i in range(-1, 2)]

        if not (blocks[1] not in world.info['blocks']['unbreakable']
            and blocks[2] not in world.info['blocks']['unbreakable']
                and not (blocks[0] in world.info['blocks']['passable'] 
                    and world.get_block(*np.sum([target, [0, -1, 0]], axis=0)) in world.info['blocks']['passable']
                    and (blocks[0] not in world.info['blocks']['passable']
                    or blocks[1] not in world.info['blocks']['passable']))):
                
            return -1
        
        if (blocks[0] in world.info['blocks']['damaging'] 
            or blocks[1] in world.info['blocks']['damaging'] 
            or blocks[2] in world.info['blocks']['damaging']):

            return -1 

        distance_to_travel = np.linalg.norm(np.array(current)-np.array(target))
        if distance_to_travel <= step_length:
            distance_to_end = np.linalg.norm(np.array(np.sum([current, pivot], axis=0))-np.array(end))
            if distance_to_end <= max_distance:
                priority = [traveled_distance + distance_to_travel + distance_to_end, traveled_distance + distance_to_travel]

                if world.get_block(*np.sum([current, [0, 0, 0]], axis=0)) not in world.info['blocks']['passable']:
                    priority[0] += 0.5
                    # priority[1] += 1
                if world.get_block(*np.sum([current, [0, 1, 0]], axis=0)) not in world.info['blocks']['passable']:
                    priority[0] += 0.5
                    # priority[1] += 1

                return priority

        return -1

    @staticmethod
    def get_actions(world, target):
        actions = []
        if world.get_block(*target) not in world.info['blocks']['passable']:
            actions.append(2)
        if world.get_block(*np.sum([target, [0, 1, 0]], axis=0)) not in world.info['blocks']['passable']:
            actions.append(3)
        actions.append(0)

        return actions

    @staticmethod
    def expand(world, visited, heap, target, start, end, traveled_distance, step_length, max_distance, pivot, priority_function='wp'):
        priority_function = Algorithm.get_method_from_dict(priority_function)
        step_length_int = ceil(step_length)
        for x in range(target[0] - step_length_int, target[0] + step_length_int + 1):
            for y in range(target[1] - step_length_int, target[1] + step_length_int + 1):
                for z in range(target[2] - step_length_int, target[2] + step_length_int + 1):
                    priority = priority_function(world, [x, y, z], target, end, start, traveled_distance, step_length, max_distance, pivot)
                    if priority != -1 and Algorithm.check_and_add(visited, [x, y, z], target):
                        heappush(heap, (priority[0], ((x, y, z), priority[1])))
    
    @staticmethod
    def check_and_add(visited, target, parent):
        if target[0] not in visited.keys():
            visited[target[0]] = {target[1] : {target[2] : parent}}
            return True
        if target[1] not in visited[target[0]].keys():
            visited[target[0]][target[1]] = {target[2] : parent}
            return True
        if target[2] not in visited[target[0]][target[1]].keys():
            visited[target[0]][target[1]][target[2]] = parent
            return True
        return False

    @staticmethod
    def find_path(world, start, end, step_length=1, max_distance=500, radius=0.5, pivot=[0, 0, 0], drop_after=1000, priority_function='wp'):
        """
        Returns list of blocks on the path and actions to be done with them.
        0 -- tp, 1 -- put block under, 2 -- break lower block, 3 -- break upper block
        """
        step_length, max_distance, radius, drop_after = float(step_length), int(max_distance), float(radius), int(drop_after)
        path = []
        heap = []
        visited = {}
        Algorithm.check_and_add(visited, start, -1)
        r = [end[i] - (start[i] + pivot[i]) for i in range(3)]
        dist_end = sum([x**2 for x in r])**0.5 
        heappush(heap, (dist_end, (start, 0)))
        last_step = []
        found = False
        bad_moves_counter = 0
        last_distance = dist_end

        while heap:
            distance, element = heappop(heap)
            current_step, traveled_distance = element
            if distance >= last_distance:
                bad_moves_counter += 1
            else:
                bad_moves_counter = max(0, bad_moves_counter - 1)
            
            last_distance = distance

            if bad_moves_counter >= drop_after:
                print('Too many bad moves, quiting. Counter is {}'.format(bad_moves_counter))
                break

            # print('Distance is {}, max is {}, len is {}, counter is {}'.format(distance, max_distance, len(heap), bad_moves_counter))
            if np.linalg.norm(np.array(np.sum([current_step, pivot], axis=0))-np.array(end)) < radius:
                block_under = world.get_block(*np.sum([current_step, [0, -1, 0]], axis=0))
                if block_under not in world.info['blocks']['passable'] and block_under not in world.info['blocks']['damaging']:
                    found = True
                    last_step = current_step
                    break
            Algorithm.expand(world, visited, heap, current_step, start, end, traveled_distance, step_length, max_distance, pivot, priority_function)
        
        if found:
            current_step = last_step
            while current_step != -1:
                actions = Algorithm.get_actions(world, current_step)
                path.append((current_step, actions))
                current_step = visited[current_step[0]][current_step[1]][current_step[2]]
            
            path.reverse()
            return (path, step_length)
        
        return None

    @classmethod
    def get_method_from_dict(cls, name):
        method_dict = {
            'wp' : cls.walk_priority,
            'wmp' : cls.walk_and_mine_priority,
        }

        return method_dict[name]