import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def __init__(self, token, url):
        super().__init__(token, url)

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg['text'] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg['text'], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def __init__(self, token, telegram_chat_url):
        super().__init__(token, telegram_chat_url)
        self.data = None

    def blur_photo(self, chat_id, img_path):
        img = Img(img_path)
        img.blur()
        new_path = img.save_img()
        self.send_photo(chat_id, new_path)

    def contour_photo(self, chat_id, img_path):
        img = Img(img_path)
        img.contour()
        new_path = img.save_img()
        self.send_photo(chat_id, new_path)

    def rotate_photo(self, chat_id, img_path):
        img = Img(img_path)
        img.rotate()
        new_path = img.save_img()
        self.send_photo(chat_id, new_path)

    def salt_n_pepper_photo(self, chat_id, img_path):
        img = Img(img_path)
        img.salt_n_pepper()
        new_path = img.save_img()
        self.send_photo(chat_id, new_path)

    def concat_photo(self, chat_id, orig_img_path, img_path, direction):
        img = Img(orig_img_path)
        other_img = Img(img_path)
        img.concat(other_img, direction)
        new_path = img.save_img()
        self.send_photo(chat_id, new_path)

    def segment_photo(self, chat_id, img_path):
        img = Img(img_path)
        img.segment()
        new_path = img.save_img()
        self.send_photo(chat_id, new_path)

    def handle_message(self, msg):
        logger.info(f'Incoming message 1: {msg}')
        possible_captions = ['blur', 'contour', 'rotate', 'salt_n_pepper', 'concat', 'segment']

        if self.is_current_msg_photo(msg):
            try:
                logger.info('photo arrived')
                caption = msg.get("caption", "")

                concat_options = ['horizontal', 'vertical', "concat,horizontal", "concat,vertical"]
                if not caption:
                    logger.error('Photo without a caption - impossible to processing')
                    self.send_text(msg['chat']['id'], "We cannot process a photo without caption. "
                                                      "Please send a photo with a caption."
                                                      f"Possible captions: {', '.join(possible_captions)}")
                else:
                    caption = caption.lower()
                    if caption not in possible_captions and caption not in concat_options:
                        logger.error(f'unsupported caption: {caption}')
                        self.send_text(msg['chat']['id'], f"Unsupported caption <{caption}>."
                                                          f" Choose one of : {', '.join(possible_captions)}")
                    else:
                        path = self.download_user_photo(msg)
                        chat_id = msg['chat']['id']

                        if caption == 'blur':
                            self.blur_photo(chat_id, path)
                        elif caption == 'contour':
                            self.contour_photo(chat_id, path)
                        elif caption == 'rotate':
                            self.rotate_photo(chat_id, path)
                        elif caption == 'salt_n_pepper':
                            self.salt_n_pepper_photo(chat_id, path)
                        elif caption == 'segment':
                            self.segment_photo(chat_id, path)
                        elif caption == 'concat' or 'horizontal' or 'vertical':
                            if self.data is None:
                                self.data = path
                                self.send_text(chat_id, f"Send another photo for concatenation and choose direction : "
                                                        f"horizontal or vertical")
                            else:
                                direction = None
                                if caption.find(',') != -1:
                                    res = caption.split(',')
                                    direction = res[-1]
                                elif caption in concat_options:
                                    direction = caption
                                else:
                                    direction = 'horizontal'

                                self.concat_photo(chat_id, self.data, path, direction)
                                self.data = None
                        else:
                            self.send_text(chat_id, f"The caption <{caption}> is under construction.")
            except NotImplementedError as e:
                self.data = None
                self.send_text(chat_id, f"Under construction.")
            except ValueError | RuntimeError as e:
                self.data = None
                self.send_text(chat_id, e)
        else:
            self.send_text(msg['chat']['id'], f"Hi {msg['chat']['first_name']}, welcome to our image processing bot."
                                              f" Please send a photo and choose one of a following captions:{'\n'}"
                                              f"{', '.join(possible_captions)}")
