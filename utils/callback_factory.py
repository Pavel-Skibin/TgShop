from aiogram.filters.callback_data import CallbackData


class CatalogNavigationCallbackFactory(CallbackData, prefix="navigate"):
    action: str  # "prev_product" или "next_product"


class AddToCartCallbackFactory(CallbackData, prefix="add_to_cart"):
    product_id: int


class BackToMenuCallbackFactory(CallbackData, prefix="back_to_menu"):
    pass
