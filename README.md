# tg-combine
Телеграм бот предназначен для управления загрузчиками книг/аудиокниг:

1. [litres_downloader](https://github.com/fabrikant/litres_downloader.git)
1. [akniga_downloader](https://github.com/fabrikant/akniga_downloader.git)
1. [knigavuhe_downloader](https://github.com/fabrikant/knigavuhe_downloader.git)
1. [yakniga_downloader](https://github.com/fabrikant/yakniga_downloader.git)
1. [kot_baun_downloader](https://github.com/fabrikant/kot_baun_downloader.git)
1. [audioknigaone_downloader](https://github.com/fabrikant/audioknigaone_downloader.git)

# Требования
1. [python3](https://www.python.org/) и venv. Тестировалось на версии 3.12
1. **API Token** для телеграм бота. Зарегестрировать нового бота и получить токен можно обратившись к [BotFather](https://t.me/BotFather)
1. **Telegram ID** пользователя, который будет главным администратором бота. Узнать свой ID можно, например, обратившись к боту [getmyid_bot](https://t.me/getmyid_bot)
1. **settings.telegram_api_id** и **settings.telegram_api_hash** нужно получить, зарегистрировавшись на сайте [my.telegram.org](https://my.telegram.org)

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
Копируем файл **settings_example.yml** в тот же каталог с именем **settings.yml** и заполняем его своими значениями.

Если какие-то из качалок не планируется использовать, то из файла можно удалить соответствующие блоки

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

# Примечание для Windows пользователей
У меня нет возможности (да и желания) тестировать работу под Windows. Могу лишь дать общие рекомендации.

Если вы по какой-то причине хотите запускать этого бота под Windows и не используете при этом [WSL](https://ru.wikipedia.org/wiki/Windows_Subsystem_for_Linux), у вас есть два пути:

1. **Правильный путь.** Создать для каждой качалки виртуальное окружение, установить зависимости в виртуальное окружение.
И самостоятельно написать для каждой качалки bat/cmd файл, который активирует виртуальное окружение и запустит качалку с переданными параметрами.
Соответствено в файле settings.yml вы прописываете что-то типа: 

    ```command: "C:\Путь\к\cmd\download.cmd"```
1. **Неправльный путь.** Установить все зависимости в системные библиотеки. Для этого выполнить в каталоге каждой качалки:
    ```
    pip install -r requirements.rxt
    ```
    А в качесестве команды указать что-то вроде:

    ```command: 'python3 "C:\Путь\к\качалке\download_book.py"'```

# Запуск бота как службы (сервиса) systemd на Linux
1. Поместить папку с программой в место постоянного пребывания
1. Перейти в папку и выполнить команду:
    ```bash
    ./install.sh
    ```
    В результате в папке с программой будет сформирован файл **tg-combine.service**
1. Выполнить следующие команды:
    ```bash
    sudo mv tg-combine.service /etc/systemd/system/tg-combine.service
    sudo systemctl enable tg-combine.service
    sudo service tg-combine start 
    ```
1. Для удаления службы выполнить команды:
    ```bash
    sudo service tg-combine stop
    sudo systemctl disable tg-combine.service
    sudo rm /etc/systemd/system/tg-combine.service
    ```
