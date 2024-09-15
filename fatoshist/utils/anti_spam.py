from time import sleep

from telebot.apihelper import ApiTelegramException


def handle_anti_spam(bot):
    for _ in range(4):
        try:
            bot.send_message()
            return
        except ApiTelegramException as ex:
            if 'error_code' in ex.result_json and ex.result_json['error_code'] == '429':
                retry_after = ex.result_json['parameters']['retry_after']
                print(f'Recebido 429, esperando {retry_after} segundos.')
                sleep(retry_after)
            else:
                raise
    bot.send_message()
