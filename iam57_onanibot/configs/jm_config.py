from pydantic import BaseModel


class JMConfig(BaseModel):
    jm_option_file_path: str = "config/jm_option.yml"
    use_default_comic_dir: bool = True
