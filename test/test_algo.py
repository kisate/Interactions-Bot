from bot.threads.path_finding_algorithm import Algorithm
import pickle

points = [
    [[67, 70, 270], [63, 64, 263]],
    [[48, 64, 271], [62, 62, 250]],
    [[60, 64, 254], [59, 63, 264]],
    [[59, 59, 261], [54, 60, 269]]
]

args = {
    'priority_function' : 'wmp',
    'step_length' : 1
}

with open('test/world.data', 'rb') as f:
    world = pickle.load(f)

for point in points:
    args['start'] = point[0]
    args['end'] = point[1]
    path = Algorithm.find_path(world, **args)
    print(f'{point} {path}')
