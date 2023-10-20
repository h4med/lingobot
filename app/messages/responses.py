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

start_message = """👋 Hello, Dear <b>{name}</b>,
Welcome to <b>RealSpeak</b>, your personal AI guide for better English.
Go to /settings to choose your English level, and press /new to begin chatting. You can text or send voice messages.

Need help? Use /help for more information.

Let's start practicing your speaking skills 🤗

@RealSpeakBot"""

start_message_back = """👋 Wellcome back dear <b>{name}</b>,
As you know I am <b>RealSpeak</b>, your personal AI guide for better English.
Go to /settings to choose your English level, and press /new to begin chatting. You can text or send voice messages.

Need help? Use /help for more information.

Let's start practicing your speaking skills 🤗

@RealSpeakBot"""