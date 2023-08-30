import diffusers
from diffusers import DDPMPipeline, DDPMScheduler, UNet2DModel
import torch
import numpy as np
import cv2

def load_model(path):
    model = UNet2DModel.from_pretrained(path)
    return model
    # (
    #         sample_size=512,
    #         in_channels=3,
    #         out_channels=3,
    #         layers_per_block=2,
    #         block_out_channels=(128, 128, 256, 256, 512, 512),
    #         down_block_types=(
    #             "DownBlock2D",
    #             "DownBlock2D",
    #             "DownBlock2D",
    #             "DownBlock2D",
    #             "AttnDownBlock2D",
    #             "DownBlock2D",
    #         ),
    #         up_block_types=(
    #             "UpBlock2D",
    #             "AttnUpBlock2D",
    #             "UpBlock2D",
    #             "UpBlock2D",
    #             "UpBlock2D",
    #             "UpBlock2D",
    #         ),
    #     )
    # weight = torch.load(path)
    # model.load_state_dict(weight)
    # return model

def save_images(images, path):
    images = images * 255
    b, h, w, c = images.shape
    images = np.reshape(b*h, w, c)
    cv2.imwrite(path, images)

def main():
    device = 'cuda:0'
    eval_batch_size = 1
    ddpm_num_steps = 1000
    ddpm_num_inference_steps = 1000
    ddpm_beta_schedule = "linear"
    path = './celeba_hq-1024/checkpoint-49000/unet/diffusion_pytorch_model.safetensors'
    path = './celeba_hq-1024/checkpoint-49000/unet'
    unet = load_model(path).to(device)
    noise_scheduler = DDPMScheduler(num_train_timesteps=ddpm_num_steps, 
                                    beta_schedule=ddpm_beta_schedule)
    image_save_path = './test.jpg'

    pipeline = DDPMPipeline(
                    unet=unet,
                    scheduler=noise_scheduler
                )
    
    generator = torch.Generator(device=pipeline.device).manual_seed(0)
                # run pipeline in inference (sample random noise and denoise)
    images = pipeline(
                    generator=generator,
                    batch_size=eval_batch_size,
                    num_inference_steps=ddpm_num_inference_steps,
                    output_type="numpy",
                ).images
    save_images(images, image_save_path)
    
    


if __name__ == '__main__':
    main()
