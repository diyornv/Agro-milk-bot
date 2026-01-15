import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand, InputMediaPhoto

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, add_cow, get_cow, get_user_language, set_user_language, delete_cow, set_user_phone, get_user, add_cow_photo, get_cow_photos
from states import AddCow, DeleteCow
from locales import get_mst, MESSAGES
from transliterate import latin_to_cyrillic

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Bot and Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Keyboards ---
def get_lang_keyboard():
    kb = [
        [KeyboardButton(text=MESSAGES["uz_latin"]["choose_lang_btn"])],
        [KeyboardButton(text=MESSAGES["uz_cyrillic"]["choose_lang_btn"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_contact_keyboard(lang_code: str):
    kb = [
        [KeyboardButton(text=get_mst(lang_code, "share_contact_btn"), request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_main_keyboard(lang_code: str):
    kb = [
        [KeyboardButton(text=get_mst(lang_code, "change_lang"))]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- Helpers ---
async def get_lang(user_id: int) -> str:
    lang = await get_user_language(user_id)
    return lang if lang else "uz_latin" # Default

async def ensure_phone_verified(user_id: int):
    # This is a helper to check if user has phone
    user = await get_user(user_id)
    if user and user['phone_number']:
        return True
    return False

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish / Бошлаш"),
        BotCommand(command="lang", description="Tilni o'zgartirish / Тилни ўзгартириш"),
        BotCommand(command="add", description="Admin: Qo'shish / Қўшиш"),
        BotCommand(command="delete", description="Admin: O'chirish / Ўчириш"),
    ]
    await bot.set_my_commands(commands)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# --- Handler Order: Critical for aiogram 3.x ---
# Place /start and language selection handlers BEFORE any generic text handlers.
# This ensures commands and language selection are always processed, even in FSM states.

# --- User Handlers ---

# /start handler: works in ANY state
@router.message(CommandStart(), StateFilter("*"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)
    # Always allow /start to reset state and show language selection if needed
    await state.clear()
    if not user or not user['language']:
        await message.answer(
            "Assalomu alaykum! Iltimos, tilni tanlang:\n\nАссалому алайкум! Илтимос, тилни танланг:",
            reply_markup=get_lang_keyboard()
        )
    elif not user['phone_number']:
        await message.answer(get_mst(user['language'], "ask_phone"), reply_markup=get_contact_keyboard(user['language']))
    else:
        await message.answer(get_mst(user['language'], "welcome_main"), reply_markup=get_main_keyboard(user['language']))

# /lang command: works in ANY state
@router.message(Command("lang"), StateFilter("*"))
async def cmd_lang(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Iltimos, tilni tanlang / Илтимос, тилни танланг:",
        reply_markup=get_lang_keyboard()
    )

# Language selection buttons: works in ANY state
@router.message(F.text.in_([MESSAGES["uz_latin"]["choose_lang_btn"], MESSAGES["uz_cyrillic"]["choose_lang_btn"]]), StateFilter("*"))
async def language_chosen(message: Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    lang_code = "uz_latin"
    if text == MESSAGES["uz_cyrillic"]["choose_lang_btn"]:
        lang_code = "uz_cyrillic"
    await set_user_language(user_id, lang_code)
    await state.clear()
    user = await get_user(user_id)
    if not user or not user['phone_number']:
        await message.answer(get_mst(lang_code, "lang_selected"), reply_markup=ReplyKeyboardRemove())
        await message.answer(get_mst(lang_code, "ask_phone"), reply_markup=get_contact_keyboard(lang_code))
    else:
        await message.answer(get_mst(lang_code, "lang_selected"), reply_markup=get_main_keyboard(lang_code))
        await message.answer(get_mst(lang_code, "welcome_main"))

# Change language button: works in ANY state
@router.message(F.text.in_([MESSAGES["uz_latin"]["change_lang"], MESSAGES["uz_cyrillic"]["change_lang"]]), StateFilter("*"))
async def change_lang_btn_click(message: Message, state: FSMContext):
    await cmd_lang(message, state)

# Contact handler: works in ANY state
@router.message(F.contact, StateFilter("*"))
async def contact_handler(message: Message, state: FSMContext):
    if not message.contact:
        return
    user_id = message.from_user.id
    phone = message.contact.phone_number
    await set_user_phone(user_id, phone)
    lang = await get_lang(user_id)
    await state.clear()
    await message.answer(get_mst(lang, "welcome_main"), reply_markup=get_main_keyboard(lang))

# --- Admin Handlers ---

# /add command: only for admins, works in ANY state
@router.message(Command("add"), StateFilter("*"))
async def cmd_add(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if not await ensure_phone_verified(message.from_user.id):
        await message.answer(get_mst(lang, "ask_phone"), reply_markup=get_contact_keyboard(lang))
        return
    if not is_admin(message.from_user.id):
        await message.answer(get_mst(lang, "not_authorized"))
        return
    await state.clear()
    await message.answer(get_mst(lang, "enter_cow_id"))
    await state.set_state(AddCow.waiting_for_id)

@router.message(AddCow.waiting_for_id, F.text)
async def process_cow_id(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if not message.text.isdigit():
        await message.answer(get_mst(lang, "id_must_be_number"))
        return
    cow_id = int(message.text)
    await state.update_data(cow_id=cow_id, photos=[])
    await message.answer(get_mst(lang, "send_photo"))
    await state.set_state(AddCow.waiting_for_photos)

@router.message(AddCow.waiting_for_photos, F.photo)
async def process_cow_photo(message: Message, state: FSMContext):
    # Collect photos. Arguments from album are sent as separate messages.
    photo: PhotoSize = message.photo[-1]
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(photo.file_id)
    await state.update_data(photos=photos)
    # Silent collection. User must send /done.

@router.message(AddCow.waiting_for_photos, Command("done"))
async def process_photos_done(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    data = await state.get_data()
    photos = data.get('photos', [])
    if not photos:
        await message.answer(get_mst(lang, "invalid_photo"))
        return
    await message.answer(get_mst(lang, "send_desc"))
    await state.set_state(AddCow.waiting_for_description)

@router.message(AddCow.waiting_for_photos)
async def process_cow_photo_invalid(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(get_mst(lang, "invalid_photo"))

@router.message(AddCow.waiting_for_description, F.text)
async def process_cow_description(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    description = message.text
    data = await state.get_data()
    cow_id = data['cow_id']
    photos = data['photos']
    await add_cow(cow_id, description)
    for p in photos:
        await add_cow_photo(cow_id, p)
    await message.answer(get_mst(lang, "cow_saved", cow_id=cow_id), reply_markup=get_main_keyboard(lang))
    await state.clear()

# /delete command: only for admins, works in ANY state
@router.message(Command("delete"), StateFilter("*"))
async def cmd_delete(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if not await ensure_phone_verified(message.from_user.id):
        await message.answer(get_mst(lang, "ask_phone"), reply_markup=get_contact_keyboard(lang))
        return
    if not is_admin(message.from_user.id):
        await message.answer(get_mst(lang, "not_authorized"))
        return
    await state.clear()
    await message.answer(get_mst(lang, "enter_delete_id"))
    await state.set_state(DeleteCow.waiting_for_id)

@router.message(DeleteCow.waiting_for_id, F.text)
async def process_delete_id(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if not message.text.isdigit():
        await message.answer(get_mst(lang, "id_must_be_number"))
        return
    cow_id = int(message.text)
    success = await delete_cow(cow_id)
    if success:
        await message.answer(get_mst(lang, "cow_deleted", cow_id=cow_id), reply_markup=get_main_keyboard(lang))
    else:
        await message.answer(get_mst(lang, "delete_not_found"), reply_markup=get_main_keyboard(lang))
    await state.clear()

# --- Cow Lookup Handler ---
# This handler matches ONLY digit messages, and is placed AFTER all command and language handlers.
# It will NOT capture commands or non-numeric messages.
@router.message(F.text.regexp(r"^\\d+$"), StateFilter("*"))
async def get_cow_info(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if not await ensure_phone_verified(message.from_user.id):
        await message.answer(get_mst(lang, "ask_phone"), reply_markup=get_contact_keyboard(lang))
        return
    cow_id = int(message.text)
    cow_data = await get_cow(cow_id)
    if cow_data:
        # Try to get photos for this cow
        photos = await get_cow_photos(cow_id)
        # If cow_data is tuple (description,) or (photo_file_id, description)
        if isinstance(cow_data, tuple) and len(cow_data) == 2:
            photo_file_id, description = cow_data
        else:
            description = cow_data[0]
            photo_file_id = None
        # Automatic Transliteration
        if lang == "uz_cyrillic":
            description = latin_to_cyrillic(description)
        if photos:
            if len(photos) == 1:
                await message.answer_photo(photos[0], caption=description)
            else:
                media = []
                for idx, p in enumerate(photos):
                    caption = description if idx == 0 else None
                    media.append(InputMediaPhoto(media=p, caption=caption))
                await message.answer_media_group(media)
        elif photo_file_id:
            await message.answer_photo(photo_file_id, caption=description)
        else:
            await message.answer(description)
    else:
        await message.answer(get_mst(lang, "cow_not_found"))

# --- Main ---

async def main():
    await init_db()
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
