cd "$(dirname "$0")"; D=$PWD; export PYTHONPATH=$D:$D/GPT_SoVITS _CUDA_VISIBLE_DEVICES=0 is_half=False hz=25hz version=v2
../gsvenv/bin/python -s GPT_SoVITS/s2_train.py --config TEMP/tmp_s2.json > s2.log 2>&1; echo S2EXIT $? >> s2.log
../gsvenv/bin/python -s GPT_SoVITS/s1_train.py --config_file TEMP/tmp_s1.yaml > s1.log 2>&1; echo S1EXIT $? >> s1.log
