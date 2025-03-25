import os
import yaml
import jmcomic

from typing import Optional
from jmcomic.jm_entity import JmAlbumDetail
from nonebot import get_driver, get_plugin_config
from PIL import Image

from ..configs.jm_config import JMConfig

driver = get_driver()
jm_plugin_config = get_plugin_config(JMConfig)

CONFIG_PATH = jm_plugin_config.config_path
JM_CONFIG = jmcomic.JmOption.from_file(CONFIG_PATH)
COMIC_PATH: Optional[str] = None


@driver.on_startup
async def set_base_dir():
    if jm_plugin_config.use_default_comic_dir:
        with open(CONFIG_PATH, "r", encoding="utf8") as jm_config_file:
            config_data = yaml.load(jm_config_file, Loader=yaml.FullLoader)
        config_data["dir_rule"]["base_dir"] = os.path.abspath(os.path.join(os.getcwd(), "data/comics"))
        with open(CONFIG_PATH, "w", encoding="utf8") as jm_config_file:
            yaml.safe_dump(config_data, jm_config_file)
    with open(CONFIG_PATH, "r", encoding="utf8") as jm_config_file:
        CONFIG_DATA = yaml.load(jm_config_file, Loader=yaml.FullLoader)
        global COMIC_PATH
        COMIC_PATH = CONFIG_DATA["dir_rule"]["base_dir"]


def download_comic(jm_id: str) -> JmAlbumDetail:
    comic, _ = jmcomic.download_album(jm_id, JM_CONFIG)
    return comic


def all_to_pdf(input_folder, pdf_path, pdf_name):
    path = input_folder
    sub_dir = []
    image = []
    sources = []
    output = None
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                sub_dir.append(int(entry.name))
    sub_dir.sort()
    for i in sub_dir:
        with os.scandir(path + "/" + str(i)) as entries:
            for entry in entries:
                if entry.is_dir():
                    print("这一级不应该有自录")
                if entry.is_file():
                    image.append(path + "/" + str(i) + "/" + entry.name)
    if "jpg" in image[0]:
        output = Image.open(image[0])
        image.pop(0)
    for file in image:
        if "jpg" in file:
            img_file = Image.open(file)
            if img_file.mode == "RGB":
                img_file = img_file.convert("RGB")
            sources.append(img_file)
    pdf_file_path = pdf_path + "/" + pdf_name
    if not pdf_file_path.endswith(".pdf"):
        pdf_file_path = pdf_file_path + ".pdf"
    output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)
    output.close()


def get_comic_file_path(comic: JmAlbumDetail):
    comic_file_path = os.path.join(COMIC_PATH + '/' + comic.title + ".pdf")
    if not os.path.exists(comic_file_path):
        print(f"开始转换: {comic.title}")
        all_to_pdf(COMIC_PATH + "/" + comic.title, COMIC_PATH, comic.title)
    return comic_file_path
