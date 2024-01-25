import datetime as dt
import glob
import json
import logging
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
import pystac
import spectral.io.envi as envi

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

    # Set up console logging using root logger
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
    logger = logging.getLogger("sister-reflect_correct")
    # Set up file handler logging
    handler = logging.FileHandler("pge_run.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(module)s]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Starting reflect_correct.py")

    run_config_json = sys.argv[1]

    with open(run_config_json, 'r') as in_file:
        run_config =json.load(in_file)

    experimental = run_config['inputs']['experimental']
    if experimental:
        disclaimer = "(DISCLAIMER: THIS DATA IS EXPERIMENTAL AND NOT INTENDED FOR SCIENTIFIC USE) "
    else:
        disclaimer = ""

    os.mkdir('output')

    rfl_base_name = os.path.basename(run_config['inputs']['reflectance_dataset'])
    sister,sensor,level,product,datetime,in_crid = rfl_base_name.split('_')

    crid = run_config['inputs']['crid']

    rfl_file = f'{run_config["inputs"]["reflectance_dataset"]}/{rfl_base_name}.bin'

    out_rfl_file =  f'output/SISTER_{sensor}_L2A_CORFL_{datetime}_{crid}.bin'

    obs_base_name = os.path.basename(run_config['inputs']['observation_dataset'])
    obs_file = f'{run_config["inputs"]["observation_dataset"]}/{obs_base_name}.bin'

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
        logger.info('Calculating topo coefficients')
        rfl.mask['calc_topo'] =  mask_create(rfl,config_dict['topo']['calc_mask'])
        rfl.mask['apply_topo'] =  mask_create(rfl,config_dict['topo']['apply_mask'])
        calc_scsc_coeffs(rfl,config_dict['topo'])
        rfl.corrections.append('topo')
    if 'BRDF' in corrections:
        logger.info('Calculating BRDF coefficients')
        set_brdf(rfl,config_dict['brdf'])
        set_solar_zn(rfl)
        rfl.mask['calc_brdf'] =  mask_create(rfl,config_dict['brdf']['calc_mask'])
        calc_flex_single(rfl,config_dict['brdf'])
        rfl.corrections.append('brdf')
    if 'Glint' in corrections:
        logger.info('Setting glint coefficients')
        rfl.glint = config_dict['glint']
        rfl.corrections.append('glint')

    #Export corrected reflectance
    header_dict = rfl.get_header()
    header_dict['description'] =f'{" ".join(corrections)} corrected reflectance'

    logger.info('Exporting corrected image')
    writer = WriteENVI(out_rfl_file,header_dict)
    iterator = rfl.iterate(by='line', corrections=rfl.corrections)
    while not iterator.complete:
        line = iterator.read_next()
        writer.write_line(line,iterator.current_line)
    writer.close()

    generate_quicklook(out_rfl_file)

    # Take care of disclaimer in ENVI header and rename files
    if experimental:
        out_hdr_file = out_rfl_file.replace(".bin", ".hdr")
        hdr = parse_envi_header(out_hdr_file)
        hdr["description"] = disclaimer + hdr["description"].capitalize()
        write_envi_header(out_hdr_file, hdr)
        for file in glob.glob(f"output/SISTER*"):
            shutil.move(file, f"output/EXPERIMENTAL-{os.path.basename(file)}")

    corfl_file = glob.glob("output/*%s.bin" % run_config['inputs']['crid'])[0]
    corfl_basename = os.path.basename(corfl_file)[:-4]

    output_runconfig_path = f'output/{corfl_basename}.runconfig.json'
    shutil.copyfile(run_config_json, output_runconfig_path)

    output_log_path = f'output/{corfl_basename}.log'
    if os.path.exists("pge_run.log"):
        shutil.copyfile('pge_run.log', output_log_path)

    # Generate STAC
    catalog = pystac.Catalog(id=corfl_basename,
                             description=f'{disclaimer}This catalog contains the output data products of the SISTER '
                                         f'corrected reflectance PGE, including topo-, brdf-, and glint-corrected '
                                         f'reflectance. Execution artifacts including the runconfig file and execution '
                                         f'log file are included with the corrected reflectance data.')

    # Add items for data products
    hdr_files = glob.glob("output/*SISTER*.hdr")
    hdr_files.sort()
    for hdr_file in hdr_files:
        # TODO: Use incoming item.json to get properties and geometry and use hdr_file for description (?)
        metadata = generate_stac_metadata(hdr_file)
        assets = {
            "envi_binary": f"./{os.path.basename(hdr_file.replace('.hdr', '.bin'))}",
            "envi_header": f"./{os.path.basename(hdr_file)}"
        }
        # If it's the reflectance product, then add png, runconfig, and log
        if os.path.basename(hdr_file) == f"{corfl_basename}.hdr":
            png_file = hdr_file.replace(".hdr", ".png")
            assets["browse"] = f"./{os.path.basename(png_file)}"
            assets["runconfig"] = f"./{os.path.basename(output_runconfig_path)}"
            if os.path.exists(output_log_path):
                assets["log"] = f"./{os.path.basename(output_log_path)}"
        item = create_item(metadata, assets)
        catalog.add_item(item)

    # set catalog hrefs
    catalog.normalize_hrefs(f"./output/{corfl_basename}")

    # save the catalog
    catalog.describe()
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print("Catalog HREF: ", catalog.get_self_href())
    # print("Item HREF: ", item.get_self_href())

    # Move the assets from the output directory to the stac item directories and create empty .met.json files
    for item in catalog.get_items():
        for asset in item.assets.values():
            fname = os.path.basename(asset.href)
            shutil.move(f"output/{fname}", f"output/{corfl_basename}/{item.id}/{fname}")
        with open(f"output/{corfl_basename}/{item.id}/{item.id}.met.json", mode="w"):
            pass


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


def generate_stac_metadata(header_file):

    header = envi.read_envi_header(header_file)
    base_name = os.path.basename(header_file)[:-4]

    metadata = {}
    metadata['id'] = base_name
    metadata['start_datetime'] = dt.datetime.strptime(header['start acquisition time'], "%Y-%m-%dt%H:%M:%Sz")
    metadata['end_datetime'] = dt.datetime.strptime(header['end acquisition time'], "%Y-%m-%dt%H:%M:%Sz")
    # Split corner coordinates string into list
    coords = [float(x) for x in header['bounding box'].replace(']', '').replace('[', '').split(',')]
    geometry = [list(x) for x in zip(coords[::2], coords[1::2])]
    # Add first coord to the end of the list to close the polygon
    geometry.append(geometry[0])
    metadata['geometry'] = {
        "type": "Polygon",
        "coordinates": geometry
    }
    base_tokens = base_name.split('_')
    metadata['collection'] = f"SISTER_{base_tokens[1]}_{base_tokens[2]}_{base_tokens[3]}_{base_tokens[5]}"
    metadata['properties'] = {
        'sensor': base_tokens[1],
        'description': header['description'],
        'product': base_tokens[3],
        'processing_level': base_tokens[2]
    }
    return metadata


def create_item(metadata, assets):
    item = pystac.Item(
        id=metadata['id'],
        datetime=metadata['start_datetime'],
        start_datetime=metadata['start_datetime'],
        end_datetime=metadata['end_datetime'],
        geometry=metadata['geometry'],
        collection=metadata['collection'],
        bbox=None,
        properties=metadata['properties']
    )
    # Add assets
    for key, href in assets.items():
        item.add_asset(key=key, asset=pystac.Asset(href=href))
    return item


if __name__== "__main__":
    main()
