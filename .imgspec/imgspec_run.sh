#!/bin/bash

imgspec_dir=$(cd "$(dirname "$0")" ; pwd -P)
pge_dir=$(dirname ${imgspec_dir})

source activate sister

mkdir output

for a in `ls -1 input/*.tar.gz`; do tar -xzvf $a -C input; done

rfl_path=$(ls input/*/*RFL* | grep -v '.hdr')
obs_path=$(ls input/*/*OBS* | grep -v '.hdr')

rfl_name=$(basename $rfl_path)
output_base_name=$(echo "${rfl_name/L2A_RSRFL/"L2A_CORFL"}")


echo "Found input RFL file: $rfl_path"
echo "Found input OBS file: $obs_path"

if [[ $rfl_name == SISTER_AV* ]]; then
    corrections="--topo --brdf --glint"
else;
    corrections="--glint"
fi

echo "Applying the following corrections: $corrections"

mkdir output/${output_base_name}

python ${pge_dir}/reflect_correct.py $rfl_path $obs_path output/${output_base_name} $corrections

#Rename, compress and cleanup outputs
cd output

mv */*_RSRFL*.hdr $output_base_name/$output_base_name.hdr
mv */*_RSRFL* $output_base_name/$output_base_name

#Create metadata
python ${imgspec_dir}/generate_metadata.py */*CORFL*.hdr .

# Create quicklook
python ${imgspec_dir}/generate_quicklook.py $(ls */*CORFL* | grep -v '.hdr') .

tar -czvf ${output_base_name}.tar.gz $output_base_name
rm -r $output_base_name

cp ../run.log ${output_base_name}.log
