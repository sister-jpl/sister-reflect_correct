# SISTER Reflectance Correction PGE Documentation## DescriptionThe L2A reflectance correction PGE applies a series of algorithms including topographic, BRDF and glint correction to surface reflectance data.## PGE ArgumentsIn addition to required MAAP job submission arguments the L2A spectral resampling PGE also takes the following argument(s):|Argument| Type |  Description | Default||---|---|---|---|| l1b_granule| string |L1b preprocess dataset granule URL | -|| l2a_granule| string |L2a reflectance dataset granule URL| -|| CRID| string | Composite release identifier| 000|## OutputsThe L2A reflectance correction PGE exports an ENVI formatted datacube along with it's associated header file. The outputs of the PGE use the following naming convention:		SISTER_<SENSOR>_L2A_CORFL_<YYYYMMDDTHHMMSS>_CRID.bin
|Subproduct| Description |  Units |Example filename ||---|---|---|---|| \*CORFL\*.bin| ENVI corrected reflectance datacube | % | SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.bin ||\*CORFL\*.hdr| ENVI corrected reflectance header file  | - | SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.hdr ||\*\.png| Reflectance PNG quicklook  | - |  SISTER_AVNG\_L2A\_CORFL\_20220502T180901\_001.png |
## Algorithm registration

	from maap.maap import MAAP
	maap = MAAP(maap_host="sister-api.imgspec.org")
	
	rfl_correct_alg = {
	    "script_command": "sister-reflect_correct/pge_run.sh",
	    "repo_url": "https://github.com/EnSpec/sister-reflect_correct.git",
	    "algorithm_name":"sister-reflect_correct",
	    "code_version":"2.0.0",
	    "algorithm_description":"Topo, BRDF and glint correction",
	    "environment_name":"ubuntu",
	    "disk_space":"70GB",
	    "queue": "sister-job_worker-16gb",
	    "build_command": "sister-reflect_correct/install.sh",
	    "docker_container_url": docker_container_url,
	    "algorithm_params":[
	        {
	            "field": "l1b_granule",
	            "type": "file"
	        },
	        {
	            "field": "l2a_granule",
	            "type": "file"
	        },
	          {
	            "field": "CRID",
	            "type": "config",
	            "default": "000"
	        }
	    ]
	}
	response = maap.registerAlgorithm(arg=rfl_correct_alg)## Example	rfl_corr_job_response = maap.submitJob(	    algo_id="sister-reflect_correct",	    version="2.0.0",	    l1b_granule=l1b_granule,	    l2a_granule=l2a_granule,
	    crid = '000',	    publish_to_cmr=False,	    cmr_metadata={},	    queue="sister-job_worker-16gb",	    identifier='SISTER_AVNG_L2A_CORFL_20220502T180901_001')