import bootstrap
import sys
import os

from multiprocessing.queues import Queue
from multiprocessing.pool import Pool
import multiprocessing
import itertools

from aisbx import platform
from game import application

def run(args):
    map, candidates = args
    sys.stdout.write('.')
    runner = platform.ConsoleRunner()
    app = application.CaptureTheFlag(list(candidates), map, quiet = True, games = 1)
    runner.run(app)
    sys.stdout.write('o')
    return map, app.scores


if __name__ == '__main__':
    p = Pool(processes = multiprocessing.cpu_count())

    total = 0
    scores = {}    
    pairs = itertools.permutations(['examples.Greedy', 'mycmd.DefensiveCommander'], 2)
    games = itertools.product(['map00', 'map01', 'map10'], pairs)
    for map, results in p.map(run, games):
        for bot, score in results.items():
            scores.setdefault(bot, [0, 0])
            scores[bot][0] += score[0]
            scores[bot][1] += score[1]
        total += 1

    print "\n%i total games run." % (total)
    for r, s in sorted(scores.items(), key = lambda i: -i[1][0]+i[1][1]):
        print "{}   for: {}, against: {}".format(r.replace('Commander', '').upper(), s[0], s[1])

    raw_input()
