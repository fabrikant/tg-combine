from telethon.tl.custom import Button
from keys import (
    DOWNLOAD_COMMAND_LITRES,
    DOWNLOAD_COMMAND_AKNIGA,
    DOWNLOAD_COMMAND_YAKNIGA,
    DOWNLOAD_COMMAND_KNIGAVUHE,
    DOWNLOAD_COMMAND_KOT_BAUN,
)


# *****************************************************************************
def create_admin_user_edit_buttons(user_id):
    btns = []
    btns.append(
        [
            Button.inline("Разблокировать", data=f"/uedit_blocked_0_{user_id}"),
            Button.inline("Заблокировать", data=f"/uedit_blocked_1_{user_id}"),
        ]
    )
    btns.append(
        [
            Button.inline("Админ", data=f"/uedit_admin_1_{user_id}"),
            Button.inline("Не админ", data=f"/uedit_admin_0_{user_id}"),
        ]
    )
    btns.append(
        [
            Button.inline("Удалить из базы", data=f"/uedit_delete_1_{user_id}"),
        ]
    )
    return btns


# *****************************************************************************
def create_admin_start_buttons():
    btns = []
    btns.append([Button.inline("Список пользователей", data="/user_list")])
    btns.append([Button.inline("Загрузить файл cookies", data="/upload_cookies")])
    btns.append(
        [
            Button.inline(
                "Создать cookies litres.ru user/password", data="/create_cookies"
            )
        ]
    )
    return btns


# *****************************************************************************
def create_admin_reg_design_buttons(user_id):
    btns = []
    btns.append(
        [Button.inline("Зарегистрировать пользователя", data=f"/reg_accept {user_id}")]
    )
    btns.append([Button.inline("Отклонить запрос", data=f"/reg_decline {user_id}")])
    btns.append(
        [Button.inline("Заблокировать пользователя", data=f"/block_user {user_id}")]
    )
    return btns


# *****************************************************************************
def create_unreg_buttons(user_id):
    btns = [
        Button.inline(
            "Отправить запрос на регистрацию", data=f"/registration_query {user_id}"
        )
    ]
    return btns


# *****************************************************************************
def hello_baner(user_info):
    msg = (
        f"Привет, {user_info}!\n"
        "Вы зарегистрированы и можете пользоваться этим ботом.\n"
        "Он умеет скачивать книги. Просто отправьте "
        "ссылку на страницу с книгой в этот чат.\n"
        "Скачивать можно:\n\n"
    )
    ind = 0
    if DOWNLOAD_COMMAND_LITRES != "":
        ind += 1
        msg += (
            f"{ind}. С сайта https://litres.ru \n"
            "**ВАЖНО!**\n__"
            "    - Скачать можно только книги доступные по подписке (не те которые нужно покупать "
            "или брать по абонементу)__\n"
        )
    if DOWNLOAD_COMMAND_AKNIGA != "":
        ind += 1
        msg += (
            f"{ind}. С сайта https://akniga.org аудиокниги и серии аудиокниг\n"
            "**ВАЖНО!**\n__"
            "   -Скачивание с сайта https://akniga.org требует значительного времени__"
            "\n"
        )
    if DOWNLOAD_COMMAND_YAKNIGA != "":
        ind += 1
        msg += f"{ind}. С сайта https://yakniga.org \n"
    if DOWNLOAD_COMMAND_KNIGAVUHE != "":
        ind += 1
        msg += f"{ind}. С сайта https://knigavuhe.org \n"
    if DOWNLOAD_COMMAND_KOT_BAUN != "":
        ind += 1
        msg += f"{ind}. С сайта https://kot-baun.ru \n"

    if ind == 0:
        msg += "Ниоткуда нельзя скачивать!!!"
    else:
        msg += (
            "**Аудиокниги доступны по адресу: https://books.n-drive.cf **\n"
            "**Текстовые книги будут отправлены в телеграм ответным сообщением**"
        )
    return msg


# *****************************************************************************
def hello_baner_unreg(user_info):
    return (
        f"Привет, {user_info}, вы не зарегистрированны.\n"
        "Попросить администратора добавить вас в список пользователей?"
    )


# *****************************************************************************
def you_blocked_baner():
    return "К сожалению, вы заблокированы!"


# *****************************************************************************
def user_about_baner(db_user):
    return (
        f"/edit_user_{db_user.id}\n"
        f"    name: {db_user.name}\n"
        f"    admin:{db_user.admin}\n"
        f"    blocked:{db_user.blocked}\n"
    )
