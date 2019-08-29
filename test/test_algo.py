from bot.threads.path_finding_algorithm import Algorithm
import pickle

points = [
    [[17, 104, 102], [15, 104, 107]],
    # [[48, 64, 271], [62, 62, 250]],
    # [[60, 64, 254], [59, 63, 264]],
    # [[59, 59, 261], [54, 60, 269]]
]

args = {
    'priority_function' : 'wp',
    'step_length' : 1
}

with open('test/world.data', 'rb') as f:
    world = pickle.load(f)

logs = []

for point in points:
    log = []
    args['start'] = point[0]
    args['end'] = point[1]
    args['log'] = log
    path = Algorithm.find_path(world, **args)
    log.append([path, -1])
    print(f'{point} {path}')
    print(log)
    logs.append(log)
with open('test/queue.log', 'wb') as f:
    pickle.dump(logs, f)
# pickle.dump
