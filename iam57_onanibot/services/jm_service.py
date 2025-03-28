from pathlib import Path
import tempfile

from jmcomic import JmAlbumDetail, JmOption
from nonebot import get_plugin_config, logger
from PIL import Image
from PyPDF2 import PdfMerger
import yaml

from iam57_onanibot.configs.jm_config import JMConfig


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
            self.all_to_pdf(self.jm_comic_path / comic.title, comic_file_path)
        return str(comic_file_path)

    def __set_comic_dir(self):
        with open(
            self.jm_config.jm_option_file_path, encoding="utf8"
        ) as jm_option_file:
            jm_option_data = yaml.safe_load(jm_option_file)
        jm_comic_path = jm_option_data["dir_rule"]["base_dir"]
        if self.jm_config.use_default_comic_dir:
            jm_comic_path = Path.cwd() / "data" / "comics"
            jm_option_data["dir_rule"]["base_dir"] = str(jm_comic_path)
            with open(
                self.jm_config.jm_option_file_path, "w", encoding="utf8"
            ) as jm_option_file:
                yaml.safe_dump(
                    jm_option_data, jm_option_file, sort_keys=False, allow_unicode=True
                )
        self.jm_comic_path = jm_comic_path

    @staticmethod
    def all_to_pdf(input_dir: str, output_pdf_path: str, batch_size=50):
        """
        将文件夹中的图片转换为PDF，采用分段处理避免内存溢出

        Args:
            input_dir (str): 输入文件夹路径
            output_pdf_path (str): 输出PDF文件路径
            batch_size (int): 每批处理的图片数量
        """
        try:
            logger.info(f"开始处理文件夹：{input_dir}")
            images = []
            input_path = Path(input_dir)
            for entry in input_path.iterdir():  # 使用 iterdir() 替代 os.scandir()
                if entry.is_file() and entry.suffix.lower() in {
                    ".jpg",
                    ".jpeg",
                    ".png",
                }:
                    images.append(str(entry))
            if not images:
                logger.warning(f"在 {input_dir} 中没有找到图片")
                return
            images.sort()
            total_images = len(images)
            logger.info(f"找到 {total_images} 张图片")
            with tempfile.TemporaryDirectory() as temp_dir:
                batch_pdfs = []
                for i in range(0, total_images, batch_size):
                    batch_images = images[i : i + batch_size]
                    batch_num = i // batch_size + 1
                    total_batches = (total_images + batch_size - 1) // batch_size
                    logger.info(f"处理第 {batch_num}/{total_batches} 批图片")
                    try:
                        first_image = Image.open(batch_images[0])
                        if first_image.mode != "RGB":
                            first_image = first_image.convert("RGB")
                        remaining_images = []
                        for img_path in batch_images[1:]:
                            img = Image.open(img_path)
                            if img.mode != "RGB":
                                img = img.convert("RGB")
                            remaining_images.append(img)
                        temp_pdf = str(Path(temp_dir) / f"temp_batch_{batch_num}.pdf")
                        first_image.save(
                            temp_pdf,
                            "PDF",
                            save_all=True,
                            append_images=remaining_images,
                        )
                        batch_pdfs.append(temp_pdf)
                        first_image.close()
                        for img in remaining_images:
                            img.close()
                        logger.info(f"第 {batch_num} 批图片处理完成")
                    except Exception as e:
                        logger.error(f"处理第 {batch_num} 批图片时出错: {e}")
                        continue
                if batch_pdfs:
                    logger.info(f"开始合并 {len(batch_pdfs)} 个临时PDF...")
                    merger = PdfMerger()
                    for pdf in batch_pdfs:
                        merger.append(pdf)
                    merger.write(output_pdf_path)
                    merger.close()
                    logger.info(f"PDF合并完成：{output_pdf_path}")
                else:
                    logger.warning("没有成功生成任何PDF")
        except Exception as e:
            logger.error(f"转换PDF时出错: {e}")
            raise
