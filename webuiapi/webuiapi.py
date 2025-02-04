import json
import requests
import io
import base64
from PIL import Image
from dataclasses import dataclass
from enum import Enum

@dataclass
class WebUIApiResult:
    images: list
    parameters: dict
    info: dict

    @property
    def image(self):
        return self.images[0]

def b64_img(image: Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = 'data:image/png;base64,' + str(base64.b64encode(buffered.getvalue()), 'utf-8')
    return img_base64

class WebUIApi:
    def __init__(self,
                 host='127.0.0.1',
                 port=7860,
                 baseurl=None,
                 sampler='Euler a',
                 steps=20,
                 use_https=False):
        if baseurl is None:
            if use_https:
                baseurl = f'https://{host}:{port}/sdapi/v1'
            else:
                baseurl = f'http://{host}:{port}/sdapi/v1'

        self.baseurl = baseurl
        self.default_sampler = sampler
        self.default_steps = steps

        self.session = requests.Session()

    def set_auth(self, username, password):
        self.session.auth = (username, password)

    def _to_api_result(self, response):

        if response.status_code != 200:
            raise RuntimeError(response.status_code, response.text)

        r = response.json()
        images = []
        if 'images' in r.keys():
            images = [Image.open(io.BytesIO(base64.b64decode(i))) for i in r['images']]
        elif 'image' in r.keys():
            images = [Image.open(io.BytesIO(base64.b64decode(r['image'])))]

        info = ''
        if 'info' in r.keys():
            try:
                info = json.loads(r['info'])
            except:
                info = r['info']
        elif 'html_info' in r.keys():
            info = r['html_info']

        parameters = ''
        if 'parameters' in r.keys():
            parameters = r['parameters']

        return WebUIApiResult(images, parameters, info)

    def txt2img(self,
                enable_hr=False,
                denoising_strength=0.0,
                firstphase_width=0,
                firstphase_height=0,
                prompt="",
                styles=[],
                seed=-1,
                subseed=-1,
                subseed_strength=0.0,
                seed_resize_from_h=-1,
                seed_resize_from_w=-1,
                batch_size=1,
                n_iter=1,
                cfg_scale=7.0,
                width=512,
                height=512,
                restore_faces=False,
                tiling=False,
                negative_prompt="",
                eta=0,
                s_churn=0,
                s_tmax=0,
                s_tmin=0,
                s_noise=1,
                override_settings={},
                override_settings_restore_afterwards=True,
                sampler_name=None,  # use this instead of sampler_index
                sampler_index=None,
                steps=None,
                script_name=None,
                script_args=None  # List of arguments for the script "script_name"
                ):
        if sampler_index is None:
            sampler_index = self.default_sampler
        if sampler_name is None:
            sampler_name = self.default_sampler
        if steps is None:
            steps = self.default_steps
        if script_args is None:
            script_args = []

        payload = {
            "enable_hr": enable_hr,
            "denoising_strength": denoising_strength,
            "firstphase_width": firstphase_width,
            "firstphase_height": firstphase_height,
            "prompt": prompt,
            "styles": styles,
            "seed": seed,
            "subseed": subseed,
            "subseed_strength": subseed_strength,
            "seed_resize_from_h": seed_resize_from_h,
            "seed_resize_from_w": seed_resize_from_w,
            "batch_size": batch_size,
            "n_iter": n_iter,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "tiling": tiling,
            "negative_prompt": negative_prompt,
            "eta": eta,
            "s_churn": s_churn,
            "s_tmax": s_tmax,
            "s_tmin": s_tmin,
            "s_noise": s_noise,
            "override_settings": override_settings,
            "override_settings_restore_afterwards": override_settings_restore_afterwards,
            "sampler_name": sampler_name,
            "sampler_index": sampler_index,
            "script_name": script_name,
            "script_args": script_args
        }
        response = self.session.post(url=f'{self.baseurl}/txt2img', json=payload)
        return self._to_api_result(response)

    def img2img(self,
                images=[],  # list of PIL Image
                mask_image=None,  # PIL Image mask
                resize_mode=0,
                denoising_strength=0.75,
                mask_blur=4,
                inpainting_fill=0,
                inpaint_full_res=True,
                inpaint_full_res_padding=0,
                inpainting_mask_invert=0,
                initial_noise_multiplier=0,
                prompt="",
                styles=[],
                seed=-1,
                subseed=-1,
                subseed_strength=0,
                seed_resize_from_h=-1,
                seed_resize_from_w=-1,
                batch_size=1,
                n_iter=1,
                cfg_scale=7.0,
                width=512,
                height=512,
                restore_faces=False,
                tiling=False,
                negative_prompt="",
                eta=0,
                s_churn=0,
                s_tmax=0,
                s_tmin=0,
                s_noise=1,
                override_settings={},
                override_settings_restore_afterwards=True,
                include_init_images=False,
                steps=None,
                sampler_name=None,  # use this instead of sampler_index
                sampler_index=None,
                script_name=None,
                script_args=None  # List of arguments for the script "script_name"
                ):
        if sampler_name is None:
            sampler_name = self.default_sampler
        if sampler_index is None:
            sampler_index = self.default_sampler
        if steps is None:
            steps = self.default_steps
        if script_args is None:
            script_args = []

        payload = {
            "init_images": [b64_img(x) for x in images],
            "resize_mode": resize_mode,
            "denoising_strength": denoising_strength,
            "mask_blur": mask_blur,
            "inpainting_fill": inpainting_fill,
            "inpaint_full_res": inpaint_full_res,
            "inpaint_full_res_padding": inpaint_full_res_padding,
            "inpainting_mask_invert": inpainting_mask_invert,
            "initial_noise_multiplier": initial_noise_multiplier,
            "prompt": prompt,
            "styles": styles,
            "seed": seed,
            "subseed": subseed,
            "subseed_strength": subseed_strength,
            "seed_resize_from_h": seed_resize_from_h,
            "seed_resize_from_w": seed_resize_from_w,
            "batch_size": batch_size,
            "n_iter": n_iter,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "restore_faces": restore_faces,
            "tiling": tiling,
            "negative_prompt": negative_prompt,
            "eta": eta,
            "s_churn": s_churn,
            "s_tmax": s_tmax,
            "s_tmin": s_tmin,
            "s_noise": s_noise,
            "override_settings": override_settings,
            "override_settings_restore_afterwards": override_settings_restore_afterwards,
            "sampler_name": sampler_name,
            "sampler_index": sampler_index,
            "include_init_images": include_init_images,
            "script_name": script_name,
            "script_args": script_args
        }
        if mask_image is not None:
            payload['mask'] = b64_img(mask_image)

        response = self.session.post(url=f'{self.baseurl}/img2img', json=payload)
        return self._to_api_result(response)

    def extra_single_image(self,
                           image,  # PIL Image
                           resize_mode=0,
                           show_extras_results=True,
                           gfpgan_visibility=0,
                           codeformer_visibility=0,
                           codeformer_weight=0,
                           upscaling_resize=2,
                           upscaling_resize_w=512,
                           upscaling_resize_h=512,
                           upscaling_crop=True,
                           upscaler_1="None",
                           upscaler_2="None",
                           extras_upscaler_2_visibility=0,
                           upscale_first=False,
                           ):
        payload = {
            "resize_mode": resize_mode,
            "show_extras_results": show_extras_results,
            "gfpgan_visibility": gfpgan_visibility,
            "codeformer_visibility": codeformer_visibility,
            "codeformer_weight": codeformer_weight,
            "upscaling_resize": upscaling_resize,
            "upscaling_resize_w": upscaling_resize_w,
            "upscaling_resize_h": upscaling_resize_h,
            "upscaling_crop": upscaling_crop,
            "upscaler_1": upscaler_1,
            "upscaler_2": upscaler_2,
            "extras_upscaler_2_visibility": extras_upscaler_2_visibility,
            "upscale_first": upscale_first,
            "image": b64_img(image),
        }

        response = self.session.post(url=f'{self.baseurl}/extra-single-image', json=payload)
        return self._to_api_result(response)

    def extra_batch_images(self,
                           images,  # list of PIL images
                           name_list=None,  # list of image names
                           resize_mode=0,
                           show_extras_results=True,
                           gfpgan_visibility=0,
                           codeformer_visibility=0,
                           codeformer_weight=0,
                           upscaling_resize=2,
                           upscaling_resize_w=512,
                           upscaling_resize_h=512,
                           upscaling_crop=True,
                           upscaler_1="None",
                           upscaler_2="None",
                           extras_upscaler_2_visibility=0,
                           upscale_first=False,
                           ):
        if name_list is not None:
            if len(name_list) != len(images):
                raise RuntimeError('len(images) != len(name_list)')
        else:
            name_list = [f'image{i + 1:05}' for i in range(len(images))]
        images = [b64_img(x) for x in images]

        image_list = []
        for name, image in zip(name_list, images):
            image_list.append({
                "data": image,
                "name": name
            })

        payload = {
            "resize_mode": resize_mode,
            "show_extras_results": show_extras_results,
            "gfpgan_visibility": gfpgan_visibility,
            "codeformer_visibility": codeformer_visibility,
            "codeformer_weight": codeformer_weight,
            "upscaling_resize": upscaling_resize,
            "upscaling_resize_w": upscaling_resize_w,
            "upscaling_resize_h": upscaling_resize_h,
            "upscaling_crop": upscaling_crop,
            "upscaler_1": upscaler_1,
            "upscaler_2": upscaler_2,
            "extras_upscaler_2_visibility": extras_upscaler_2_visibility,
            "upscale_first": upscale_first,
            "imageList": image_list,
        }

        response = self.session.post(url=f'{self.baseurl}/extra-batch-images', json=payload)
        return self._to_api_result(response)

    # XXX 500 error (2022/12/26)
    def png_info(self, image):
        payload = {
            "image": b64_img(image),
        }

        response = self.session.post(url=f'{self.baseurl}/png-info', json=payload)
        return self._to_api_result(response)

    # XXX always returns empty info (2022/12/26)
    def interrogate(self, image):
        payload = {
            "image": b64_img(image),
        }

        response = self.session.post(url=f'{self.baseurl}/interrogate', json=payload)
        return self._to_api_result(response)

    def get_options(self):
        response = self.session.get(url=f'{self.baseurl}/options')
        return response.json()

    # working (2022/11/21)
    def set_options(self, options):
        response = self.session.post(url=f'{self.baseurl}/options', json=options)
        return response.json()

    def get_cmd_flags(self):
        response = self.session.get(url=f'{self.baseurl}/cmd-flags')
        return response.json()
    def get_samplers(self):        
        response = self.session.get(url=f'{self.baseurl}/samplers')
        return response.json()
    def get_upscalers(self):        
        response = self.session.get(url=f'{self.baseurl}/upscalers')
        return response.json()
    def get_sd_models(self):        
        response = self.session.get(url=f'{self.baseurl}/sd-models')
        return response.json()
    def get_hypernetworks(self):        
        response = self.session.get(url=f'{self.baseurl}/hypernetworks')
        return response.json()
    def get_face_restorers(self):        
        response = self.session.get(url=f'{self.baseurl}/face-restorers')
        return response.json()
    def get_realesrgan_models(self):        
        response = self.session.get(url=f'{self.baseurl}/realesrgan-models')
        return response.json()
    def get_prompt_styles(self):        
        response = self.session.get(url=f'{self.baseurl}/prompt-styles')
        return response.json()
    def get_artist_categories(self):        
        response = self.session.get(url=f'{self.baseurl}/artist-categories')
        return response.json()
    def get_artists(self):        
        response = self.session.get(url=f'{self.baseurl}/artists')
        return response.json()
    def refresh_checkpoints(self):
        response = self.session.post(url=f'{self.baseurl}/refresh-checkpoints')
        return response.json()

    def get_endpoint(self, endpoint, baseurl):
        if baseurl:
            return f'{self.baseurl}/{endpoint}'
        else:
            from urllib.parse import urlparse, urlunparse
            parsed_url = urlparse(self.baseurl)
            basehost = parsed_url.netloc
            parsed_url2 = (parsed_url[0], basehost, endpoint, '', '', '')
            return urlunparse(parsed_url2)
    def custom_get(self, endpoint, baseurl=True):
        url = self.get_endpoint(endpoint, baseurl)
        response = self.session.get(url=url)
        return response.json()
    def custom_post(self, endpoint, payload={}, baseurl=True):
        url = self.get_endpoint(endpoint, baseurl)
        response = self.session.post(url=url, json=payload)
        return self._to_api_result(response)

    def util_get_model_names(self):
        return sorted([x['title'] for x in self.get_sd_models()])
    def util_set_model(self, name, find_closest=True):
        name = name.lower()
        models = self.util_get_model_names()
        found_model = None
        if name in models:
            found_model = name
        elif find_closest:
            import difflib
            def str_simularity(a, b):
                return difflib.SequenceMatcher(None, a, b).ratio()
            max_sim = 0.0
            max_model = models[0]
            for model in models:
                sim = str_simularity(name, model)
                if sim >= max_sim:
                    max_sim = sim
                    max_model = model
            found_model = max_model
        if found_model:
            print(f'loading {found_model}')
            options = {}
            options['sd_model_checkpoint'] = found_model
            self.set_options(options)
            print(f'model changed to {found_model}')
        else:
            print('model not found')
    def util_get_current_model(self):
        return self.get_options()['sd_model_checkpoint']


class Upscaler(str, Enum):
    none = 'None'
    Lanczos = 'Lanczos'
    Nearest = 'Nearest'
    LDSR = 'LDSR'
    BSRGAN = 'BSRGAN'
    ESRGAN_4x = 'ESRGAN_4x'
    R_ESRGAN_General_4xV3 = 'R-ESRGAN General 4xV3'
    ScuNET_GAN = 'ScuNET GAN'
    ScuNET_PSNR = 'ScuNET PSNR'
    SwinIR_4x = 'SwinIR 4x'
