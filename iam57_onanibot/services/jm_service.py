from pathlib import Path

import yaml
from PIL import Image
from jmcomic import JmAlbumDetail, JmOption
from nonebot import get_plugin_config, logger

from ..configs.jm_config import JMConfig


class JMServiceMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class JMService(metaclass=JMServiceMeta):
    def __init__(self):
        self.jm_client = JmOption.default().new_jm_client()
        self.jm_config = get_plugin_config(JMConfig)
        self.jm_option = JmOption.from_file(self.jm_config.jm_option_file_path)
        self.jm_comic_path = None
        self.__set_comic_dir()

    def get_comic_detail(self, jm_id: str) -> JmAlbumDetail:
        return self.jm_client.get_album_detail(jm_id)

    def download_comic_and_get_pdf_file_path(self, comic: JmAlbumDetail):
        comic_file_path = self.jm_comic_path / f"{comic.title}.pdf"
        if not Path.exists(comic_file_path):
            self.jm_option.download_album(comic.album_id)
            self.all_to_pdf(self.jm_comic_path / comic.title, self.jm_comic_path, comic.title)
        return str(comic_file_path)

    def __set_comic_dir(self):
        with open(self.jm_config.jm_option_file_path, "r", encoding="utf8") as jm_option_file:
            jm_option_data = yaml.safe_load(jm_option_file)
        jm_comic_path = jm_option_data["dir_rule"]["base_dir"]
        if self.jm_config.use_default_comic_dir:
            jm_comic_path = Path.cwd() / "data" / "comics"
            jm_option_data["dir_rule"]["base_dir"] = str(jm_comic_path)
            with open(self.jm_config.jm_option_file_path, "w", encoding="utf8") as jm_option_file:
                yaml.safe_dump(jm_option_data, jm_option_file, sort_keys=False, allow_unicode=True)
        self.jm_comic_path = jm_comic_path

    @staticmethod
    def all_to_pdf(input_dir: str, output_dir: str, output_filename: str):
        """
        扫描 input_dir 下的子文件夹，收集所有 .jpg 图片并合并导出为 PDF。

        :param input_dir:       存放图片的文件夹路径
        :param output_dir:      PDF 输出目录
        :param output_filename: PDF 文件名（可不带 .pdf 后缀）
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        sub_dirs = []
        for entry in input_path.iterdir():
            if entry.is_dir():
                try:
                    sub_dirs.append(int(entry.name))
                except ValueError:
                    logger.warning(f"子目录名非数字：{entry.name}，已跳过。")
        sub_dirs.sort()
        images = []
        for subdir in sub_dirs:
            subdir_path = input_path / str(subdir)
            if not subdir_path.is_dir():
                logger.warning(f"目录不存在或不是文件夹：{subdir_path}，已跳过。")
                continue
            for sub_entry in subdir_path.iterdir():
                if sub_entry.is_dir():
                    logger.warning(f"在目录 {subdir_path} 下发现了意外的子目录: {sub_entry.name}")
                elif sub_entry.is_file() and sub_entry.suffix.lower() == ".jpg":
                    images.append(sub_entry)
        if not images:
            logger.error(f"未在目录 {input_path} 下找到任何 .jpg 图片，无法生成 PDF。")
            return
        main_image_path = images[0]
        main_image = Image.open(main_image_path)
        if main_image.mode != "RGB":
            main_image = main_image.convert("RGB")
        extra_images = []
        for img_path in images[1:]:
            img = Image.open(img_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            extra_images.append(img)
        pdf_file_path = output_path / output_filename
        if pdf_file_path.suffix.lower() != ".pdf":
            pdf_file_path = pdf_file_path.with_suffix(".pdf")
        pdf_file_path.parent.mkdir(parents=True, exist_ok=True)
        main_image.save(pdf_file_path, "PDF", save_all=True, append_images=extra_images)
        logger.info(f"PDF 文件已生成：{pdf_file_path}")
        main_image.close()
        for img in extra_images:
            img.close()
