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
    DOWNLOAD_COMMAND,
    DOWNLOAD_PATH,
    COOKIES_FILE,
)


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
        msg += f"{db_user.id}\n\
                name: {db_user.name}\n\
                admin:{db_user.admin}\n\
                blocked:{db_user.blocked}\n"

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
    msg = "Отправьте сообщение с командой /upload_cookies и вложенным файлом"
    await event.respond(msg)


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
@client.on(events.NewMessage(pattern="https://www.litres.ru/audiobook/(.+)"))
async def litres_url(event):
    url = event.text
    user_id = event.sender_id

    if not db.user_is_valid(db_session, user_id):
        user_info = await get_user_info(user_id)
        logging.warning(
            f"Попытка запустить скачивание не валидным пользователем\
            {user_info} с id: {user_id}"
        )
        return

    subprocess.Popen(
        f"{DOWNLOAD_COMMAND} --telegram-api {BOT_TOKEN} --telegram-chatid {event.chat_id} \
        --cookies-file {COOKIES_FILE} --output {DOWNLOAD_PATH} --url {url}",
        shell=True,
    )


# *****************************************************************************
@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    sender_id = event.sender_id
    user_info = await get_user_info(event.sender)

    if db.user_is_blocked(db_session, sender_id):
        await event.respond("К сожалению, вы заблокированы!")
        return

    if not db.user_is_valid(db_session, sender_id):
        await event.respond(
            cmd.hello_baner_unreg(user_info),
            buttons=cmd.create_unreg_buttons(sender_id),
        )
    else:
        if db.user_is_admin(db_session, sender_id):
            await event.respond("Команды", buttons=cmd.create_admin_start_buttons())
        else:
            await event.respond(cmd.hello_baner(user_info))


# *****************************************************************************
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    client.start()
    client.run_until_disconnected()
