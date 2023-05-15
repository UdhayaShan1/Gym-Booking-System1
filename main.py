# Rolex Alpha 0.1.3
#Update to 0.2.X only when booking logic is properly started

#Modules to be imported
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
import aiogram.utils.markdown as md
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
import pickle
import logging
from datetime import *
import re
import aiogram.utils.markdown as md
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
    #set_phone = State()
    set_room = State()
    set_spotter_name = State()
    set_spotter_room = State()
    change_name = State()
    change_room = State()
    change_spotter_name = State()
    change_spotter_room = State()
    delete_details = State()
    
#State machines for booking process to create a sequential process (in progress)
class Book(StatesGroup):
    picked_date= State()
    picked_time = State()

#Local dictionary usage for user creation... probably will be deprecated
users = {}
# For local storage
class User:
    def __init__(self, teleId):
        self.teleId = teleId
        self.name = None
        self.room = None
        self.spotter_name = None
        self.spotter_room = None

#Force exit out of any state
@dp.message_handler(state="*", commands=['exit'])
async def exit(message: types.Message, state : FSMContext):
    curr_state  = await state.get_state()
    if curr_state == None:
        await message.reply("Nothing to exit")
    else:
        await message.reply("Okay left current state, use / to continue with avaliable commands")
    await state.finish()

#Probably will use to handle user familirization with bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state : FSMContext):
    await message.reply("Thank you for using our gym booking bot, powered by Aiogram and MySQL\nVersion: 0.1.3\nCreated by Rolex\nContact @frostbitepillars and @ for any queries")
    user_id = message.from_user.id
    # Now we check if user is already in our system
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (user_id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult != None:
        await message.reply("You are already registered, if you would like to change details, type / and check appropriate commands ")
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

#Room number validation
def check_string_format(string):
    pattern = r"^\d{2}-\d{2}[a-zA-Z]?$"
    if re.match(pattern, string):
        return True
    else:
        return False

@dp.message_handler(state=Form.set_room)
async def set_room(message: types.Message, state : FSMContext):
    user = users[message.from_user.id]
    s = message.text
    if check_string_format(s):
        user.room = s
        """
        #Insert into SQL database
        sqlFormula = "INSERT INTO user (teleId, roomNo, name) VALUES (%s, %s, %s)"
        data = (message.from_user.id, user.room, user.name)
        mycursor.execute(sqlFormula, data)
        db.commit()
        
        options = ["Telegram", "Phone"]

        buttons = [InlineKeyboardButton(
            text=md.text(button_label),
            callback_data=f"{button_label}"
        ) for button_label in options]

        calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
        await message.reply("Okay, we require your spotter's details, would like to add their Telegram Handle or Phone No?", reply_markup=calendar_keyboard)
        """
        await message.reply("Okay, what is your spotter's name?")
        await state.set_state(Form.set_spotter_name)
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

@dp.message_handler(state=Form.set_spotter_name)
async def set_spotter_name(message: types.Message, state : FSMContext):
    user = users[message.from_user.id]
    user.spotter_name = message.text
    await message.reply("Okay what is their Room No?")
    await state.set_state(Form.set_spotter_room)

@dp.message_handler(state=Form.set_spotter_room)
async def set_spotter_room(message: types.Message, state : FSMContext):
    user = users[message.from_user.id]
    s = message.text
    if check_string_format(s):
        user.spotter_room = s
        #Insert into SQL database
        sqlFormula = "INSERT INTO user (teleId, roomNo, name, spotterName, spotterRoomNo) VALUES (%s, %s, %s, %s, %s)"
        data = (message.from_user.id, user.room, user.name, user.spotter_name, user.spotter_room)
        mycursor.execute(sqlFormula, data)
        db.commit()
        await message.reply("Okay info set, check via /myinfo")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

@dp.message_handler(commands=['myinfo'])
async def myinfo(message: types.Message):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered, please /start to begin profile creation")
    else:
        await message.reply("Your name is " + myresult[3] + "\nYour room number is " + myresult[2] +"\nYour spotter is " + myresult[-2] + "\nYour spotter room number is " + myresult[-1])

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
    await message.reply("Okay, what would you like to change your registered room to?")
    await state.set_state(Form.change_room)

@dp.message_handler(state=Form.change_room)
async def chg_roomHandler(message: types.Message, state : FSMContext):
    s = message.text
    if check_string_format(s):
        sqlFormula = "UPDATE user SET roomNo = %s WHERE teleId = %s"
        data = (s, message.from_id, )
        mycursor.execute(sqlFormula, data)
        db.commit()
        await message.reply("Okay done, use /myinfo to check")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

@dp.message_handler(commands=['spotternamechg'])
async def chg_name(message: types.Message, state : FSMContext):
    await message.reply("Okay, what would you like to change your spotter's name to?")
    await state.set_state(Form.change_spotter_name)

@dp.message_handler(state=Form.change_spotter_name)
async def chg_nameHandler(message: types.Message, state : FSMContext):
    sqlFormula = "UPDATE user SET spotterName = %s WHERE teleId = %s"
    data = (message.text, message.from_id, )
    mycursor.execute(sqlFormula, data)
    db.commit()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()

@dp.message_handler(commands=['spotterroomchg'])
async def chg_room(message: types.Message, state : FSMContext):
    await message.reply("Okay, what would you like to change your registered spotter's room number to?")
    await state.set_state(Form.change_spotter_room)

@dp.message_handler(state=Form.change_spotter_room)
async def chg_roomHandler(message: types.Message, state : FSMContext):
    s = message.text
    if check_string_format(s):
        sqlFormula = "UPDATE user SET spotterRoomNo = %s WHERE teleId = %s"
        data = (s, message.from_id, )
        mycursor.execute(sqlFormula, data)
        db.commit()
        await message.reply("Okay done, use /myinfo to check")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")


@dp.message_handler(state='*', commands=['delete'])
async def deleteMyDetails(message: types.Message, state : FSMContext):
    """
    button1 = KeyboardButton('Yes!')
    button2 = KeyboardButton('No!')
    keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button1).add(button2)
    """

    #Attempt at InLineKeyboard instead
    button3 = InlineKeyboardButton(text="Yes!", callback_data="Yes!")
    button4 = InlineKeyboardButton(text="No!", callback_data="No!")
    keyboard2 = InlineKeyboardMarkup().add(button3).add(button4)
    await message.reply("Are you sure you want to delete your details, this is not undoable\nWe will delete your records from our mySQL database and any attached bookings", reply_markup=keyboard2)
    await state.set_state(Form.delete_details)

"""
@dp.message_handler(state=Form.delete_details)
async def deleteHandler(message: types.Message, state : FSMContext):
    if message.text == "Yes!":
        sqlFormula = "DELETE FROM user WHERE teleId = %s"
        data = (message.from_id, )
        mycursor.execute(sqlFormula, data)
        db.commit()
        await message.reply("Data deleted, use /start to begin user creation again")
    else:
        await message.reply("Data not deleted..")
    #Add code to ammend all associated bookings to have teleId and spotterId to None.
    await state.finish()
"""

@dp.callback_query_handler(state=Form.delete_details)
async def deleteHandler2(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Yes!":
        sqlFormula = "DELETE FROM user WHERE teleId = %s"
        data = (call.from_user.id, )
        mycursor.execute(sqlFormula, data)
        db.commit()
        await call.message.answer("Data deleted, use /start to begin user creation again")
    else:
        await call.message.answer("Data not deleted..")
    #Add code to ammend all associated bookings to have teleId and spotterId to None.
    await state.finish()



##############<<<BOOKING LOGIC>>>##############  

@dp.message_handler(commands=['book'])
async def book(message: types.Message, state: FSMContext):
    #Fetch current time, current date and date in 2 weeks for SQL query, not sure if need adjust GMT looks like based on IDE
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.date()
    current_date_14_forward = (now.date()+timedelta(days=14))
    dates = [current_date + timedelta(days=i) for i in range(14)]
    await message.reply("Sure, let's display available dates\n" +"Current date is "+ str(current_date) +"\nTime is " + str(current_time))
    
    #Lets do this sequentially..
    """
    #Lets fetch our relevant rows
    sqlFormula = "SELECT * FROM booking_slots WHERE timeslot > %s AND date >= %s AND date <= %s"
    data = (current_time, current_date,current_date_14_forward)
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    str1 = ""
    for i in dates:
        str1 += str(i)+"\n"
    #await message.reply(str1)
    """

    # Create a list of button labels for each date
    button_labels = [date.strftime('%Y-%m-%d') for date in dates]

    # Create a list of InlineKeyboardButton objects for each date
    buttons = [InlineKeyboardButton(
        text=md.text(button_label),
        callback_data=f"date_{button_label}"
    ) for button_label in button_labels]

    # Create an InlineKeyboardMarkup object with the list of buttons
    calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    await message.reply("Select date", reply_markup=calendar_keyboard)
    await state.set_state(Book.picked_date)


@dp.callback_query_handler(state=Book.picked_date)
async def bookStageViewSlots(call: types.CallbackQuery, state : FSMContext):
    #await call.message.answer(call.data)
    now = datetime.now()
    if now.date() != call.data:
        sqlFormula = "SELECT * FROM booking_slots WHERE date = %s"
        data = (str(call.data)[5:], )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()

        time_button_labels = []
        str1 = "Slots at a glance\n"
        for i in myresult:
            if i[3] == 0:
                str1 += str(i[2])[:-3] + " ✅\n"
                time_button_labels.append(str(i[2])[:-3])
            else:
                str1 += str(i[2])[:-3] + " ❌\n"
        
        buttons = [InlineKeyboardButton(
            text=md.text(button_label),
            callback_data=f"time_{button_label}"
        ) for button_label in time_button_labels]
            
        calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
        await call.message.answer(str1, reply_markup=calendar_keyboard)

    else:
        current_time = now.strftime("%H:%M:%S")
        sqlFormula = "SELECT * FROM booking_slots WHERE date = %s"
        data = (str(call.data)[5:], current_time, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        for i in myresult:
            await call.message.answer(i)
    
    await state.finish()





#Leave this at bottom to catch unknown commands or text input by users
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("Unknown command, use / to check for available commands")

@dp.callback_query_handler()
async def echo1(call: types.CallbackQuery):
    await call.message.answer("You may have clicked on a previous in-line keyboard button")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
