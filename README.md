# 五七のオナニーボット

## :book: 简介

五七的自用机器人。之所以叫做オナニーボット，是因为这个机器人的开发起源于下载禁漫并转换成 PDF。

## :package: 部署

### :whale: Docker Compose（推荐）

与 NapCat 集成，使用以下 `docker-compose.yml` 配置：

```yaml
version: "3"

x-config-host: &config-host ${HOST:-0.0.0.0}
x-config-port: &config-port ${PORT:-8888}

networks:
  onanibot-network:
    external: true

volumes:
  bot_data:
  bot_config:
  qq_data:
  napcat_config:

services:
  onanibot:
    image: iam57ao/onanibot:latest
    container_name: onanibot
    ports:
      - *config-port
    environment:
      ENVIRONMENT: prod
      HOST: *config-host
      PORT: *config-port
    restart: always
    networks:
      - onanibot-network
    volumes:
      - bot_data:/app/data
      - bot_config:/app/config
      
  napcat:
    ports:
      - 3000:3000
      - 3001:3001
      - 6099:6099
    container_name: napcat
    restart: always
    image: mlikiowa/napcat-docker:latest
    networks:
      - onanibot-network
    volumes:
      - qq_data:/app/.config/QQ
      - napcat_config:/app/napcat/config
      - bot_data:/app/data
```

## :gear: 配置

### JM_OPTION_FILE_PATH

禁漫配置文件的地址。

- **类型**: `str`
- **默认值**: `"config/jm_option.yml"`

### USE_DEFAULT_COMIC_DIR

是否使用默认的下载地址。如果该配置的值为 `True`，则 `JM_OPTION_FILE_PATH` 设置的配置文件中 `dir_rule->base_dir` 的值会被程序运行根目录下的 `/data/comics` 文件夹替换，即默认漫画下载地址。

- **类型**: `bool`
- **默认值**: `True`

