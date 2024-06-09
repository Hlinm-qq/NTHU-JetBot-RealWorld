import torch

path = "../../unet/unet/checkpoints/checkpoint_epoch5_64.pth"
save_path = path[:-4] + "_jetbot.pth"

state_dict = torch.load(path, map_location="cpu")
torch.save(state_dict, save_path, _use_new_zipfile_serialization=False)