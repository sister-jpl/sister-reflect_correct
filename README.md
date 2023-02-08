# SISTER Reflectance Correction PGE Documentation## DescriptionThe L2A reflectance correction PGE applies topographic, BRDF and glint corrections to surface reflectance data. Topographic correction is performed using the Sun-Canopy-Sensor+C algorithm (Soenen et al. 2005), BRDF correction is performed using the FlexBRDF algorithm (Queally et al. 2022) and glint correction is performed using the method of Gao and Li (2021). Because of narrow fields of view BRDF correction is not applied to PRISMA or DESIS images.

![AVIRIS correctionexample](./reflect_correct_example.png)

### References

 - Gao, B. C., & Li, R. R. (2021). Correction of Sunglint Effects in High Spatial Resolution Hyperspectral Imagery Using SWIR or NIR Bands and Taking Account of Spectral Variation of Refractive Index of Water. Advances in Environmental and Engineering Research, 2(3), 1-15.
 - Queally, N., Ye, Z., Zheng, T., Chlus, A., Schneider, F., Pavlick, R. P., & Townsend, P. A. (2022). FlexBRDF: A flexible BRDF correction for grouped processing of airborne imaging spectroscopy flightlines. Journal of Geophysical Research: Biogeosciences, 127(1), e2021JG006622.
 - Soenen, S. A., Peddle, D. R., & Coburn, C. A. (2005). SCS+ C: A modified sun-canopy-sensor topographic correction in forested terrain. IEEE Transactions on geoscience and remote sensing, 43(9), 2148-2159.


## PGE ArgumentsIn addition to required MAAP job submission arguments the L2A spectral resampling PGE also takes the following argument(s):|Argument| Type |  Description | Default||---|---|---|---|| observation_dataset| file |L1B observation dataset | -|| reflectance_dataset| config |L2A reflectance dataset| -|| crid| config | Composite release identifier| '000'|## OutputsThe outputs of the L2A reflectance correction PGE use the following naming convention:

    SISTER_<SENSOR>_L2A_CORFL_<YYYYMMDDTHHMMSS>_<CRID>
|Product description |  Units |Example filename ||---|---|---|
| ENVI corrected reflectance datacube | % | SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.bin || ENVI corrected reflectance header file  | - | SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.hdr |
| Corrected reflectance metadata  | - | SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.met.json || False color reflectance quicklook  | - |  SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.png |
| PGE runconfig| - |  SISTER\_AVNG\_L2A\_CORFL\_20220502T180901\_001.runconfig.json |
| PGE log| - |  SISTER\_AVNG\_L2A\_CORFL\_20220502T180901\_001.log |## Algorithm registration

This algorithm can be registered using the algorirthm_config.yml file found in this repository:

	from maap.maap import MAAP
	import IPython
	
	maap = MAAP(maap_host="sister-api.imgspec.org")

	reflect_correct_alg_yaml = './sister-reflect_correct/algorithm_config.yaml'
	maap.register_algorithm_from_yaml_file(file_path= reflect_correct_alg_yaml)## Example	rfl_corr_job_response = maap.submitJob(	    algo_id="sister-reflect_correct",	    version="2.0.0",	    observation_dataset ='SISTER_AVNG_L1B_RDN_20220502T180901_001_OBS',	    reflectance_dataset ='SISTER_AVNG_L2A_RSRFL_20220502T180901_001',
	    crid = '000',	    publish_to_cmr=False,	    cmr_metadata={},	    queue="sister-job_worker-16gb",	    identifier='SISTER_AVNG_L2A_CORFL_20220502T180901_001')