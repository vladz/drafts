import logging
import os

from telegram_bot import app, config

DEBUG = True if os.getenv('DEBUG') else False

if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if DEBUG else logging.INFO)
    logging.info('Telegram bot init.')
    logging.info('Config loading.')
    cfg = config.init(DEBUG)

    app.main(cfg)
