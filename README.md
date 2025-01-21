# tg-combine
Телеграм бот предназначен для управления загрузчиками аудиокниг:

1. [litres_audiobooks_downloader](https://github.com/fabrikant/litres_audiobooks_downloader.git)
1. [akniga_downloader](https://github.com/fabrikant/akniga_downloader.git)
1. [knigavuhe_downloader](https://github.com/fabrikant/knigavuhe_downloader.git)
1. [yakniga_downloader](https://github.com/fabrikant/yakniga_downloader.git)

# Требования
1. [python3](https://www.python.org/) и venv. Тестировалось на версии 3.12
1. **API Token** для телеграм бота. Зарегестрировать нового бота и получить токен можно обратившись к [BotFather](https://t.me/BotFather)
1. **Telegram ID** пользователя, который будет главным администратором бота. Узнать свой ID можно, например, обратившись к боту [getmyid_bot](https://t.me/getmyid_bot)
1. **API_ID** и **API_HASH** нужно получить, зарегистрировавшись на сайте [my.telegram.org](https://my.telegram.org)

> **ВАЖНО!!!**
>
> Должно работать и на Windows, но тестировалось только на Linux. 

# Установка

Скачиваем любым способом исходный код. Например:  
```bash
git clone https://github.com/fabrikant/yakniga_downloader.git
```
Переходим в каталог с исходным кодом и выполняем команду  
**Linux:**
```bash
./install.sh
```
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
```

# Настройка
Копируем файл **keys_examle.py** в тот же каталог с именем **keys.py** и заполняем его своими значениями.

Если какие-то из качалок не планируется использовать, то для соответсвующих переменных необходимо в качестве пути указать пустую строку. Например:

```python3
DOWNLOAD_COMMAND_AKNIGA = ""
```

# Запуск
**Linux**
```bash
./tg-combine.sh
```
 
**Windows**

Перед запуском скрипта необходимо активировать виртуальное окружение командой:
```
venv\Scripts\activate
```
Далее скрипт вызывается командой:
```
python3 tg_combine.py
```