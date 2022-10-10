# SISTER Reflectance Correction PGE Documentation## DescriptionThe L2A reflectance correction PGE applies a series of algorithms including topographic, BRDF and glint correction to surface reflectance data.## PGE ArgumentsIn addition to required MAAP job submission arguments the L2A spectral resampling PGE also takes the following argument(s):|Argument| Type |  Description | Default||---|---|---|---|| l1b_granule| string |L1n preprocess dataset granule URL | -|| l2a_granule| string |L2a reflectance dataset granule URL| -|## OutputsThe L2A reflectance correction PGE exports an ENVI formatted datacube along with it's associated header file. The outputs of the PGE use the following naming convention:		SISTER_INSTRUMENT_YYYYMMDDTHHMMSS_L2A_SUBPRODUCT_VERSION|Subproduct| Description |  Units |Example filename ||---|---|---|---|| CORFL| ENVI corrected reflectance datacube | % | SISTER_AVNG\_20220502T180901\_L2A\_CORFL\_001 || | ENVI corrected reflectance header file  | - | SISTER_AVNG\_20220502T180901\_L2A\_CORFL\_001.hdr |All outputs of the L2A reflectance correction are compressed into a single tar.gz file using the following naming structure: 	 	SISTER_INSTRUMENT_YYYYMMDDTHHMMSS_L2A_CORFL_VERSION.tar.gzexample:		SISTER_AVNG_20220502T180901_L2A_CORFL_001.tar.gz## Algorithm registration

	from maap.maap import MAAP
	maap = MAAP(maap_host="sister-api.imgspec.org")
	

	rfl_correct_alg = {
	    "script_command": "sister-reflect_correct/.imgspec/imgspec_run.sh",
	    "repo_url": "https://github.com/EnSpec/sister-reflect_correct.git",
	    "algorithm_name":"sister-reflect_correct",
	    "code_version":"1.0.0",
	    "algorithm_description":"Topo, BRDF and glint correction",
	    "environment_name":"ubuntu",
	    "disk_space":"70GB",
	    "queue": "sister-job_worker-32gb",
	    "build_command": "sister-reflect_correct/.imgspec/install.sh",
	    "docker_container_url": docker_container_url,
	    "algorithm_params":[
	        {
	            "field": "l1b_granule",
	            "type": "file"
	        },
	        {
	            "field": "l2a_granule",
	            "type": "file"
	        }
	    ]
	}
	response = maap.registerAlgorithm(arg=rfl_correct_alg)## Example	rfl_corr_job_response = maap.submitJob(	    algo_id="sister-reflect_correct",	    version="1.0.0",	    l1b_granule=l1b_granule,	    l2a_granule=l2a_granule,	    publish_to_cmr=False,	    cmr_metadata={},	    queue="sister-job_worker-32gb",	    identifier='SISTER_AVNG_20170827T175432_L2A_CORFL_000')