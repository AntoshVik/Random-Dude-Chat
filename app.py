from aiogram import Bot, types
import asyncio
import logging
from aiogram.dispatcher import Dispatcher
from aiogram.utils.emoji import emojize
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.utils import executor
from aiogram.types.message import ContentType
from aiogram.utils.callback_data import CallbackData
from contextlib import suppress
from aiogram import types
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
print("Bot running...")

queue_persons_list = [] #Очередь ожидания

list_of_chats = [] #Список чатов кто с кем общается




class Person:
    def __init__(self, user_id: int, first_name: str):
        self.user_id = user_id
        self.first_name = first_name

    def get_Person_id(self):
        return self.user_id

    def get_Person_name(self):
        return self.first_name

class Chat:
    def __init__(self, first: int, second: int):
        self.first = first
        self.second = second

    def get_Chat_persons(self):
        return self.first, self.second

    def get_Chat_first(self):
        return self.first

    def get_Chat_second(self):
        return self.second




def who_is_Opponent(person: int):
    for x in range(len(list_of_chats)):
        (first, second) = Chat.get_Chat_persons(list_of_chats[x])
        if first == person:
            return second

def destroy_Chat(first: int):
    second = who_is_Opponent(first)
    for x in range(len(list_of_chats)):
        if Chat.get_Chat_first(list_of_chats[x]) == first:
            list_of_chats.pop(x)
    for y in range(len(list_of_chats)):
        if Chat.get_Chat_first(list_of_chats[y]) == second:
            list_of_chats.pop(y)
    return first, second

def is_Person_in_Chat(person: int):
    for x in range(len(list_of_chats)):
        (first, second) = Chat.get_Chat_persons(list_of_chats[x])
        if first == person or second == person:
            return True
    return False



@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):

    hello_text = "Добро пожаловать в сервис VolkiTechRDC! " + \
                "Здесь вы можете общаться с незнакомцем до тех пор, пока одному из собеседников не надоест."
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.clean()
    keyboard.add(types.KeyboardButton(text="!!! Начать общение !!!"))
    await bot.send_message(message.from_user.id, text=hello_text, reply_markup=keyboard)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(message: types.Message):
    if message.text == "!!! Начать общение !!!" :
        if(is_Person_in_Chat(message.from_user.id)):
            await bot.send_message(message.from_user.id, text="Вы уже в чате!")
        else:
            queue_persons_list.append(Person(message.from_user.id, message.from_user.first_name))
            
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.clean()
            keyboard.add(types.KeyboardButton(text="!!! Отмена поиска !!!"))
            await bot.send_message(message.from_user.id, text="Ищем оппонента...", reply_markup=keyboard)
            if(len(queue_persons_list) >= 2):
                current_opponent = queue_persons_list.pop(0)
                remote_opponent = queue_persons_list.pop(0)
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.clean()
                keyboard.add(types.KeyboardButton(text="!!! Закончить общение !!!"))
                await bot.send_message(Person.get_Person_id(current_opponent), text="Имя вашего оппонента: " + Person.get_Person_name(remote_opponent), reply_markup=keyboard)
                await bot.send_message(Person.get_Person_id(remote_opponent), text="Имя вашего оппонента: " + Person.get_Person_name(current_opponent), reply_markup=keyboard)
                list_of_chats.append(Chat(Person.get_Person_id(current_opponent), Person.get_Person_id(remote_opponent)))
                list_of_chats.append(Chat(Person.get_Person_id(remote_opponent), Person.get_Person_id(current_opponent)))
    elif message.text == "!!! Закончить общение !!!" :
        if not is_Person_in_Chat(message.from_user.id):
            await bot.send_message(message.from_user.id, text="Вы не в чате!")
        else:
            current, remote = destroy_Chat(message.from_user.id)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.clean()
            keyboard.add(types.KeyboardButton(text="!!! Начать общение !!!"))
            await bot.send_message(message.from_user.id, text="Вы разорвали общение", reply_markup=keyboard)
            if current != message.from_user.id:
                await bot.send_message(current, text="Оппонент разорвал общение", reply_markup=keyboard)
            elif remote != message.from_user.id:
                await bot.send_message(remote, text="Оппонент разорвал общение", reply_markup=keyboard)
    elif message.text == "!!! Отмена поиска !!!":
            for x in range(len(queue_persons_list)):
                if Person.get_Person_id(queue_persons_list[x])  == message.from_user.id and Person.get_Person_name(queue_persons_list[x]) == message.from_user.first_name:
                    queue_persons_list.pop(x)
                    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    keyboard.clean()
                    keyboard.add(types.KeyboardButton(text="!!! Начать общение !!!"))
                    await bot.send_message(message.from_user.id, text="Вы вышли из очереди", reply_markup=keyboard)
            await bot.send_message(message.from_user.id, text="Вы не в очереди")
    
    elif message.text:
        if is_Person_in_Chat(message.from_user.id):
            await bot.send_message(who_is_Opponent(message.from_user.id), text=message.text)
            

    else:
        message_text = "Команда не распознана"
        await message.reply(message_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
