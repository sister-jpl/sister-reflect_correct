import glob
import json
import os
import shutil
import sys
import numpy as np
import hytools as ht
from hytools.io import parse_envi_header, write_envi_header
from hytools.io.envi import WriteENVI
from hytools.brdf import calc_flex_single,set_solar_zn
from hytools.topo import calc_scsc_coeffs
from hytools.masks import mask_create
from hytools.misc import set_brdf
from PIL import Image


anc_names = ['path_length','sensor_az','sensor_zn',
                'solar_az', 'solar_zn','phase','slope',
                'aspect', 'cosine_i','utc_time','']


# Hard-code configuration dictionary
#######################################################
config_dict = {}
config_dict["topo"] =  {}
config_dict["topo"]['type'] =  'scs+c'
config_dict["topo"]['calc_mask'] = [["ndi", {'band_1': 850,'band_2': 660,
                                             'min': 0.1,'max': 1.0}],
                                    ['ancillary',{'name':'slope',
                                                  'min': np.radians(5),'max':'+inf' }],
                                    ['ancillary',{'name':'cosine_i',
                                                  'min': 0.12,'max':'+inf' }]]
config_dict["topo"]['apply_mask'] = [["ndi", {'band_1': 850,'band_2': 660,
                                             'min': 0.1,'max': 1.0}],
                                    ['ancillary',{'name':'slope',
                                                  'min': np.radians(5),'max':'+inf' }],
                                    ['ancillary',{'name':'cosine_i',
                                                  'min': 0.12,'max':'+inf' }]]
config_dict["topo"]['c_fit_type'] = 'nnls'

config_dict["brdf"] = {}
config_dict["brdf"]['type'] =  'flex'
config_dict["brdf"]['grouped'] =  False
config_dict["brdf"]['geometric'] = 'li_dense_r'
config_dict["brdf"]['volume'] = 'ross_thick'
config_dict["brdf"]["b/r"] = 2.5
config_dict["brdf"]["h/b"] = 2
config_dict["brdf"]['sample_perc'] = 0.1
config_dict["brdf"]['interp_kind'] = 'linear'
config_dict["brdf"]['calc_mask'] = [["ndi", {'band_1': 850,'band_2': 660,
                                              'min': 0.1,'max': 1.0}]]
config_dict["brdf"]['apply_mask'] = [["ndi", {'band_1': 850,'band_2': 660,
                                              'min': 0.1,'max': 1.0}]]
config_dict["brdf"]['bin_type'] = 'dynamic'
config_dict["brdf"]['num_bins'] = 18
config_dict["brdf"]['ndvi_bin_min'] = 0.1
config_dict["brdf"]['ndvi_bin_max'] = 1.0
config_dict["brdf"]['ndvi_perc_min'] = 10
config_dict["brdf"]['ndvi_perc_max'] = 95

config_dict["glint"]  = {}
config_dict['glint']['type'] = 'gao'
config_dict['glint']['correction_wave'] = 860
config_dict['glint']['apply_mask'] =  [["ndi", {'band_1': 850,'band_2': 660,
                                              'min': -1,'max': 0.}],
                                       ["band", {'band': 560,
                                              'min': 0,'max': 0.2}]]
config_dict['glint']['truncate'] = True
#######################################################

def main():

    run_config_json = sys.argv[1]

    with open(run_config_json, 'r') as in_file:
        run_config =json.load(in_file)

    experimental = run_config['inputs']['experimental']

    os.mkdir('output')

    rfl_base_name = os.path.basename(run_config['inputs']['reflectance_dataset'])
    sister,sensor,level,product,datetime,in_crid = rfl_base_name.split('_')

    crid = run_config['inputs']['crid']

    rfl_file = f'input/{rfl_base_name}/{rfl_base_name}.bin'
    rfl_met = rfl_file.replace('.bin','.met.json')

    out_rfl_file =  f'output/SISTER_{sensor}_L2A_CORFL_{datetime}_{crid}.bin'
    out_rfl_met = out_rfl_file.replace('.bin','.met.json')

    obs_base_name = os.path.basename(run_config['inputs']['observation_dataset'])
    obs_file = f'input/{obs_base_name}/{obs_base_name}.bin'

    # Load input file
    anc_files = dict(zip(anc_names,[[obs_file,a] for a in range(len(anc_names))]))
    rfl = ht.HyTools()
    rfl.read_file(rfl_file,'envi',anc_files)
    rfl.create_bad_bands([[300,400],[1337,1430],[1800,1960],[2450,2600]])

    if sensor in ['PRISMA','DESIS','EMIT']:
        corrections = ['Topographic','Glint']
    else:
        corrections = ['Topographic','BRDF','Glint']

    #Run corrections
    if 'Topographic' in corrections:
        print('Calculating topo coefficients')
        rfl.mask['calc_topo'] =  mask_create(rfl,config_dict['topo']['calc_mask'])
        rfl.mask['apply_topo'] =  mask_create(rfl,config_dict['topo']['apply_mask'])
        calc_scsc_coeffs(rfl,config_dict['topo'])
        rfl.corrections.append('topo')
    if 'BRDF' in corrections:
        print('Calculating BRDF coefficients')
        set_brdf(rfl,config_dict['brdf'])
        set_solar_zn(rfl)
        rfl.mask['calc_brdf'] =  mask_create(rfl,config_dict['brdf']['calc_mask'])
        calc_flex_single(rfl,config_dict['brdf'])
        rfl.corrections.append('brdf')
    if 'Glint' in corrections:
        print('Setting glint coefficients')
        rfl.glint = config_dict['glint']
        rfl.corrections.append('glint')

    #Export corrected reflectance
    header_dict = rfl.get_header()
    header_dict['description'] =f'{" ".join(corrections)} corrected reflectance'

    print('Exporting corrected image')
    writer = WriteENVI(out_rfl_file,header_dict)
    iterator = rfl.iterate(by='line', corrections=rfl.corrections)
    while not iterator.complete:
        line = iterator.read_next()
        writer.write_line(line,iterator.current_line)
    writer.close()

    # Take care of disclaimer in ENVI header and .met.json
    if experimental:
        disclaimer = "(DISCLAIMER: THIS DATA IS EXPERIMENTAL AND NOT INTENDED FOR SCIENTIFIC USE) "
        out_hdr_file = out_rfl_file.replace(".bin", ".hdr")
        hdr = parse_envi_header(out_hdr_file)
        hdr["description"] = disclaimer + hdr["description"].capitalize()
        write_envi_header(out_hdr_file, hdr)
    else:
        disclaimer = ""
    generate_metadata(rfl_met,
                      out_rfl_met,
                      {'product': 'CORFL',
                      'processing_level': 'L2A',
                      'description' : disclaimer + header_dict['description']})

    generate_quicklook(out_rfl_file)

    shutil.copyfile(run_config_json,
                    out_rfl_file.replace('.bin','.runconfig.json'))

    if os.path.exists("run.log"):
        shutil.copyfile('run.log',
                        out_rfl_file.replace('.bin','.log'))

    # If experimental, prefix filenames with "EXPERIMENTAL-"
    if experimental:
        for file in glob.glob(f"output/SISTER*"):
            shutil.move(file, f"output/EXPERIMENTAL-{os.path.basename(file)}")


def generate_metadata(in_file,out_file,metadata):

    with open(in_file, 'r') as in_obj:
        in_met =json.load(in_obj)

    for key,value in metadata.items():
        in_met[key] = value

    with open(out_file, 'w') as out_obj:
        json.dump(in_met,out_obj,indent=3)


def generate_quicklook(input_file):

    img = ht.HyTools()
    img.read_file(input_file)
    image_file = input_file.replace('.bin','.png')

    if 'DESIS' in img.base_name:
        band3 = img.get_wave(560)
        band2 = img.get_wave(850)
        band1 = img.get_wave(660)
    else:
        band3 = img.get_wave(560)
        band2 = img.get_wave(850)
        band1 = img.get_wave(1660)

    rgb=  np.stack([band1,band2,band3])
    rgb[rgb == img.no_data] = np.nan

    rgb = np.moveaxis(rgb,0,-1).astype(float)
    bottom = np.nanpercentile(rgb,5,axis = (0,1))
    top = np.nanpercentile(rgb,95,axis = (0,1))
    rgb = np.clip(rgb,bottom,top)
    rgb = (rgb-np.nanmin(rgb,axis=(0,1)))/(np.nanmax(rgb,axis= (0,1))-np.nanmin(rgb,axis= (0,1)))
    rgb = (rgb*255).astype(np.uint8)

    im = Image.fromarray(rgb)
    im.save(image_file)

if __name__== "__main__":
    main()
