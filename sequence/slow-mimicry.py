#!/usr/bin/env python3

import sys
import os
import pickle as pkl

# From https://eddmann.com/posts/depth-first-search-and-breadth-first-search-in-python/
# Pythonic way of BFS (modified for my needs)
def bfs_paths(graph, start, goal, maxDepth):
    queue = [(start, [start])]
    while queue:
        (vertex, path) = queue.pop(0)
        for next in graph[vertex] - set(path):
            if len(path) > maxDepth:
                break

            if next == goal:
                yield path + [next]
            else:
                queue.append((next, path + [next]))

# Perform mimicry attack on sequences
def mimicry(raw, benign_list, target):
    rv = list()

    # Determine which samples to model paths after
    sample = list()
    with open(benign_list,'r') as fr:
        for line in fr:
            line = line.strip('\n')
            sample.append(line)

    print('Constructing benign paths')

    # Construct paths between benign sample API calls
    benign_path = dict()
    for e,s in enumerate(sample):
        prev = None

        sys.stdout.write('Processing sample: {0}/{1}\r'.format(e,len(sample)))
        sys.stdout.flush()

        # If this file doesn't exist, ignore it
        if not os.path.exists(os.path.join(raw,s)):
            sys.stderr.write('Sample {0} doesn\'t exist\n'.format(s))
            continue

        with open(os.path.join(raw,s),'r') as fr:
            for line in fr:
                line = line.strip('\n')
                line = line.split(' ')[1]

                if prev != None:
                    if prev not in benign_path:
                        benign_path[prev] = set()

                    benign_path[prev].add(line)

                prev = line

    sys.stdout.write('\n')
    sys.stdout.flush()

    print('Writing benign paths...')
    with open('benign_paths.pkl','w') as fw:
        pkl.dump(benign_path,fw)

    print('Running mimicry attack...')

    # Read target and determine mimicry sequence (logging any erroneous linking)
    with open(os.path.join(raw,target),'r') as fr:
        prev = None

        for line in fr:
            line = line.strip('\n')
            api = line.split(' ')[1]

            # Find path from prev to line
            if prev != None:
                if prev in benign_path:

                    a = 'null'
                    # Check for path of length 2
                    if a != api:
                        p = list(bfs_paths(benign_path, prev, api, 2))
                        if len(p) == 0:
                            sys.stderr.write('Error. No short path between {0} and {1}\n'.format(prev,api))
                        else:
                            for a in p[0][1:-1]:
                                rv.append('-1 {0}'.format(a))

            rv.append(line)

            prev = api

    return rv
