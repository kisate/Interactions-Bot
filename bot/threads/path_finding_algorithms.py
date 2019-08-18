from heapq import heappush, heappop
from math import ceil

class Algorithm():
    def __init__(self, world):
        self.world = world
    def find_path(self, start, end, step_length=8):
        return []
    

class StraightForwardAlgorithm(Algorithm):
    def find_path(self, start, end, step_length=8):
        """
        Returns list of blocks on the path and actions to be done with them.
        0 -- tp, 1 -- put block under, 2 -- break lower block, 3 -- break upper block
        """
        path = []
        current_block = start
        r = [end[i] - current_block[i] for i in range(3)]
        dist = sum([x**2 for x in r])**0.5    
        
        while dist >= step_length:
            next_block = [int(r[i]/dist*step_length + current_block[i]) for i in range(3)]
            next_step = [next_block, []]
            if self.world.get_block(next_block[0], next_block[1] - 1, next_block[2]) == 0:
                next_step[1].append(1)
            if self.world.get_block(*next_block) != 0:
                next_step[1].append(2)
            if self.world.get_block(next_block[0], next_block[1] + 1, next_block[2]) != 0:
                next_step[1].append(3)
            next_step[1].append(0)
            next_step[0][0] += 0.5
            next_step[0][2] += 0.5

            path.append(next_step)

            current_block = next_block
            r = [end[i] - current_block[i] for i in range(3)]
            dist = sum([x**2 for x in r])**0.5    

        next_block = [int(x) for x in end]
        next_step = [next_block, []]
        if self.world.get_block(next_block[0], next_block[1] - 1, next_block[2]) == 0:
            next_step[1].append(1)
        if self.world.get_block(*next_block) != 0:
            next_step[1].append(2)
        if self.world.get_block(next_block[0], next_block[1] + 1, next_block[2]) != 0:
            next_step[1].append(3)
        next_step[1].append(0)
        next_step[0][0] += 0.5
        next_step[0][2] += 0.5

        path.append(next_step)
        return (path, step_length)

class AStarAlgorithm(Algorithm):

    def expand(self, visited, heap, target, end, step_length, max_distance, pivot):
        step_length_int = ceil(step_length)
        for x in range(target[0] - step_length_int, target[0] + step_length_int + 1):
            for y in range(target[1] - step_length_int, target[1] + step_length_int + 1):
                for z in range(target[2] - step_length_int, target[2] + step_length_int + 1):
                    if (self.world.get_block(x, y, z) in self.world.block_info['blocks']['passable'] 
                        and self.world.get_block(x, y + 1, z) in self.world.block_info['blocks']['passable']
                            and not (self.world.get_block(x, y - 1, z) in self.world.block_info['blocks']['passable'])):
                        distance_to_travel = ((x - target[0])**2 + (y - target[1])**2 + (z - target[2])**2)**0.5
                        if distance_to_travel <= step_length or (y != target[1] and distance_to_travel <= step_length*2 and distance_to_travel <= 9):
                            distance_to_end = ((x + pivot[0] - end[0])**2 + (y + pivot[1]- end[1])**2 + (z + pivot[2] - end[2])**2)**0.5
                            if distance_to_end <= max_distance:
                                if self.check_and_add(visited, (x, y, z), target):
                                    heappush(heap, (distance_to_end, (x, y, z)))
   
    def check_and_add(self, visited, target, parent):
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

    def find_path(self, start, end, step_length=1, max_distance=500, radius=0.5, pivot=[0, 0, 0], drop_after=500):
        """
        Returns list of blocks on the path and actions to be done with them.
        0 -- tp
        """
        path = []
        heap = []
        visited = {}
        self.check_and_add(visited, start, -1)
        r = [end[i] - (start[i] + pivot[i]) for i in range(3)]
        dist = sum([x**2 for x in r])**0.5  
        heappush(heap, (dist, start))
        last_step = []
        found = False
        bad_moves_counter = 0
        last_distance = dist

        while heap:
            distance, current_step = heappop(heap)
            if distance >= last_distance:
                bad_moves_counter += 1
            else:
                bad_moves_counter = max(0, bad_moves_counter - 1)
            
            last_distance = distance

            if bad_moves_counter >= drop_after:
                print('Too many bad moves, quiting. Counter is {}'.format(bad_moves_counter))
                break

            # print('Distance is {}, max is {}, len is {}, counter is {}'.format(distance, max_distance, len(heap), bad_moves_counter))
            if (sum([(end[i] - (current_step[i] + pivot[i]))**2 for i in range(3)]))**0.5 < radius:  
                found = True
                last_step = current_step
                break
            self.expand(visited, heap, current_step, end, step_length, max_distance, pivot)
        
        if found:
            current_step = last_step
            while current_step != -1:
                path.append((current_step, [0]))
                current_step = visited[current_step[0]][current_step[1]][current_step[2]]
            
            path.reverse()
            return (path, step_length)
        
        return None
