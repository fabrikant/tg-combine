# Нужно пообщаться с https://t.me/BotFather и получить токен
BOT_TOKEN = "TokenYourBot"
# На my.telegram.org нужно зарегестрировать приложение
API_ID = "api_id from my.telegram.org"
API_HASH = "api hash from my.telegram.org"
# Ваш id в телеграм. Можно спросить у какого-нибудь бота. Например @getmyid_bot
# должно быть числом, а не строкой (без кавычек)
ADMIN_ID = 1234567890
ADMIN_NAME="YourName"

# Полный путь к файлу базы данных. Используется sqlite3
DB_FILENAME = "/home/user/tg-combine.db"
# Полный путь к каталогу загрузки аудиокниг
DOWNLOAD_PATH_AUDIOBOOKS = "/some/books/path/audio"
# Полный путь к каталогу загрузки текстов книг
DOWNLOAD_PATH_TEXTBOOKS = "/some/books/path/texts"

# Утилита загрузки с сайта litres.ru (https://github.com/fabrikant/litres_downloader)
DOWNLOAD_COMMAND_LITRES = "/some_path/litres_downloader/download-book.sh"
#Утилита создания файла cookies по имени пользователя и паролю
CREATE_COOKIES_COMMAND_LITRES = (
    "/some_path/litres_downloader/create-cookies.sh"
)
#Путь к файлу cookies для сайта litres.ru
COOKIES_FILE = "/some_path/cookies.json"

# Утилита загрузки с сайта akniga.org (https://github.com/fabrikant/akniga_downloader)
DOWNLOAD_COMMAND_AKNIGA = "/some_path/akniga_downloader/download-book.sh"

# Утилита загрузки с сайта yakniga.org (https://github.com/fabrikant/yakniga_downloader.git)
DOWNLOAD_COMMAND_YAKNIGA = "/some_path/yakniga_downloader/download-book.sh"

# Утилита загрузки с сайта knigavuhe.org (https://github.com/fabrikant/knigavuhe_downloader.git)
DOWNLOAD_COMMAND_KNIGAVUHE = "/some_path/knigavuhe_downloader/download-book.sh"
