# SISTER L2A Reflectance Correction PGE Documentation

## Description

The L2A reflectance correction PGE applies a series of algorithms including topographic, BRDF and glint correction to surface reflectance data.......


## PGE Arguments

In addition to required MAAP job submission arguments the L2A spectral resampling PGE also takes the following argument(s):


|Argument| Type |  Description | Default|
|---|---|---|---|
| l1p_granule| string |URL to input L1 preprocess dataset granule| -|
| rfl_granule| string |URL to input L2a reflectance dataset granule| -|


## Outputs

The L2A spectral resampling PGE exports 2 ENVI formatted datacubes along with their associated header files. The outputs of the PGE use the following naming convention: 

		INSTRUMENT_YYYYMMDDTHHMMSS_L2A_SUBPRODUCT_VERSION

|Subproduct| Description |  Units |Example filename |
|---|---|---|---| 
| CORFL| ENVI 10nm reflectance datacube | % | AVNG\_20220502T180901\_L1B\_CORFL\_001 |
| CORFL  .hdr| ENVI 10nm reflectance header file  | - | AVNG\_20220502T180901\_L1B\_CORFL\_001.hdr |


All outputs of the L2a reflectance correction are compressed into a single tar.gz file using the following naming structure:
 
 	 	INSTRUMENT_YYYYMMDDTHHMMSS_L2A_CORFL_VERSION.tar.gz
 	 	
example:

		AVNG_20220502T180901_L2A_CORFL_001.tar.gz		

| Subproduct code | Description | Example | 
| ---|---|---|
| CORFL | Corrected reflectance datacube | 


Header files follow the same naming convention with a .hdr appended to the end of the filename.

## Example
	
	rfl_corr_job_response = maap.submitJob(
	    algo_id="sister-reflect_correct",
	    version="1.0.0",
	    l1_granule=l1p_granule,
	    l2_granule=rfl_granule,
	    publish_to_cmr=False,
	    cmr_metadata={},
	    queue="sister-job_worker-32gb",
	    identifier='l2a_corfl_AVNG_20170827T175432')














