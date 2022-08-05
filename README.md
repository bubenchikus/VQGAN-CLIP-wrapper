# VQGAN-CLIP-wrapper

## Setup process:
```sh
git clone 'https://github.com/bubenchikus/VQGAN-CLIP-wrapper'
cd VQGAN-CLIP-wrapper
mkdir ./checkpoints
curl -L -o ./checkpoints/vqgan_imagenet_f16_16384.yaml -C - 'https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/files/?p=%2Fconfigs%2Fmodel.yaml&dl=1' #ImageNet 16384
curl -L -o ./checkpoints/vqgan_imagenet_f16_16384.ckpt -C - 'https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/files/?p=%2Fckpts%2Flast.ckpt&dl=1' #ImageNet 16384

conda create --name vqgan python=3.9
conda activate vqgan

pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install ftfy regex tqdm omegaconf pytorch-lightning IPython kornia imageio imageio-ffmpeg einops torch_optimizer

git clone 'https://github.com/nerdyrodent/VQGAN-CLIP'
git clone 'https://github.com/openai/CLIP' ./VQGAN-CLIP/CLIP
git clone 'https://github.com/CompVis/taming-transformers' ./VQGAN-CLIP/taming-transformers
```
