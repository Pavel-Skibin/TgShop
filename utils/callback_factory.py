from aiogram.filters.callback_data import CallbackData


class CatalogNavigationCallbackFactory(CallbackData, prefix="navigate"):
    action: str  # "prev_product" или "next_product"



class PaidCallbackFactory(CallbackData, prefix="paid"):
    payment_id: int
    sum: int
