# Cow Telegram Bot

A simple Telegram bot to manage and view cow data.

## Features
- **Admin**: Add new cows with ID, Photo, and Description.
- **User**: Retrieve cow details by sending the Cow ID.

## Prerequisites
- Python 3.9+
- A Telegram Bot Token (from @BotFather)

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configuration:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
     (or just rename it)
   - Edit `.env` and fill in your details:
     - `BOT_TOKEN`: Your Telegram Bot API token.
     - `ADMIN_IDS`: Comma-separated list of Telegram User IDs who can add data. (e.g., `12345678, 87654321`)

## Running the Bot

Run the bot with:
```bash
python bot.py
```

## Database Schema
The bot uses SQLite (`cows.db`).

**Table: `cows`**
| Column | Type | Description |
|--------|------|-------------|
| `cow_id` | INTEGER (PK) | Unique numeric ID of the cow |
| `photo_file_id` | TEXT | Telegram file_id of the photo |
| `description` | TEXT | Description text |

## Usage

**Admin Flow:**
1. Send `/add`.
2. Bot asks for ID -> Send `1`.
3. Bot asks for Photo -> Send a photo.
4. Bot asks for Description -> Send `This is a Holstein cow, 3 years old`.
5. Saved!

**User Flow:**
1. Send `1`.
2. Bot replies with the photo and description.
