import argparse
import numpy as np
import hytools as ht
from hytools.io.envi import WriteENVI
from hytools.brdf import calc_flex_single,set_solar_zn
from hytools.topo import calc_scsc_coeffs
from hytools.masks import mask_create
from hytools.misc import set_brdf

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

    desc = "Apply topographic, BRDF and glint corrections to reflectance image"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('rfl_file', type=str,
                        help='Input reflectance image')
    parser.add_argument('obs_file', type=str,
                        help='Input observables image')
    parser.add_argument('out_dir', type=str,
                        help='Output directory')
    parser.add_argument('--topo',  action='store_true',
                        help='Apply topo correction')
    parser.add_argument('--brdf',  action='store_true',
                        help='Apply brdf correction')
    parser.add_argument('--glint',  action='store_true',
                        help='Apply glint correction')

    args = parser.parse_args()

    if not args.topo | args.brdf | args.glint:
        print("No corrections specified. Exiting.")
        return

    # Load input file
    anc_files = dict(zip(anc_names,[[args.obs_file,a] for a in range(len(anc_names))]))
    rfl = ht.HyTools()
    rfl.read_file(args.rfl_file,'envi',anc_files)
    rfl.create_bad_bands([[300,400],[1337,1430],[1800,1960],[2450,2600]])

    corrections = []
    #Run corrections
    if args.topo:
        print('Calculating topo coefficients')
        rfl.mask['calc_topo'] =  mask_create(rfl,config_dict['topo']['calc_mask'])
        rfl.mask['apply_topo'] =  mask_create(rfl,config_dict['topo']['apply_mask'])
        calc_scsc_coeffs(rfl,config_dict['topo'])
        rfl.corrections.append('topo')
        corrections.append('Topographic')
    if args.brdf:
        print('Calculating BRDF coefficients')
        set_brdf(rfl,config_dict['brdf'])
        set_solar_zn(rfl)
        rfl.mask['calc_brdf'] =  mask_create(rfl,config_dict['brdf']['calc_mask'])
        calc_flex_single(rfl,config_dict['brdf'])
        rfl.corrections.append('brdf')
        corrections.append('BRDF')
    if args.glint:
        print('Setting glint coefficients')
        rfl.glint = config_dict['glint']
        rfl.corrections.append('glint')
        corrections.append('Glint')

    #Export corrected reflectance
    header_dict = rfl.get_header()
    header_dict['description'] = "%s corrected reflectance." % (' '.join(corrections))
    output_name = "%s/%s" % (args.out_dir,rfl.base_name)

    print('Exporting corrected image')
    writer = WriteENVI(output_name,header_dict)
    iterator = rfl.iterate(by='line', corrections=rfl.corrections)
    while not iterator.complete:
        line = iterator.read_next()
        writer.write_line(line,iterator.current_line)
    writer.close()

if __name__== "__main__":
    main()
