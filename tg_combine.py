import logging
import db
import tg_dialogs as dialogs
from telethon import TelegramClient, events
import re
import asyncio
from tg_settings import settings

db_session = db.create_database(
    f"sqlite:///{settings.db_filename}", settings.admin_id, settings.admin_name
)
client = TelegramClient(
    "bot", settings.telegram_api_id, settings.telegram_api_hash
).start(bot_token=settings.telegram_bot_token)


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
async def upload_file(event, filename):
    document = event.message.document
    if document == None:
        await event.respond(f"Файл не приложен к сообщению")
        return
    file = await event.message.download_media(file=filename)
    await event.respond(f"Записан файл {filename}")


# *****************************************************************************
async def create_cookies_file(event, exec_filename, cookies_filename):
    usr_pass_array = event.text.split(" ")
    if len(usr_pass_array) != 3:
        await event.respond(f"Неверный формат команды")
        return
    cmd = (
        f"{exec_filename} -b {settings.browser} --telegram-api {settings.telegram_bot_token} "
        f" --telegram-chatid {event.chat_id} --cookies-file {cookies_filename} "
        f" -u {usr_pass_array[-2]} -p {usr_pass_array[-1]} "
    )
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.communicate()


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
        msg += dialogs.user_about_banner(db_user)
    await event.respond(msg)


# *****************************************************************************
# Нажата inline кнопка /downloads_list
# Убеждаемся, что пользователь - админ и ответным сообщением выводим список
@client.on(events.CallbackQuery(data=b"/downloads_list"))
async def downloads_list(event):
    str_command = event.data.decode("utf-8")
    user_id = event.sender_id
    if not await check_user_right(str_command, user_id, need_admin_rights=True):
        return
    db_query = (
        db_session.query(db.Books, db.Users)
        .join(db.Users, db.Users.id == db.Books.user, isouter=True)
        .order_by(db.Books.date.desc())
        .limit(20)
    )

    msg = ""
    for db_record in db_query:
        msg += dialogs.downloads_banner(db_record)
    await event.respond(msg)


# *****************************************************************************
# Нажата одна из кнопок редактирования пользователя /uedit.
# Убеждаемся, что команду дал админ и редактируем мы не главного админа,
# тот, который settings.admin_id.
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
    if cmd_user_id == settings.admin_id:
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
        msg = f"Новые значения:\n{dialogs.user_about_banner(db_user)}"
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

    await client.send_message(unreg_user_id, dialogs.you_blocked_banner())
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
        await event.respond(dialogs.you_blocked_banner())
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
    btns = dialogs.create_admin_reg_design_buttons(sender_id)
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
        f"Редактирование пользователя\n{dialogs.user_about_banner(db_user)}",
        buttons=dialogs.create_admin_user_edit_buttons(edit_user_id),
    )


# *****************************************************************************
# Обработка загрузки команды администратора
# Обязательно нужно убедиться, что файл присылает админ
@client.on(events.NewMessage(pattern="/command(.+)"))
async def admin_command(event):
    user_id = event.sender_id
    text = event.text
    if not await check_user_right(text, user_id, True):
        return

    for downloader in settings.downloaders:
        if not hasattr(downloader, "admin_commands"):
            continue
        for admin_command in downloader.admin_commands:
            if text.startswith(admin_command.id):
                if admin_command.command == "load_cookies":
                    await upload_file(event, downloader.cookies_filename)
                    return
                elif admin_command.command == "create_cookies":
                    await create_cookies_file(
                        event, admin_command.exec_file, downloader.cookies_filename
                    )
                    return


# *****************************************************************************
# Обработка url
@client.on(events.NewMessage(pattern="https://(.+)"))
async def url_message(event):
    url = event.text
    url_compare = url.replace("https://www.", "https://")
    user_id = event.sender_id
    user_info = await get_user_info(user_id)

    if not db.user_is_valid(db_session, user_id):
        logging.warning(
            f"Попытка запустить скачивание не валидным пользователем\
            {user_info} с id: {user_id}"
        )
        return

    cmd = ""
    output_path = settings.audiobooks_path
    cover_prefix = ""
    metadata_prefix = ""
    for downloader in settings.downloaders:
        if not url_compare.startswith(downloader.url):
            continue

        cmd = downloader.command
        if hasattr(downloader, "cookies_filename"):
            # Если для загрузки требуется файл cookies,
            # передаем его
            cmd += f" --cookies-file {downloader.cookies_filename}"

        if hasattr(downloader, "text_book_url_pattern"):
            if downloader.text_book_url_pattern in url:
                # Будем скачивать текстовую, а не аудиокнигу
                # меняем каталог загрузки, отключаем загрузку обложки
                # и метаданных, отправляем файл книги в телеграм
                output_path = settings.textbooks_path
                cover_prefix = "no-"
                metadata_prefix = "no-"
                cmd += " --send-fb2-via-telegram "

    common_args = (
        f" -vv --{cover_prefix}cover --{metadata_prefix}metadata --telegram-api {settings.telegram_bot_token} "
        f" --telegram-chatid {str(event.chat_id)} --output {output_path} --url {url} "
    )

    if len(cmd) > 0:
        # Пишем в лог и в базу данных у запуске загрузки
        logging.info(f"Пользователь: {user_info} запустил загрузку: {url}")
        db.add_book_record(db_session, user=user_id, url=url)
        # Запуск процесса загрузки. Процесс сам будет отправлять сообщения пользователю
        # в телеграм о процессе и результате загрузки
        proc = await asyncio.create_subprocess_shell(cmd + common_args)
        await proc.communicate()

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
        await event.respond(dialogs.hello_banner(user_info))
        if db.user_is_admin(db_session, sender_id):
            msg, buttons = dialogs.create_admin_start_message()
            await event.respond(msg, buttons=buttons)
    else:
        await event.respond(
            dialogs.hello_banner_unreg(user_info),
            buttons=dialogs.create_unreg_buttons(sender_id),
        )


# *****************************************************************************
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )

    client.start()
    client.run_until_disconnected()
    db_session.close()
