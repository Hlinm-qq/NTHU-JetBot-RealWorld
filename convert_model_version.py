import torch

path = "./unet/checkpoints/checkpoint_epoch5.pth"
sava_path = "./unet/checkpoints/checkpoint_epoch5_jetbot.pth"

state_dict = torch.load(path, map_location="cpu")
torch.save(state_dict, sava_path, _use_new_zipfile_serialization=False)