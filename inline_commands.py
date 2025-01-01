from telethon.tl.custom import Button


# *****************************************************************************
def create_admin_start_buttons():
    btns = []
    btns.append([Button.inline("Список пользователей", data="/user_list")])
    btns.append([Button.inline("Загрузить файл cookies", data="/upload_cookies")])
    # btns.append([Button.inline("Зарегистрировать пользователя", data="/add_user")])
    return btns


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


def create_unreg_buttons(user_id):
    btns = [
        Button.inline(
            "Отправить запрос на регистрацию", data=f"/registration_query {user_id}"
        )
    ]
    return btns


def hello_baner(user_info):
    return (
        f"Привет, {user_info}!\n"
        "Вы зарегистрированы и можете пользоваться этим ботом.\n"
        "Он умеет скачивать аудиокниги доступные для прослушивания по подписке "
        "сайта https://litres.ru. Для этого просто отправтье ссылку на страницу "
        "с аудиокнигой в этот чат. О результате скачивания будет отправлено "
        "сообщение.\n"
        "ВАЖНО!\n"
        "    1. Скачать можно только книги доступные по подписке (не те которые нужно покупать "
        "или брать по абонементу)\n"
        "    2. При копировании ссылки обращайте внимание на то, чтобы страница была именно "
        "аудиокниги, а не текстовой версии. Текстовая и аудио версии имеют разные "
        "идентификаторы и адреса"
    )


def hello_baner_unreg(user_info):
    return (
        f"Привет, {user_info}, вы не зарегистрированны.\n"
        "Попросить администратора добавить вас в список пользователей?"
    )


def you_blocked_baner():
    return "К сожалению, вы заблокированы!"
