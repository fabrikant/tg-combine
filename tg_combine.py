import logging
import db
import inline_commands as cmd
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import re

import subprocess
from keys import (
    BOT_TOKEN,
    API_ID,
    API_HASH,
    DB_FILENAME,
    DOWNLOAD_COMMAND_LITRES,
    DOWNLOAD_COMMAND_AKNIGA,
    DOWNLOAD_COMMAND_YAKNIGA,
    DOWNLOAD_COMMAND_KNIGAVUHE,
    CREATE_COOKIES_COMMAND_LITRES,
    DOWNLOAD_PATH,
    COOKIES_FILE,
    ADMIN_ID,
)

subprocess_list = []

db_session = db.create_database(f"sqlite:///{DB_FILENAME}")
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


# *****************************************************************************
async def get_user_info(user_or_id):
    if type(user_or_id) == type(1):
        user = await client.get_entity(user_or_id)
    else:
        user = user_or_id

    info = user.first_name
    if user.last_name != None:
        info += f" {user.last_name}"
    if user.phone != None:
        info += f" ({user.phone})"
    return info


# *****************************************************************************
async def check_user_right(str_command, user_id, need_admin_rights=False):
    result = True
    logging.info(f"Получена команда {str_command} от id {user_id}")
    if need_admin_rights:
        if not db.user_is_admin(db_session, user_id):
            user_info = await get_user_info(user_id)
            logging.warning(
                f"Попытка выполнить команду {str_command} без полномочий администратора\
                    пользователем {user_info} c id: {user_id}"
            )
            result = False
    else:
        if not db.user_is_valid(db_session, user_id):
            user_info = await get_user_info(user_id)
            logging.warning(
                f"Попытка выполнить команду {str_command} не валидным\
                    пользователем {user_info} c id: {user_id}"
            )
            result = False
    return result


# *****************************************************************************
# Нажата inline кнопка /user_list
# Убеждаемся, что пользователь - админ и ответным сообщением выводим список
@client.on(events.CallbackQuery(data=b"/user_list"))
async def user_list(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return
    db_query = db_session.query(db.Users).order_by(db.Users.name).all()
    msg = ""
    for db_user in db_query:
        msg += cmd.user_about_baner(db_user)
    await event.respond(msg)


# *****************************************************************************
# Нажата inline кнопка /upload_cookies
# Убеждаемся, что пользователь - админ и ответным сообщением выводим
# Подсказку о загрузке файла cookies
@client.on(events.CallbackQuery(data=b"/upload_cookies"))
async def upload_cookies(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return
    msg = "Отправьте сообщение с командой\n/upload_cookies\nи вложенным файлом"
    await event.respond(msg)


# *****************************************************************************
# Нажата inline кнопка /create_cookies
# Убеждаемся, что пользователь - админ и ответным сообщением выводим
# Подсказку о создании файла cookies
@client.on(events.CallbackQuery(data=b"/create_cookies"))
async def create_cookies(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return
    msg = (
        "Отправьте сообщение с командой:\n/create_cookies user password\n"
        "через пробел для создания файла cookies на сервере"
    )
    await event.respond(msg)


# *****************************************************************************
# Нажата одна из кнопок редактирования пользователя /uedit.
# Убеждаемся, что команду дал админ и редактируем мы не главного админа,
# тот, который ADMIN_ID.
# Разбираем и выполняем команду
@client.on(events.CallbackQuery(data=re.compile(b"/uedit_")))
async def reg_decline(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return
    cmd_array = str_command.replace("/uedit_", "").split("_")
    cmd_or_field = cmd_array[0]
    cmd_value = int(cmd_array[1])
    cmd_user_id = int(cmd_array[2])
    # Проверим, что мы не редактируем главного админа
    if cmd_user_id == ADMIN_ID:
        await event.respond("Запрещено редактировать главного админа")
        return

    # Проверим, что пользователь существует в базе
    db_user = db_session.query(db.Users).filter_by(id=cmd_user_id).first()
    if db_user == None:
        msg = f"Попытка редактирования отсутствующего в базе пользователя\nid:{cmd_user_id}"
        await event.respond(msg)
        logging.warning(msg)
        return

    # Редактирование пользователя
    if cmd_or_field == "blocked" or cmd_or_field == "admin":
        setattr(db_user, cmd_or_field, cmd_value)
        db_user.postprocessing()
        db_session.add(db_user)
        db_session.commit()

        # Читаем пользователя из базы и выводим новые значения
        db_user = db_session.query(db.Users).filter_by(id=cmd_user_id).first()
        msg = f"Новые значения:\n{cmd.user_about_baner(db_user)}"
        await event.respond(msg)

    # Удаление пользователя из базы
    if cmd_or_field == "delete":
        db_session.query(db.Users).filter_by(id=cmd_user_id).delete()
        db_session.commit()
        await event.respond(f"Пользователь id: {cmd_user_id}\nудален из базы")


# *****************************************************************************
# Нажата inline кнопка /reg_accept - запрос на регистрацию одобрен
# Убеждаемся, что пользователь, нажавший кнопку - администратор
# Регистрируем пользователя
# и пишем сообщение о регистрации соискателю,
# а админу о регистрации пользователя
@client.on(events.CallbackQuery(data=re.compile(b"/reg_accept")))
async def reg_accept(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return

    unreg_user_id = int(str_command.replace("/reg_accept", ""))
    unreg_user_info = await get_user_info(unreg_user_id)

    db.get_or_create(
        db_session,
        db.Users,
        True,
        id=unreg_user_id,
        name=unreg_user_info,
        admin=False,
        blocked=False,
    )
    msg = (
        f"Поздравляю! Заявка на регистрацию одобрена!\nНачните работу с команды /start"
    )
    await client.send_message(unreg_user_id, msg)
    await event.respond(
        f"Новый пользователь {unreg_user_info} зарегестрирован в системе"
    )


# *****************************************************************************
# Нажата inline кнопка /reg_decline - запрос на регистрацию отклонен
# Убеждаемся, что пользователь, нажавший кнопку - администратор
# и пишем сообщение об отклонении соискателю регистрации
@client.on(events.CallbackQuery(data=re.compile(b"/reg_decline")))
async def reg_decline(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return
    unreg_user_id = int(str_command.replace("/reg_decline", ""))
    unreg_user_info = await get_user_info(unreg_user_id)
    await client.send_message(
        unreg_user_id, "К сожалению, заявка на регистрацию отклонена!"
    )
    await event.respond(
        f"Отклонена заявка о регистрации пользователя {unreg_user_info}"
    )


# *****************************************************************************
# Нажата inline кнопка /block_user - запрос на регистрацию одобрен
# Убеждаемся, что пользователь, нажавший кнопку - администратор
# Регистрируем пользователя
# и пишем сообщение о регистрации соискателю,
# а админу о регистрации пользователя
@client.on(events.CallbackQuery(data=re.compile(b"/block_user")))
async def block_user(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return

    unreg_user_id = int(str_command.replace("/block_user", ""))
    unreg_user_info = await get_user_info(unreg_user_id)

    db.get_or_create(
        db_session,
        db.Users,
        True,
        id=unreg_user_id,
        name=unreg_user_info,
        admin=False,
        blocked=True,
    )

    await client.send_message(unreg_user_id, cmd.you_blocked_baner())
    await event.respond(f"Пользователь {unreg_user_info} заблокирован в системе")


# *****************************************************************************
# Нажата inline кнопка /registration_query - запрос на регистрацию
# Убеждаемся, что пользователь еще не зарегистрирован и отправляем
# админам запроса на регистрацию, а пользователю сообщение о том,
# что запрос отправлен админам
@client.on(events.CallbackQuery(data=re.compile(b"/registration_query")))
async def registration_query(event):
    sender_id = event.sender_id
    sender = event.sender
    sender_info = await get_user_info(sender)

    if db.user_is_blocked(db_session, sender_id):
        await event.respond(cmd.you_blocked_baner())
        return
    if db.user_is_valid(db_session, sender_id):
        await event.respond("Вы уже зарегистрированы")
        return

    # Отправляем запрос администраторам
    db_query = (
        db_session.query(db.Users)
        .filter(db.Users.admin == True)
        .filter(db.Users.blocked == False)
        .all()
    )
    btns = cmd.create_admin_reg_design_buttons(sender_id)
    msg = f"Запрос на регистрацию от пользователя: {sender_info}\n id: {sender_id}"
    for db_admin in db_query:
        await client.send_message(db_admin.id, msg, buttons=btns)
    # Отправляем ответ пользователю
    await event.respond(
        "Запрос на регистрацию отправлен. Ожидайте решения администратора!"
    )


# *****************************************************************************
# Обработка команды /edit_user
# Обязательно нужно убедиться, что команду присылает админ
# После этого отправляем inline кнопки для редактирования usera
@client.on(events.NewMessage(pattern="/edit_user_(.+)"))
async def edit_user(event):
    user_id = event.sender_id
    if not await check_user_right("/upload_cookies", user_id, True):
        return
    edit_user_id = int(event.text.replace("/edit_user_", ""))
    db_user = db_session.query(db.Users).filter_by(id=edit_user_id).first()
    await client.send_message(
        user_id,
        f"Редактирование пользователя\n{cmd.user_about_baner(db_user)}",
        buttons=cmd.create_admin_user_edit_buttons(edit_user_id),
    )


# *****************************************************************************
# Обработка загрузки файла cookies
# Обязательно нужно убедиться, что файл присылает админ
@client.on(events.NewMessage(pattern="/upload_cookies"))
async def upload_cookies(event):
    user_id = event.sender_id
    if not await check_user_right("/upload_cookies", user_id, True):
        return
    document = event.message.document
    if document == None:
        await event.respond(f"Файл не приложен к сообщению")
        return
    file = await event.message.download_media(file=COOKIES_FILE)
    await event.respond(f"Записан файл {COOKIES_FILE}")


# *****************************************************************************
# Обработка команды создания файла cookies по имени и паролю
# Обязательно нужно убедиться, что файл присылает админ
@client.on(events.NewMessage(pattern="/create_cookies (.+) (.+)"))
async def message_create_cookies(event):
    user_id = event.sender_id
    if not await check_user_right("/create_cookies", user_id, True):
        return
    usr_pass_array = event.text.replace("/create_cookies ", "").split(" ")
    if len(usr_pass_array) != 2:
        await event.respond(f"Неверный формат команды")
        return
    # Запуск процесса создания файла cookies.
    # Процесс сам будет отправлять сообщения пользователю
    # в телеграм о процессе и результате загрузки
    subprocess_list.append(
        subprocess.Popen(
            (
                f"{CREATE_COOKIES_COMMAND_LITRES} -b firefox --telegram-api {BOT_TOKEN} "
                f"--telegram-chatid {event.chat_id} --cookies-file {COOKIES_FILE} "
                f" -u {usr_pass_array[0]} -p {usr_pass_array[1]} "
            ),
            shell=True,
        )
    )


# *****************************************************************************
# Обработка url
@client.on(events.NewMessage(pattern="https://(.+)"))
async def url_message(event):
    url = event.text
    user_id = event.sender_id
    user_info = await get_user_info(user_id)

    if not db.user_is_valid(db_session, user_id):
        logging.warning(
            f"Попытка запустить скачивание не валидным пользователем\
            {user_info} с id: {user_id}"
        )
        return

    common_args = [
        "-vv",
        "--telegram-api",
        BOT_TOKEN,
        "--telegram-chatid",
        str(event.chat_id),
        "--output",
        DOWNLOAD_PATH,
        "--url",
        url,
    ]
    cmd_list = []

    if "litres.ru" in url:
        if DOWNLOAD_COMMAND_LITRES != "":
            cmd_list = [DOWNLOAD_COMMAND_LITRES, "--cookies-file", COOKIES_FILE]
    elif "https://yakniga.org" in url and DOWNLOAD_COMMAND_YAKNIGA != "":
        cmd_list = [DOWNLOAD_COMMAND_YAKNIGA]
    elif "https://akniga.org" in url and DOWNLOAD_COMMAND_AKNIGA != "":
        cmd_list = [DOWNLOAD_COMMAND_AKNIGA]
    elif "https://knigavuhe.org" in url and DOWNLOAD_COMMAND_KNIGAVUHE != "":
        cmd_list = [DOWNLOAD_COMMAND_KNIGAVUHE]

    if len(cmd_list) > 0:
        # Пишем в лог и в базу данных у запуске загрузки
        logging.info(f"Пользователь: {user_info} запустил загрузку: {url}")
        db.add_book_record(db_session, user=user_id, url=url)
        # Запуск процесса загрузки. Процесс сам будет отправлять сообщения пользователю
        # в телеграм о процессе и результате загрузки
        subprocess_list.append(subprocess.Popen(cmd_list + common_args))
    else:
        await event.respond(f"Адрес: {url} не может быть обработан")


# *****************************************************************************
# Обработка команды /start
@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    sender_id = event.sender_id
    user_info = await get_user_info(event.sender)

    if db.user_is_blocked(db_session, sender_id):
        await event.respond("К сожалению, вы заблокированы!")
        return

    if db.user_is_valid(db_session, sender_id):
        await event.respond(cmd.hello_baner(user_info))
        if db.user_is_admin(db_session, sender_id):
            await event.respond("Команды", buttons=cmd.create_admin_start_buttons())
    else:
        await event.respond(
            cmd.hello_baner_unreg(user_info),
            buttons=cmd.create_unreg_buttons(sender_id),
        )


# *****************************************************************************
# Обработка всех сообщений
@client.on(events.NewMessage())
async def all_messages(event):
    # Просто проверяем нет ли завершившихся процессов
    check_subprocesses()


# *****************************************************************************
# Избавляемся от зомби процессов
def check_subprocesses():
    indexes = []
    for index, sub_prc in enumerate(subprocess_list):
        sub_prc.communicate()
        if not sub_prc.poll() is None:
            indexes.append(index)

    for index in sorted(indexes, reverse=True):
        del subprocess_list[index]


# *****************************************************************************
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    client.start()
    client.run_until_disconnected()
    db_session.close()
    check_subprocesses()
