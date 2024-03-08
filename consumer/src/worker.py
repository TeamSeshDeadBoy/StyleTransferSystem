import base64
from dotenv.main import load_dotenv
import numpy as np
import random
import os
from PIL import Image
import torch
from diffusers.utils import load_image
from diffusers import EulerDiscreteScheduler
from photomaker import PhotoMakerStableDiffusionXLPipeline



###-----------DEVELOPMENT-ONLY-------------------
load_dotenv()
volume_path = os.environ["VOLUME_ADRESS"]
# change .env to use this (for cpu development)
def picture(foldername):
    """Returns the pictures in input folder in b64 encoding
    Args:
        foldername (str): path of input folder
    Returns:
        arr[str]: array of b64 encoded images
    """
    encoded_strings_arr = []
    for filename in os.listdir('/data/user_data/'+foldername):
        with open(volume_path+foldername+'/'+filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_strings_arr.append(encoded_string)
    return encoded_strings_arr

### IN-DEV: for further pay-as-you-go usage
# def image_grid(imgs, rows, cols, size_after_resize):
#     assert len(imgs) == rows*cols
#     w, h = size_after_resize, size_after_resize
#     grid = Image.new('RGB', size=(cols*w, rows*h))
#     grid_w, grid_h = grid.size
#     for i, img in enumerate(imgs):
#         img = img.resize((w,h))
#         grid.paste(img, box=(i%cols*w, i//cols*h))
#     return grid
###--------------------------------------------



### ENVIRONMENT VARIABLES INITIALIZATION
load_dotenv()
volume_path = os.environ["VOLUME_ADRESS"]
photomaker_path = os.environ["PHOTOMAKER_PATH"]
base_model_path = os.environ["BASE_MODEL_PATH"]
mode = os.environ["MODE"]
device = "cuda"

if mode == "PROD":
    ### BASE MODEL LOADING
    pipe = PhotoMakerStableDiffusionXLPipeline.from_pretrained(
        base_model_path,  # can change to any base model based on SDXL from huggingface_hub
        torch_dtype=torch.bfloat16, 
        use_safetensors=True, 
        variant="fp16"
    ).to(device)
    pipe.enable_vae_slicing()


    ### PHOTOMAKER CHECKPOINT LOADING
    pipe.load_photomaker_adapter(
        os.path.dirname(photomaker_path),
        subfolder="",
        weight_name=os.path.basename(photomaker_path),
        trigger_word="img"  # define the trigger word
    )     
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.fuse_lora()


### PRODUCTION: GENERATE 1 IMAGE BASED ON INPUT FOLDER NAME
def picture_prod(foldername, idx_person, user_prompt="sci-fi, closeup portrait photo of a man img wearing the sunglasses in Iron man suit, face, slim body, high quality, film grain", num_images_user=1, num_steps_user=50, style_strength_user=20):
    """Generates picture with photomaker pipeline.
    Args:
        foldername (str): A name of folder in the mounted volume "data/user_data"
        idx_person (int): index of user's chosen person (subfolder of /data/userdata/person_{i})
        num_images_user (int): a number of images generated per prompt (1-4 recomended)
        num_steps_user (int): number of inference steps
        style_strength_user (int): percent of style strength (0-100%)

    Returns:
        str: A string path of output folder
    """
    ## getting images
    image_basename_list = os.listdir('/data/user_data/'+foldername+"/person_"+str(idx_person))
    image_path_list = sorted([os.path.join('/data/user_data/'+foldername+"/person_"+str(idx_person), basename) for basename in image_basename_list])

    ## getting id from images
    input_id_images = []
    for image_path in image_path_list:
        input_id_images.append(load_image(image_path))

    ## utils initialization
    negative_prompt = "(asymmetry, worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch), open mouth"
    generator = torch.Generator(device=device).manual_seed(np.random.randint(low=10, high=99))

    ## starting merge step evaluation
    start_merge_step = int(float(style_strength_user) / 100 * num_steps_user)
    if start_merge_step > 30:
        start_merge_step = 30

    ## pipeline initialization with customization
    images = pipe(
        prompt=user_prompt,
        input_id_images=input_id_images,
        negative_prompt=negative_prompt,
        num_images_per_prompt=num_images_user,
        num_inference_steps=num_steps_user,
        start_merge_step=start_merge_step,
        generator=generator,
    ).images
    
    ## outputs saved to given input folder
    for idx, image in enumerate(images):
            output_path = '/data/user_data/'+foldername + "/" + f"image_{idx}.png"
            image.save(output_path)
    return output_path

