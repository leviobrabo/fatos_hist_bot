from fatoshist.bot import Bot
from fatoshist.config import TOKEN


def main():
    bot = Bot(token=TOKEN)
    bot.start()


if __name__ == '__main__':
    main()
