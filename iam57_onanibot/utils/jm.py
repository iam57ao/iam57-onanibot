import os

import jmcomic
import yaml
from PIL import Image

from jmcomic.jm_entity import JmAlbumDetail

CONFIG = "jm_config.yml"
JM_CONFIG = jmcomic.JmOption.from_file(CONFIG)

with open(CONFIG, "r", encoding="utf8") as f:
    CONFIG_DATA = yaml.load(f, Loader=yaml.FullLoader)
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
    # 对数字进行排序
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
