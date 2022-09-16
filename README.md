# SISTER L2A Reflectance Correction PGE Documentation## DescriptionThe L2A reflectance correction PGE applies a series of algorithms including topographic, BRDF and glint correction to surface reflectance data.......## PGE ArgumentsIn addition to required MAAP job submission arguments the L2A spectral resampling PGE also takes the following argument(s):|Argument| Type |  Description | Default||---|---|---|---|| l1b_granule| string |L1n preprocess dataset granule URL | -|| rfl_granule| string |L2a reflectance dataset granule URL| -|## OutputsThe L2A spectral resampling PGE exports 2 ENVI formatted datacubes along with their associated header files. The outputs of the PGE use the following naming convention:		SISTER_INSTRUMENT_YYYYMMDDTHHMMSS_L2A_SUBPRODUCT_VERSION|Subproduct| Description |  Units |Example filename ||---|---|---|---|| CORFL| ENVI corrected reflectance datacube | % | SISTER_AVNG\_20220502T180901\_L2A\_CORFL\_001 || | ENVI corrected reflectance header file  | - | SISTER_AVNG\_20220502T180901\_L2A\_CORFL\_001.hdr |All outputs of the L2A reflectance correction are compressed into a single tar.gz file using the following naming structure: 	 	SISTER_INSTRUMENT_YYYYMMDDTHHMMSS_L2A_CORFL_VERSION.tar.gzexample:		SISTER_AVNG_20220502T180901_L2A_CORFL_001.tar.gz## Example	rfl_corr_job_response = maap.submitJob(	    algo_id="sister-reflect_correct",	    version="1.0.0",	    l1_granule=l1b_granule,	    l2_granule=rfl_granule,	    publish_to_cmr=False,	    cmr_metadata={},	    queue="sister-job_worker-32gb",	    identifier='SISTER_AVNG_20170827T175432_L2A_CORFL_000')