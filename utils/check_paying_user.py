from yoomoney import Client
from data.config import TOKEN_WALLET


def check_paying_user(label: str) -> bool:
    token = TOKEN_WALLET
    client = Client(token)
    history = client.operation_history()
    for operation in history.operations:
        if operation.label == label:
            return True
    return False
