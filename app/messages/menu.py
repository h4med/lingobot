from telegram import (
    Update,
    InlineKeyboardButton,
)

def settings_main_menu(level):
    keyboard = [
        [InlineKeyboardButton(f"Level: {level}", callback_data='level')] #TODO: add enable/disable show text on voices
    ]
    return keyboard

def settings_level_list_menu():

    keyboard = [
            [InlineKeyboardButton("Beginner", callback_data='level_1')],
            [InlineKeyboardButton("Elementary", callback_data='level_2')],
            [InlineKeyboardButton("Intermediate", callback_data='level_3')],
            [InlineKeyboardButton("Upper-Intermediate", callback_data='level_4')],
            [InlineKeyboardButton("Advanced", callback_data='level_5')],
            [InlineKeyboardButton("Cancel", callback_data='cancel')]
        ]

    return keyboard