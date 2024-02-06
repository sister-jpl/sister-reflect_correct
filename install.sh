pge_dir=$(cd "$(dirname "$0")" ; pwd -P)

# Need to do custom install to prevent dependency errors
conda create -y --name sister python=3.8
source activate sister
pip install pystac==1.8.4
pip install spectral==0.23.1

git clone https://github.com/EnSpec/hytools.git -b 1.5.0
cd hytools
pip install .
