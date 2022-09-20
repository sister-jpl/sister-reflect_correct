#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTER
Space-based Imaging Spectroscopy and Thermal PathfindER
Author: Adam Chlus
"""

import sys
import json
import os
from hytools.io import parse_envi_header


def main():

    header_file  = sys.argv[1]
    output_dir = sys.argv[2]

    header = parse_envi_header(header_file)
    base_name =os.path.basename(header_file)[:-4]

    metadata = {}
    metadata['sensor'] = header['sensor type'].upper()
    metadata['start_time'] = header['start acquisition time'].upper()
    metadata['end_time'] = header['end acquisition time'].upper()
    metadata['spatial_bounds'] = {}
    metadata['spatial_bounds']['latitude_min'] = float(header['latitude min'])
    metadata['spatial_bounds']['latitude_max'] = float(header['latitude max'])
    metadata['spatial_bounds']['longitude_min'] = float(header['longitude min'])
    metadata['spatial_bounds']['longitude_max'] = float(header['longitude max'])
    metadata['product'] = base_name.split('_')[4]
    metadata['processing_level'] = base_name.split('_')[3]

    config_file = '%s/%s.met.json' % (output_dir,base_name)

    with open(config_file, 'w') as outfile:
        json.dump(metadata,outfile,indent=3)

if __name__=='__main__':
    main()
