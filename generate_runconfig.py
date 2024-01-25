#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTER
Space-based Imaging Spectroscopy and Thermal PathfindER
Author: Adam Chlus
"""

import argparse
import sys
import json

def main():
    '''
        This function takes as input the path to an inputs.json file and exports a run config json
        containing the arguments needed to run the L1 preprocess PGE.

    '''

    parser = argparse.ArgumentParser(description='Parse inputs to create runconfig.json')
    parser.add_argument('--observation_dataset', help='Path to reflectance dataset')
    parser.add_argument('--reflectance_dataset', help='Path to uncertainty dataset')
    parser.add_argument('--crid', help='CRID value', default="000")
    parser.add_argument('--experimental', help='If true then designates data as experiemntal', default="True")
    args = parser.parse_args()

    run_config = {
        "inputs": {
            "observation_dataset": args.observation_dataset,
            "reflectance_dataset": args.reflectance_dataset,
            "crid": args.crid
        }
    }
    run_config["inputs"]["experimental"] = True if args.experimental.lower() == "true" else False

    config_file = 'runconfig.json'

    with open(config_file, 'w') as outfile:
        json.dump(run_config,outfile,indent=3)


if __name__=='__main__':
    main()
