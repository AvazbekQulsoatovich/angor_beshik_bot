from aiogram.fsm.state import StatesGroup, State

class AdminCategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()

class AdminCategoryEditStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_emoji = State()

class AdminProductStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_photos = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_cost_price = State()
    waiting_for_price = State()
    waiting_for_stock = State()
    waiting_for_confirmation = State()

class AdminProductEditStates(StatesGroup):
    waiting_for_photos = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_cost_price = State()
    waiting_for_price = State()
    waiting_for_stock = State()

class AdminReplyStates(StatesGroup):
    waiting_for_reply = State()

class AdminManageStates(StatesGroup):
    waiting_for_new_admin_id = State()
