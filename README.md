<img src="https://i.imgur.com/OQKrs8P.jpeg" align="right" width="200" height="200"/>

# Fatos Históricos

[![](https://img.shields.io/badge/Site-História-blue)](https://www.historiadodia.com/)
[![](https://img.shields.io/badge/Telegram-@fatoshistbot-blue)](https://t.me/fatoshistbot)
[![](https://img.shields.io/badge/Suporte-@kylorensbot-1b2069)](https://t.me/kylorensbot)
[![](https://img.shields.io/badge/Telegram-@HojeNaHistoria-red)](https://t.me/historia_br)

[Fatos Históricos](https://t.me/historia_br) é um bot para telegram que tem como objetivo propagar o conhecimento de história e bem como levar o conhecimento de forma "leve" e "tranquila" para todo o público.

## Funcionalidades

-   Envia eventos históricos do dia
    -   Chat privado (8h)
    -   Canal (5h3min)
    -   Grupos (8h)
-   Envia frases históricas
-   Envia Feriados do dia
-   Envia Nascido do dia
-   Envia mortos do dia
-   Envia imagens de eventos históricos
    -   Chat privado
    -   Canal
    -   Grupos
-   Envia curiosidade históricas
-   Envia data comemorativas
-   Envia quiz com perguntas históricas 🆕
    -   Chat
    -   Canal
-   Envia Presidentes de cada país 🆕

[![](https://i.imgur.com/MzZuN3G.jpeg)](#)

### Pré-requisitos

Você vai precisar ter instalado em sua máquina as seguintes ferramentas:

-   [Git](https://git-scm.com)
-   [Python](https://www.python.org/)
-   [MongoDB](https://cloud.mongodb.com/)
-   [WIKIMEDIA](https://api.wikimedia.org/wiki/Feed_API/Reference/On_this_day)

### 🤖 Deploy no Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### 🤖 Rodando o bot localmente

```bash
# Clone este repositório
$ git clone https://github.com/leviobrabo/fatoshisbot.git

# Acesse a pasta do projeto no terminal/cmd
$ cd fatoshisbot

# Instale as dependências

# Usando o pip:
$ pip3 install -r requirements.txt

# altere o nome do conf
$ cp sample.bot.conf bot.conf

# Variáveis ambientes

# Crie um arquivo com bot.conf com qualquer editor de texto e coloque:
[FATOSHIST]
TOKEN=
HIST_LOG=
HIST_CHANNEL=
BOT_NAME=
BOT_USERNAME=
OWNER_ID=
HIST_CHANNEL_POST =

[DB]
MONGO_CON=

[LOG]
LOG_PATH = /path/to/log/file

# Execute a aplicação
$ python3 fatoshistoricos.py

```

## Pronto, o bot já estará rodando
