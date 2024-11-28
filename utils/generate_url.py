from yoomoney import Quickpay
from data.config import RECEIVER


def generate_url(label: str, amount: int) -> str:
    quickpay = Quickpay(
        receiver=RECEIVER,
        quickpay_form="shop",
        targets="Sponsor this project",
        label=label,
        paymentType="SB",
        sum=amount,
    )
    return quickpay.redirected_url
