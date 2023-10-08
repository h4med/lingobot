# Lingo-Bot

This project implements a chatbot using the `python-telegram-bot` library, with data managed in a PostgreSQL database running as a Docker service on a Linux machine. The Bot is using OpenAi Generative AI models as the brain to answer user queries.

## Folder structure

This is the structure:

```plaintext
lingobot/
│
├── app/                    # Main application folder
│   ├── __init__.py
│   ├── bot.py              # Telegram bot handlers and main loop
│   ├── db_manager.py       # Database connection and query handling
│   ├── settings.py         # Configuration settings
│   └── modules/            # Separate functionalities into modules
│       ├── __init__.py
│       ├── user_management.py
│       ├── message_processing.py
│       └── command_handling.py
│
├── tests/                  # Folder for test cases
│   ├── __init__.py
│   ├── test_bot.py
│   ├── test_db_manager.py
│   ├── test_user_management.py
│   ├── test_message_processing.py
│   └── test_command_handling.py
│
├── migrations/             # Database migration scripts
│   ├── __init__.py
│   └── ...                 # Migration scripts
│
├── docs/                   # Documentation folder
│   └── ...                 # Documentation files
│
├── scripts/                # Utility scripts (e.g., database initialization)
│   └── ...                 # Script files
│
├── docker-compose.yml      # Docker Compose file for PostgreSQL service
│
├── requirements.txt        # Project dependencies
│
└── README.md               # Project overview and setup instructions
```

## Getting Started

These instructions will help you set up the project on your local machine for development and testing purposes.


### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Virtual environment (optional, but recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/h4med/lingobot.git
   cd lingobot
    ```

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
    ```
