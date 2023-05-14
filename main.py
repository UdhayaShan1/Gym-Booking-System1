# Rolex 130523 2145

# Core modules
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
import aiogram.utils.markdown as md
import pickle
import logging
from datetime import *


# Database connection, we will use mySQL and localhost for now
import mysql.connector
pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd=pwd,
    database="testdatabase"
)

mycursor = db.cursor()

logging.basicConfig(level=logging.INFO)

# Set up dispatcher
TOKEN = None
with open("includes\dot_token.txt") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



###########################################<<<MAIN CODE>>>###########################################



#State machines for booking process to create a sequential process (in progress)
class Book(StatesGroup):
    picking_looking = State()
    picking_booked = State()

#Local dictionary usage... probably will be deprecated
users = {}
# For local storage
class User:
    def __init__(self, teleId):
        self.teleId = teleId
        self.nusnetId = None

#Probably will use to handle user familirization with bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Hi, welcome to our bot")
    user_id = message.from_user.id
    # Now we check if user is already in our system

@dp.message_handler(commands=['book'])
async def book(message: types.Message):
    await message.reply("Sure, let's display available dates")
    #Fetch current time, current date and date in 2 weeks for SQL query, not sure if need adjust GMT looks like based on IDE
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.date()
    current_date_14_forward = (now.date()+timedelta(days=14))

    #Lets fetch our relevant rows
    sqlFormula = "SELECT * FROM booking_slots WHERE timeslot > %s AND date >= %s AND date <= %s"
    data = (current_time, current_date,current_date_14_forward)
    mycursor.execute(sqlFormula, data)
    result = mycursor.fetchall()
    
    







if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
