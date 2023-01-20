run_dir=$('pwd')
imgspec_dir=$(cd "$(dirname "$0")" ; pwd -P)
pge_dir=$(dirname ${imgspec_dir})

# Need to do custom install to prevent dependency errors
conda create -y --name sister python=3.7
source activate sister

pip install -r ${pge_dir}/requirements.txt

git clone https://github.com/EnSpec/hytools.git
cd hytools
pip install .
