#!/bin/bash

imgspec_dir=$(cd "$(dirname "$0")" ; pwd -P)
pge_dir=$(dirname ${imgspec_dir})

source activate sister

mkdir output

for a in `ls -1 input/*.tar.gz`; do tar -xzvf $a -C input; done

rfl_file=$(ls input/*/*rfl)
file_base=$(basename $rfl_file)

if [[ $file_base == f* ]]; then
    output_prefix=$(echo $file_base | cut -c1-16)
    obs_file=$(ls input/*/*obs_ort)
    corrections="--topo --brdf --glint"
elif [[ $file_base == ang* ]]; then
    output_prefix=$(echo $file_base | cut -c1-18)
    obs_file=$(ls input/*/*obs_ort)
    corrections="--topo --brdf --glint"
elif [[ $file_base == PRS* ]]; then
    output_prefix=$(echo $file_base | cut -c1-38)
    obs_file=$(ls input/*/*obs_prj)
    corrections="--glint"
elif [[ $file_base == DESIS* ]]; then
    output_prefix=$(echo $file_base | cut -c1-44)
    obs_file=$(ls input/*/*obs_prj)
    corrections="--glint"
fi

out_dir=${output_prefix}_crfl
mkdir output/${out_dir}

python ${pge_dir}/reflect_correct.py $rfl_file $obs_file output/${out_dir} $corrections

cd output
tar -czvf ${out_dir}.tar.gz $out_dir
rm -r $out_dir
