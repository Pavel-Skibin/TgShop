from data.config import MESSAGES, BUTTONS


def msg(section: str, number: str):
    return MESSAGES[section][number]


def btn(section: str, number: str):
    return BUTTONS[section][number]

