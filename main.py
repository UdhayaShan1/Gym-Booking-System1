# Rolex Alpha 0.1.0

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

##############<<<USER CREATION>>>##############

#State machines for booking process to create user profile
class Form(StatesGroup):
    set_name = State()
    set_room = State()
    change_name = State()
    change_room = State()
    
#State machines for booking process to create a sequential process (in progress)
class Book(StatesGroup):
    picking_looking = State()
    picking_booked = State()

#Local dictionary usage for user creation... probably will be deprecated
users = {}
# For local storage
class User:
    def __init__(self, teleId):
        self.teleId = teleId
        self.name = None
        self.room = None

#Probably will use to handle user familirization with bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state : FSMContext):
    await message.reply("Thank you for using our gym booking bot, powered by Aiogram and MySQL\nVersion: 0.1.0\nCreated by Rolex\nContact @frostbitepillars and @ for any queries")
    user_id = message.from_user.id
    # Now we check if user is already in our system
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (user_id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult != None:
        await message.reply("You are already registered, if you would like to change details... ")
    else:
        await message.reply("Appears either you are not in the system, likely due to new Telegram account\nPlease Register Again!")
        await message.reply("Let's begin by typing your name")
        user = User(user_id)
        users[user_id] = user
        await state.set_state(Form.set_name)

@dp.message_handler(state=Form.set_name)
async def set_name(message: types.Message, state : FSMContext):
    user = users[message.from_user.id]
    user.name = message.text
    await message.reply("Okay, what is your room number")
    await state.set_state(Form.set_room)

@dp.message_handler(state=Form.set_room)
async def set_room(message: types.Message, state : FSMContext):
    user = users[message.from_user.id]
    user.room = message.text

    #Insert into SQL database
    sqlFormula = "INSERT INTO user (teleId, roomNo, name) VALUES (%s, %s, %s)"
    data = (message.from_user.id, user.room, user.name)
    mycursor.execute(sqlFormula, data)
    db.commit()

    await message.reply("Okay, profile is set, use /myinfo to check")
    await state.finish()

@dp.message_handler(commands=['myinfo'])
async def myinfo(message: types.Message):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered, please /start to begin profile creation")
    else:
        await message.reply("Your name is " + myresult[-1] + "\nYour room number is " + myresult[-2])

@dp.message_handler(commands=['namechg'])
async def chg_name(message: types.Message, state : FSMContext):
    await message.reply("Okay, what would you like to change your name to?")
    await state.set_state(Form.change_name)

@dp.message_handler(state=Form.change_name)
async def chg_nameHandler(message: types.Message, state : FSMContext):
    sqlFormula = "UPDATE user SET name = %s WHERE teleId = %s"
    data = (message.text, message.from_id, )
    mycursor.execute(sqlFormula, data)
    db.commit()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()

@dp.message_handler(commands=['roomchg'])
async def chg_room(message: types.Message, state : FSMContext):
    await message.reply("Okay, what would you like to change your room to?")
    await state.set_state(Form.change_room)

@dp.message_handler(state=Form.change_room)
async def chg_roomHandler(message: types.Message, state : FSMContext):
    sqlFormula = "UPDATE user SET roomNo = %s WHERE teleId = %s"
    data = (message.text, message.from_id, )
    mycursor.execute(sqlFormula, data)
    db.commit()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()



    



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
