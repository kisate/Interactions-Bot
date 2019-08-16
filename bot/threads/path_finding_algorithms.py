from heapq import heappush, heappop

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
        return path

class AStarAlgorithm(Algorithm):

    def expand(self, visited, heap, target, end, step_length, max_distance):
        for x in range(target[0] - step_length, target[0] + step_length + 1):
            for y in range(target[1], target[1] + 2):
                for z in range(target[2] - step_length, target[2] + step_length + 1):
                    if self.world.get_block(x, y, z) == 0 and self.world.get_block(x, y + 1, z) == 0:
                        distance_to_travel = ((x - target[0])**2 + (y - target[1])**2 + (z - target[2])**2)**0.5
                        if distance_to_travel <= step_length:
                            distance_to_end = ((x - end[0])**2 + (y - end[1])**2 + (z - end[2])**2)**0.5
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

    def find_path(self, start, end, step_length=8, max_distance=50):
        """
        Returns list of blocks on the path and actions to be done with them.
        0 -- tp
        """
        path = []
        heap = []
        visited = {}
        self.check_and_add(visited, start, -1)
        r = [end[i] - start[i] for i in range(3)]
        dist = sum([x**2 for x in r])**0.5  
        heappush(heap, (dist, start))
        found = False

        while heap:
            current_step = heappop(heap)[1]
            if current_step[0] == end[0] and current_step[1] == end[1] and current_step[2] == end[2]:  
                found = True
                break
            self.expand(visited, heap, current_step, end, step_length, max_distance)
        
        if found:
            current_step = end
            while current_step != -1:
                path.append((current_step, [0]))
                current_step = visited[current_step[0]][current_step[1]][current_step[2]]
            
            path.reverse()
            return path
        
        return None
        