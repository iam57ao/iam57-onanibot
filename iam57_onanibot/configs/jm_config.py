from pydantic import BaseModel


class JMConfig(BaseModel):
    use_default_comic_dir: bool = True
    jm_enable_groups: list[str] = []
    jm_option_file_path: str = "config/jm_option.yml"
