from pydantic import BaseModel


class JMConfig(BaseModel):
    config_path: str = "config/jm_config.yml"
    use_default_comic_dir: bool = True
