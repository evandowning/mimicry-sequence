#!/usr/bin/env python3

import sys
import os
import pickle as pkl

def usage():
    print('usage: python3 pkl2api.py api.txt metadata.pkl data.pkl')
    sys.exit(2)

def _main():
    if len(sys.argv) != 4:
        usage()

    api_fn = sys.argv[1]
    metadata_fn = sys.argv[2]
    sample = sys.argv[3]

    # Get number of API calls
    a = 0
    api_list = list()
    with open(api_fn, 'rb') as fr:
        for e,line in enumerate(fr):
            line = line.strip('\n')
            api_list.append('{0} {1}'.format(e+1,line))
            a += 1

    # Read metadata file
    with open(metadata_fn,'rb') as fr:
        # Window Size
        windowSize = pkl.load(fr)
        # Number of samples per label
        labelCount = pkl.load(fr)
        # Number of samples per data file (so we can determine folds properly)
        fileMap = pkl.load(fr)

    count = fileMap[os.path.basename(sample)[:-4]]

    # Extract API calls
    with open(sample,'rb') as fr:
        for i in range(count):
            s,l = pkl.load(fr)

            for api in s:
                if api == 0:
                    continue
#               print api, api_list[api-1]
                print(api_list[api-1].split(' ')[1])

if __name__ == '__main__':
    _main()
