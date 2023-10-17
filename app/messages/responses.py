# app/messages/responses.py

help_message="""Lingo: Dear <b>{name}</b>, you can talk to me via text message or voice in the language of your choice.
None of your personal information is saved by me and only the content of the last five messages remains in my temporary memory so that the sequence of responses is logical.
I use artificial intelligence GPT-4.0 and GPT-3.5, which you can choose to use in the /settings section.

Version 4.0 is more powerful, but the cost of using it is about 5 times more.
Each account has an initial charge, and if it runs out, you can send up to {free_quota} text or voice messages with GPT-3.5 version.

Instructions guide:
🔹 /settings - settings
🔹 /image - creating an image from the text
🔹 /balance - inventory
🔹 /help – Help

@LingoTheBot\n"""

start_message = """👋 Hello, Dear <b>{name}</b>
I am <b>HooshYar</b>, your smart assistant.
You can communicate with me via text or voice in the selected language in the settings.
No personal information is stored by me, and only the content of your last seven messages stays in my temporary memory to make the sequence of responses logical.
You can also delete these last seven messages at any time by hitting the command below.
🔹 /reset – Clear message history

Your credit balance is:
{credit} Toman

You can check your remaining credit balance by the command below.
🔹 /balance – Credit balance

Start talking to me by sending a text or voice message 🤗
@HooshYarTheBot\n"""
