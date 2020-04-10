#!/usr/bin/env python3

import sys
import os
import configparser

from multiprocessing import Pool
from contextlib import closing

import sequence.neo4j_mimicry

def usage():
    sys.stderr.write('usage: python3 mimicry.py mimicry.cfg\n')
    sys.exit(2)

def _main():
    if len(sys.argv) != 2:
        usage()

    config_fn = sys.argv[1]

    # Read configuration
    config = configparser.ConfigParser()
    config.read(config_fn)

    # Get arguments
    sequence_features = config['input_options']['sequences']
    target_hashes = config['input_options']['target_hashes']
    preferred_api = config['input_options']['preferred']
    attack_features = config['output_options']['attack_features']
    attack_configs = config['output_options']['attack_configs']

    # If folders don't exist, create them
    if not os.path.exists(attack_features):
        os.mkdir(attack_features)
    if not os.path.exists(attack_configs):
        os.mkdir(attack_configs)

    # Get preferred API calls to insert
    preferred = list()
    with open(preferred_api,'r') as fr:
        for line in fr:
            line = line.strip('\n')
            preferred.append(line)

    # Mimicry on sequence
    if config.getboolean('sequence','enable'):
        sys.stdout.write('Running sequence mimicry attack\n')

        attack_features_path = os.path.join(attack_features,'api-sequences')
        if not os.path.exists(attack_features_path):
            os.mkdir(attack_features_path)

        attack_configs_path = os.path.join(attack_configs,'api-sequences')
        if not os.path.exists(attack_configs_path):
            os.mkdir(attack_configs_path)


        # Get hashes to perform attack on
        hashes = list()
        with open(target_hashes,'r') as fr:
            for line in fr:
                line = line.strip('\n')
                h,c = line.split('\t')
                hashes.append(h)

                # Create output folders
                folder = os.path.join(attack_features_path,h)
                folder = os.path.join(attack_configs_path,h)
                if not os.path.exists(folder):
                    os.makedirs(folder)

        # Get parameters
        neo4j_username = config['sequence']['neo4j_username']
        neo4j_password = eval(config['sequence']['neo4j_password'])
        generations = int(config['sequence']['generations'])

        # Create arguments for multiprocessing
        args = [(sequence_features,h,neo4j_username,neo4j_password,attack_features_path,generations,preferred) for h in hashes]

        # Perform attack
        with closing ( Pool(20,maxtasksperchild=1) ) as p:
            results = p.imap_unordered(sequence.neo4j_mimicry.mimicry_wrapper,args)

            for e,r in enumerate(results):
                sys.stdout.write('Generating attack samples: {0}/{1}\r'.format(e+1,len(args)))
                sys.stdout.flush()

            sys.stdout.write('\n')
            sys.stdout.flush()
        #TODO - debugging
#       for a in args:
#           sequence.neo4j_mimicry.mimicry_wrapper(a)
#           break

        # Output config file for patchPE to use
        for h in hashes:
            # Get number of generated attacks
            attack_files = os.listdir(attack_features_path)
            generated = [f[-1] for f in attack_files if f[:len(h)] == h]

            # For each attack created for this sample
            for e,attack in enumerate(generated):

                sys.stdout.write('Writing configs for attacks: {0}/{1}\r'.format(e+1,len(generated)))
                sys.stdout.flush()

                attack_path = os.path.join(attack_features_path,h+'_'+attack)

                # Dictionary to hold calls to insert
                shells = dict()
                # Don't insert multiple API calls after a unique PC
                pc_set = set()

                # Scan attack sequence for inserted calls
                with open(attack_path,'r') as fr:
                    prev = None

                    # For each API call
                    for line in fr:
                        line = line.strip('\n')
                        pc,api = line.split(' ')

                        if prev == None:
                            prev = line
                            continue

                        # If this is an original call
                        if int(pc) != -1:
                            prev = line
                            continue

                        # If this is an inserted call
                        else:
                            if api not in shells:
                                shells[api] = dict()

                            # Get PC of previous call
                            pc_prev,api_prev = prev.split(' ')

                            # Only add API call if it's never been added before this PC before
                            if pc_prev not in pc_set:
                                shells[api][pc_prev] = api_prev
                                pc_set.add(pc_prev)

                # Write config file for creating new PE file
                attack_config = os.path.join(attack_configs_path,h,attack+'.cfg')
                with open(attack_config,'w') as fw:
                    for k,v in shells.items():
                        fw.write('[shellcode_{0}]\n'.format(k.lower()))
                        fw.write('target_addr = (\n')

                        for k2,v2 in v.items():
                            fw.write('    # {0}\n'.format(v2))
                            fw.write('    {0},\n'.format(hex(int(k2))))

                        fw.write('              )\n\n')

        sys.stdout.write('\n')
        sys.stdout.flush()

        sys.stdout.write('================================\n')

if __name__ == '__main__':
    _main()
