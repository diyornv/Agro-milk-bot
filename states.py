from aiogram.fsm.state import State, StatesGroup

class AddCow(StatesGroup):
    waiting_for_id = State()
    waiting_for_photos = State()
    waiting_for_description = State()

class DeleteCow(StatesGroup):
    waiting_for_id = State()

