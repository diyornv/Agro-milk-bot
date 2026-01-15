MESSAGES = {
    "uz_latin": {
        "welcome_select_lang": "Assalomu alaykum! Iltimos, tilni tanlang:",
        "lang_selected": "Til tanlandi: O'zbekcha (Lotin)",
        "welcome_main": "Xush kelibsiz! Ma'lumot olish uchun mol ID raqamini yuboring.",
        "not_authorized": "Sizda bu buyruqdan foydalanish huquqi yo'q.",
        "enter_cow_id": "Iltimos, molning ID raqamini (son) kiriting:",
        "id_must_be_number": "ID raqam bo'lishi kerak. Qaytadan urinib ko'ring:",
        "send_photo": "Tushunarli. Endi molning rasmlarini yuboring (birma-bir yoki albom). Tugatgach /done buyrug'ini yuboring.",
        "send_desc": "Rasmlar qabul qilindi. Endi mol haqida ma'lumot (ta'rif) yozing.",
        "invalid_photo": "Iltimos, rasm yuboring yoki tugatish uchun /done bosing.",
        "cow_saved": "Mol #{cow_id} muvaffaqiyatli saqlandi!",
        "cow_not_found": "Bunday raqamli mol topilmadi.",
        "ask_cow_id": "Qidirish uchun mol raqamini yuboring.",
        "choose_lang_btn": "🇺🇿 O'zbekcha (Lotin)",
        "change_lang": "Tilni o'zgartirish",
        "menu_main_title": "Asosiy menyu",
        "search_cow_btn": "🔍 Mol qidirish",
        "cmd_menu_start": "Boshlash",
        "cmd_menu_lang": "Tilni o'zgartirish",
        "cmd_menu_add": "Yangi mol qo'shish (Admin)",
        "menu_delete_cow": "Molni o'chirish (Admin)",
        "enter_delete_id": "O'chirish uchun mol ID raqamini kiriting:",
        "cow_deleted": "Mol #{cow_id} o'chirildi.",
        "delete_not_found": "O'chirish uchun bunday mol topilmadi.",
        "share_contact_btn": "📞 Telefon raqamni yuborish",
        "ask_phone": "Iltimos, botdan foydalanish uchun telefon raqamingizni yuboring tugmasini bosing:"
    },
    "uz_cyrillic": {
        "welcome_select_lang": "Ассалому алайкум! Илтимос, тилни танланг:",
        "lang_selected": "Тил танланди: Ўзбекча (Кирилл)",
        "welcome_main": "Хуш келибсиз! Маълумот олиш учун мол ID рақамини юборинг.",
        "not_authorized": "Сизда бу буйруқдан фойдаланиш ҳуқуқи йўқ.",
        "enter_cow_id": "Илтимос, молнинг ID рақамини (сон) киритинг:",
        "id_must_be_number": "ID рақам бўлиши керак. Қайтадан уриниб кўринг:",
        "send_photo": "Тушунарли. Энди молнинг расмларини юборинг (бирма-бир ёки альбом). Тугатгач /done буйруғини юборинг.",
        "send_desc": "Расмлар қабул қилинди. Энди мол ҳақида маълумот (таъриф) ёзинг.",
        "invalid_photo": "Илтимос, расм юборинг ёки тугатиш учун /done босинг.",
        "cow_saved": "Мол #{cow_id} муваффақиятли сақланди!",
        "cow_not_found": "Бундай рақамли мол топилмади.",
        "ask_cow_id": "Қидириш учун мол рақамини юборинг.",
        "choose_lang_btn": "🇺🇿 Ўзбекча (Кирилл)",
        "change_lang": "Тилни ўзгартириш",
        "menu_main_title": "Асосий меню",
        "search_cow_btn": "🔍 Мол қидириш",
        "cmd_menu_start": "Бошлаш",
        "cmd_menu_lang": "Тилни ўзгартириш",
        "cmd_menu_add": "Янги мол қўшиш (Админ)",
        "menu_delete_cow": "Молни ўчириш (Админ)",
        "enter_delete_id": "Ўчириш учун мол ID рақамини киритинг:",
        "cow_deleted": "Мол #{cow_id} ўчирилди.",
        "delete_not_found": "Ўчириш учун бундай мол топилмади.",
        "share_contact_btn": "📞 Телефон рақамни юбориш",
        "ask_phone": "Илтимос, ботдан фойдаланиш учун телефон рақамингизни юборинг тугмасини босинг:"
    }
}

def get_mst(lang_code: str, key: str, **kwargs) -> str:
    lang = MESSAGES.get(lang_code, MESSAGES["uz_latin"])
    text = lang.get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text
