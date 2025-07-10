import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import os
from io import BytesIO

from .codeformer.basicsr.archs.codeformer_arch import CodeFormer
from .codeformer.facelib.utils.face_restoration_helper import FaceRestoreHelper
from .codeformer.basicsr.utils.download_util import load_file_from_url
from .codeformer.basicsr.utils import imwrite

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load model hanya sekali
net = CodeFormer(dim_embd=512, codebook_size=1024, n_head=8, n_layers=9, 
                 connect_list=['32', '64', '128', '256']).to(device)
ckpt_path = os.path.join('app', 'CodeFormer', 'weights', 'CodeFormer', 'codeformer.pth')
net.load_state_dict(torch.load(ckpt_path, map_location=device)['params_ema'])
net.eval()

# transform
to_tensor = transforms.ToTensor()
to_pil = transforms.ToPILImage()

def enhance_image(pil_image):
    face_helper = FaceRestoreHelper(upscale_factor=1, face_size=512, 
                                     crop_ratio=(1, 1), det_model=None, save_ext='png')
    img_np = np.array(pil_image)
    img_np = img_np[:, :, ::-1]  # RGB ke BGR
    face_helper.read_image(img_np)
    face_helper.get_face_landmarks_5()
    face_helper.align_warp_face()

    if len(face_helper.cropped_faces) == 0:
        return pil_image  # ga ada muka? balikin asli aja

    restored_faces = []
    for face in face_helper.cropped_faces:
        face_tensor = to_tensor(face).unsqueeze(0).to(device)
        with torch.no_grad():
            output = net(face_tensor, w=0.7, adain=True)[0]
            output = output.squeeze().cpu().clamp(0, 1)
        restored_faces.append(to_pil(output))

    # Gabungin hasil
    face_helper.add_restored_face(restored_faces)
    restored_img = face_helper.get_restored_image()

    pil_result = Image.fromarray(restored_img[:, :, ::-1])  # BGR ke RGB
    return pil_result
