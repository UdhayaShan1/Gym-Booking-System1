# Rolex Alpha 0.2.6

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
import random
import string
from email.message import EmailMessage
import ssl
import smtplib


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
    set_nusnet = State()
    set_name = State()
    #set_phone = State()
    set_room = State()
    set_spotter_name = State()
    set_spotter_room = State()
    change_name = State()
    change_room = State()
    change_spotter_name = State()
    change_spotter_room = State()
    otp_verify = State()
    delete_details = State()
    
#State machines for booking process to create a sequential process (in progress)
class Book(StatesGroup):
    picked_date= State()
    picked_time = State()
    additional_time = State()
    repicked_date = State()
    picked_unbook_date = State()
    picked_unbook_additional = State()

#Dictionary for user creation Useful for profile creation.
users = {}
class User:
    def __init__(self, teleId):
        self.teleId = teleId
        self.nusnet = None
        self.otp = None
        self.name = None
        self.room = None
        self.spotter_name = None
        self.spotter_room = None

#Dictionary for booking creation. No proper use yet... probably will be deprecated.             
bookings = {}
class Booking:
    def __init__(self, teleId):
        self.teleId = teleId
        self.date = None
        self.time = None

#Force exit out of any state
@dp.message_handler(state="*", commands=['exit'])
async def exit(message: types.Message, state: FSMContext):
    """
    Handler to force exit out of any state in the FSM context.

    Parameters:
        message (types.Message): The message triggering the command.
        state (FSMContext): The FSM context for managing states.

    Returns:
        None

    Raises:
        None

    Usage:
        The handler is triggered when the "/exit" command is used. It checks if there is an active state.
        - If there is no active state, it sends a response indicating that there is nothing to exit.
        - If there is an active state, it sends a response acknowledging that the user has left the current state.
          It suggests using "/" to continue with the available commands.
        Finally, it finishes the current state using `state.finish()`, resetting the state machine.

    Example:
        User: /exit
        Bot: Nothing to exit

        User (in an active state): /exit
        Bot: Okay, left current state. Use / to continue with available commands
    """
    curr_state = await state.get_state()
    if curr_state is None:
        await message.reply("Nothing to exit")
    else:
        await message.reply("Okay, left current state. Use / to continue with available commands")
    await state.finish()

def nusnetRetriever(id):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    return myresult[-2]


#Probably will use to handle user familirization with bot
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state : FSMContext):
    """
    Handler for the '/start' command. Initializes the registration process for the user.
    
    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context of the conversation.

    Usage:
        /start - Start the gym booking bot and register (if not already registered).

    Example:
        User (not registered): /start
        Bot: Begins form creation process

        User (registered): /start
        Bot: Already registered, directs on how to change info if needed

    """
    await message.reply("Thank you for using our gym booking bot, powered by Aiogram, Python and MySQL.\nVersion: 0.2.7 Track progress and read patch notes on GitHub!\nCreated by Rolex\nContact @frostbitepillars and @ for any queries")
    user_id = message.from_user.id
    # Now we check if user is already in our system
    """
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (user_id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult != None:
        await message.reply("You are already registered, if you would like to change details, type / and check appropriate commands ")
    else:
        await message.reply("Appears either you are not in the system!\nPlease Register!")
        await message.reply("Lets begin by typing your NUSNET ID!")
        #await message.reply("Let's begin by typing your name")
        user = User(user_id)
        users[user_id] = user
        await state.set_state(Form.set_nusnet)
    """
    await message.reply("Okay, first begin by typing your NUSNET id to check if your profile is created! 👍")
    await state.set_state(Form.set_nusnet)

#Check if valid nusnet id
def validnusNet(input_string):
    pattern = r'^e\d{7}$'  # Regex pattern to match "e" followed by 7 digits
    match = re.match(pattern, input_string)
    return match is not None


@dp.message_handler(state=Form.set_nusnet)
async def set_nusnet(message: types.Message, state : FSMContext):
    users[message.from_user.id] = User(message.from_user.id)
    user = users[message.from_user.id]
    #user = users[message.from_user.id]
    nusnet = str(message.text).lower()
    if validnusNet(nusnet) == False:
        await message.reply("Please type valid NUSNET id!")
    else:
        sqlFormula = "SELECT * FROM user WHERE nusnet = %s"
        data = (nusnet, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchone()


        sqlFormula = "SELECT * FROM user WHERE nusnet = %s AND name IS NOT NULL AND roomNo IS NOT NULL AND spotterName IS NOT NULL AND spotterRoomNo IS NOT NULL;"
        data = (nusnet, )
        mycursor.execute(sqlFormula, data)
        myresult1 = mycursor.fetchone()
        if myresult == None:
            user.nusnet = nusnet
            await message.reply("You have not been registered yet! Begin by typing your name")
            await state.set_state(Form.set_name)
        elif myresult1 == None:
            user.nusnet = nusnet
            await message.reply("Your profile creation has not been completed! Begin by typing your name")
            await state.set_state(Form.set_name)
        else:
            await message.reply("You have already been registered! Use /myinfo to check again")
            await state.finish()

# Generate a random OTP
async def generate_otp():
    otp = ''.join(random.choices(string.digits, k=4))
    return otp

#Send otp to user
async def send_otp(nusnet):
    email_receiver = nusnet+"@u.nus.edu"
    email_sender = "chad.ionos2@gmail.com"
    email_pw = None
    with open("includes\gmailPwd.txt") as f:
        email_pw = f.read().strip()
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em["Subject"] = "Your FitBook OTP"
    otp = await generate_otp()
    em.set_content("Your OTP is " + otp)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_pw)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    return otp

    

@dp.message_handler(state=Form.set_name)
async def set_name(message: types.Message, state : FSMContext):
    """
    Handler for setting the user's name during the registration process.

    Usage:
        [User Input] - Set the user's name during the registration process.

    Example:
        John Doe

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context of the conversation.
    """
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
    """
    Handler for setting the user's room number during the registration process.

    Usage:
        [User Input] - Set the user's room number during the registration process.
    
    Example:
        11-12

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context of the conversation.
    """
    user = users[message.from_user.id]
    s = message.text
    if check_string_format(s):
        user.room = s
        await message.reply("Okay, what is your spotter's name?")
        await state.set_state(Form.set_spotter_name)
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

@dp.message_handler(state=Form.set_spotter_name)
async def set_spotter_name(message: types.Message, state : FSMContext):
    """
    Handler for setting the spotter's name during the registration process.

    Usage:
        [User Input] - Set the spotter's name during the registration process.
    
    Example:
        John Doe

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context of the conversation.
    """
    user = users[message.from_user.id]
    user.spotter_name = message.text
    await message.reply("Okay what is their Room No?")
    await state.set_state(Form.set_spotter_room)

@dp.message_handler(state=Form.set_spotter_room)
async def set_spotter_room(message: types.Message, state : FSMContext):
    """
    Handler for setting the spotter's room number during the registration process.
    If valid room, add user into SQL database.

    Usage:
        [User Input] - Set the spotter's room number during the registration process.

    Example:
        11-12F

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state context of the conversation.
    """
    user = users[message.from_user.id]
    s = message.text
    if check_string_format(s):
        user.spotter_room = s
        sqlFormula = "SELECT * FROM user WHERE nusnet = %s"
        data = (user.nusnet, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchone()
        if myresult == None:
            #Insert into SQL database
            sqlFormula = "INSERT INTO user (teleId, roomNo, name, spotterName, spotterRoomNo, nusnet) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (message.from_user.id, user.room, user.name, user.spotter_name, user.spotter_room, user.nusnet)
            mycursor.execute(sqlFormula, data)
            db.commit()
        else:
            sqlFormula = "UPDATE user SET teleId = %s, roomNo = %s, name = %s, spotterName = %s, spotterRoomNo = %s WHERE nusnet = %s"
            data = (message.from_user.id, user.room, user.name, user.spotter_name, user.spotter_room, user.nusnet, )
            mycursor.execute(sqlFormula, data)
            db.commit()
        await message.reply("Okay info set, check via /myinfo")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

@dp.message_handler(commands=['myinfo'])
async def myinfo(message: types.Message):
    """
    Handler for retrieving the user's profile information.

    Usage:
        /myinfo - Retrieve the user's profile information.

    Args:
        message (types.Message): The incoming message object.
    """
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered, please /start to begin profile creation")
    else:
        verifiedStr = ""
        if myresult[-1] == 0:
            verifiedStr = "\n\nYou are not verified yet, proceed to /verify!"
        else:
            verifiedStr = "\n\nYou are verified!"
        await message.reply("Your NUSNET is " + myresult[-2] + "\n\nYour name is " + myresult[3] + "\n\nYour room number is " + myresult[2] +"\n\nYour spotter is " + myresult[-4] + "\n\nYour spotter room number is " + myresult[-3] + verifiedStr)

@dp.message_handler(commands=['namechg'])
async def chg_name(message: types.Message, state : FSMContext):
    """
    Handler for changing the user's name.

    Usage:
        /namechg - Initiate the name change process.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    await message.reply("Okay, what would you like to change your name to?")
    await state.set_state(Form.change_name)

@dp.message_handler(state=Form.change_name)
async def chg_nameHandler(message: types.Message, state : FSMContext):
    """
    Handler for changing the user's name.

    Usage:
        [User Input] - Provide the new name to change.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    sqlFormula = "UPDATE user SET name = %s WHERE teleId = %s"
    data = (message.text, message.from_id, )
    mycursor.execute(sqlFormula, data)
    db.commit()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()

@dp.message_handler(commands=['roomchg'])
async def chg_room(message: types.Message, state : FSMContext):
    """
    Handler for changing the user's registered room.

    Usage:
        /roomchg - Initialise the room number change process

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    await message.reply("Okay, what would you like to change your registered room to?")
    await state.set_state(Form.change_room)

@dp.message_handler(state=Form.change_room)
async def chg_roomHandler(message: types.Message, state : FSMContext):
    """
    Handler for changing the user's registered room.

    Usage:
        [User Input] - Provide the new room number in the format XX-XX or XX-XXX.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
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
    """
    Handler for changing the user's spotter's name.

    Usage:
        /spotternamechg - Initialise the spotter's name change process

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    await message.reply("Okay, what would you like to change your spotter's name to?")
    await state.set_state(Form.change_spotter_name)

@dp.message_handler(state=Form.change_spotter_name)
async def chg_nameHandler(message: types.Message, state : FSMContext):
    """
    Handler for updating the user's spotter's name.

    Usage:
        [User Input] - Provide the new name for the spotter.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    sqlFormula = "UPDATE user SET spotterName = %s WHERE teleId = %s"
    data = (message.text, message.from_id, )
    mycursor.execute(sqlFormula, data)
    db.commit()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()

@dp.message_handler(commands=['spotterroomchg'])
async def chg_room(message: types.Message, state : FSMContext):
    """
    Handler for changing the user's registered spotter's room number.

    Usage:
        [Command] - /spotterroomchg

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    await message.reply("Okay, what would you like to change your registered spotter's room number to?")
    await state.set_state(Form.change_spotter_room)

@dp.message_handler(state=Form.change_spotter_room)
async def chg_roomHandler(message: types.Message, state : FSMContext):
    """
    Handler for changing the user's spotter's room number.

    Usage:
        [User Input] - Provide the new room number for the spotter.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
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

@dp.message_handler(commands=['verify'])
async def verify(message: types.Message, state : FSMContext):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not in the system, please /start first 👍")
    else:
        if myresult[-1] == 1:
            await message.reply("You are already verified!")
        else:
            if message.from_user.id not in users:
                user = User(message.from_user.id)
                users[message.from_user.id] = user
            else:
                user = users[message.from_user.id]

            otp = await send_otp(myresult[-2])
            user.otp = otp
            await message.reply("Okay, OTP sent to your NUSNET email, please type it out")
            await state.set_state(Form.otp_verify)

@dp.message_handler(state=Form.otp_verify)
async def otp_handler(message: types.Message, state : FSMContext):
    #print(users)
    otp_given = message.text
    user = users[message.from_user.id]
    if otp_given == user.otp:
        sqlFormula = "UPDATE user SET verifiedTele = %s WHERE teleId = %s"
        data = (1, message.from_user.id, )
        mycursor.execute(sqlFormula, data)
        db.commit()
        await message.reply("Woo! 😺 You are now verified and can proceed to book!")
        await state.finish()
    else:
        await message.reply("😔 Sorry, OTP is not correct, try /verify again!")
        await state.finish()

@dp.message_handler(state='*', commands=['delete'])
async def deleteMyDetails(message: types.Message, state : FSMContext):
    """
    Handler for deleting user details.

    Usage:
        [Command] - /delete

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """

    """
    button1 = KeyboardButton('Yes!')
    button2 = KeyboardButton('No!')
    keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button1).add(button2)
    """

    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered in the system.")
    else:
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
    """
    Callback handler for confirming the deletion of user details.

    Usage:
        [CallbackData] - "Yes!" or "No!"

    Args:
        call (types.CallbackQuery): The incoming callback query object.
        state (FSMContext): The state object for managing conversation state.
    """
    if call.data == "Yes!":
        nusnet = nusnetRetriever(call.from_user.id)
        sqlFormula = "UPDATE user SET teleId = %s, roomNo = %s, name = %s, spotterName = %s, spotterRoomNo = %s, verifiedTele = 0 WHERE teleId = %s"
        data = (None, None, None, None, None, call.from_user.id, )
        mycursor.execute(sqlFormula, data)
        db.commit()
        
        sqlFormula = "UPDATE booking_slots SET is_booked = 0, assoc_teleId = %s, assoc_nusnet = %s WHERE (assoc_teleId = %s OR assoc_nusnet = %s)"
        mycursor.execute(sqlFormula, (None, None, call.from_user.id, nusnet, ))
        db.commit()
        await call.message.answer("Data deleted, use /start to begin user creation again")
    else:
        await call.message.answer("Data not deleted..")
    #Add code to ammend all associated bookings to have teleId and spotterId to None.
    await state.finish()

##############<<<BOOKING LOGIC>>>##############  

@dp.message_handler(commands=['book'])
async def book(message: types.Message, state: FSMContext):
    """
    Command handler for the '/book' command.
    Allows users to book an appointment.

    This code defines a command handler that allows users to book an appointment. 
    It first checks if the user is registered in the system. If not registered, it sends a message to prompt the user to start the profile creation process. 
    If the user is registered, it creates a local booking object and stores it in the bookings dictionary. 
    Next, the current date and time are fetched and displayed to the user. 
    Then, a list of dates for the next 14 days is generated. Each date is converted into a button label and an InlineKeyboardButton object is created for each date. 
    An InlineKeyboardMarkup is created with the list of buttons, and a message with the calendar keyboard for date selection is sent to the user. 
    The conversation state is set to Book.picked_date to track the progress of the conversation.

    Usage:

    User sends the /book command to initiate the booking process.
    The function checks if the user is registered in the system by querying the database.
    If the user is not registered, a message is sent to prompt the user to start the profile creation process.
    If the user is registered, a local booking object is created and stored in the bookings dictionary.
    The current date, current time, and dates for the next 14 days are fetched.
    The current date and time are displayed to the user.
    A list of button labels is created for each date.
    InlineKeyboardButton objects are created for each date using the button labels.
    An InlineKeyboardMarkup object is created with the list of buttons.
    A message with the calendar keyboard for date selection is sent to the user.
    The conversation state is set to Book.picked_date to track the progress of the conversation.

    Example:

    User: /book

    Bot: Sure, let's display available dates
    Current date is 2023-05-18
    Time is 15:30:00

    Bot: Select date
    [Inline keyboard with date options is displayed]
    In the example above, the user sends the /book command. The bot responds by displaying the current date and time. It then presents an inline keyboard with date options for the user

    Parameters:
    - message: The message object representing the user's message.
    - state: The FSMContext object for managing the conversation state.
    """
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult != None and myresult[-1] == 0:
        await message.reply("You are not verified yet, proceed to /verify")
    elif myresult == None:
        await message.reply("You are not registered, use /start to begin profile creation")
    else:
        #Create local booking object
        booking_obj = Booking(message.from_user.id)
        bookings[message.from_user.id] = booking_obj
        #Fetch current time, current date and date in 2 weeks for SQL query, not sure if need adjust GMT looks like based on IDE
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.date()
        current_date_14_forward = (now.date()+timedelta(days=14))
        dates = [current_date + timedelta(days=i) for i in range(14)]
        await message.reply("Sure, let's display available dates\n" +"Current date is "+ str(current_date) +"\nTime is " + str(current_time))


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

async def bookCycle(message: types.Message, state: FSMContext, id):
    await message.reply(bookings)
    """
    Function for handling the booking cycle.
    Allows users to repick a date for booking.
    Essentially to handle a go-back function.

    Parameters:
    - message: The message object representing the user's message.
    - state: The FSMContext object for managing the conversation state.
    """
    #Check if user is in the system in the first place
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered, use /start to begin profile creation")
    else:
        #Fetch current time, current date and date in 2 weeks for SQL query, not sure if need adjust GMT looks like based on IDE
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.date()
        current_date_14_forward = (now.date()+timedelta(days=14))
        dates = [current_date + timedelta(days=i) for i in range(14)]
        await message.reply("Sure, let's display available dates\n" +"Current date is "+ str(current_date) +"\nTime is " + str(current_time))
    
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

#To be completed
def dateValidator(s):
    pass
#To be completed
def timeValidator(s):
    pass

@dp.callback_query_handler(state=Book.picked_date)
async def bookStageViewSlots(call: types.CallbackQuery, state : FSMContext):
    """
    Callback query handler for viewing available time slots for booking.

    Usage:

    This callback query handler is triggered when the user selects a date from the calendar keyboard presented after the /book command. 
    It processes the selected date and checks if it is in the past. 
    
    If the selected date is in the past, a message is sent to the user informing them that booking in the past is not allowed and the conversation is finished. 
    If the selected date is valid, the handler retrieves the available time slots for the selected date from the database.
    If the selected date is different from the current date, the handler retrieves all time slots for that date and generates a message displaying the availability of each time slot. 
    The user can select a specific time slot for booking from the displayed options.

    If the selected date is the current date, the handler retrieves only the available time slots from the current time onwards. 
    If no available time slots are found, a message is sent to the user indicating that there are no more available time slots for the day. 
    Otherwise, the available time slots are displayed, and the user can select a specific time slot for booking.
    After displaying the available time slots, the conversation state is set to Book.picked_time to track the progress of the conversation.

    Example:

    User: [Selects a date from the calendar keyboard]

    Bot: [Displays the available time slots for the selected date]
        Slots at a glance
        09:00 ✅
        10:00 ❌
        11:00 ✅
        12:00 ✅
        [Inline keyboard with time options is displayed]
    In the example above, the user selects a date from the calendar keyboard. 
    The bot responds by displaying the available time slots for that date. 
    Each time slot is marked with either a ✅ (available) or ❌ (not available). 
    The user can then select a specific time slot from the displayed options.
    


    Parameters:
    - call: The CallbackQuery object representing the callback query.
    - state: The FSMContext object for managing the conversation state.
    """
    #await call.message.answer(call.data)
    booking_obj = bookings[call.from_user.id]
    booking_obj.date = str(call.data)[5:]
    now = datetime.now()
    print(now.date(), call.data)
    date1 = now.date()
    date2 = datetime.strptime(str(call.data)[5:], "%Y-%m-%d").date()
    if date1 > date2:
        await call.message.answer("You cannot book in the past, /book to retry")
        await state.finish()
    else:
        if str(now.date()) != str(booking_obj.date):
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
            button1 = InlineKeyboardButton(text="Pick another date", callback_data="Pick another date")
            calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(button1)
            await call.message.answer(str1, reply_markup=calendar_keyboard)
            await state.set_state(Book.picked_time)
        else:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            sqlFormula = "SELECT * FROM booking_slots WHERE date = %s AND timeslot > %s"
            data = (str(call.data)[5:], current_time,)
            mycursor.execute(sqlFormula, data)
            myresult = mycursor.fetchall()
            if len(myresult) == 0:
                await call.message.answer("No more avaliable time slots for the day")
                await state.finish()
            else:
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
                button1 = InlineKeyboardButton(text="Pick another date", callback_data="Pick another date")
                calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(button1)
                await call.message.answer(str1, reply_markup=calendar_keyboard)
                await state.set_state(Book.picked_time)

#This function must be explicitly called if and only if user asks to book agn for same day
async def bookStageViewSlotsCycle(message :types.Message, state : FSMContext, id):
    #await message.reply(message.text)
    #print((bookings.keys()))
    booking_obj = bookings[id]
    now = datetime.now()
    print(now.date(), booking_obj.date)
    date1 = now.date()
    date2 = datetime.strptime(str(booking_obj.date), "%Y-%m-%d").date()
    if date1 > date2:
        await message.reply("You cannot book in the past, /book to retry")
        await state.finish()
    else:
        if str(now.date()) != str(booking_obj.date):
            sqlFormula = "SELECT * FROM booking_slots WHERE date = %s"
            data = (str(booking_obj.date), )
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
                
            button1 = InlineKeyboardButton(text="Pick another date", callback_data="Pick another date")
            calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(button1)
            await message.reply(str1, reply_markup=calendar_keyboard)
            await state.set_state(Book.picked_time)
        else:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            sqlFormula = "SELECT * FROM booking_slots WHERE date = %s AND timeslot > %s"
            data = (str(booking_obj.date), current_time,)
            mycursor.execute(sqlFormula, data)
            myresult = mycursor.fetchall()
            if len(myresult) == 0:
                await message.reply("No more avaliable time slots for the day")
                await state.finish()
            else:
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
                
                button1 = InlineKeyboardButton(text="Pick another date", callback_data="Pick another date")
                calendar_keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons).add(button1)
                await message.reply(str1, reply_markup=calendar_keyboard)
                await state.set_state(Book.picked_time)

@dp.callback_query_handler(state=Book.picked_time)
async def bookStageSelectedTime(call: types.CallbackQuery, state : FSMContext):
    """
    Callback query handler for selecting a specific time slot for booking.

    Parameters:
    - call: The CallbackQuery object representing the callback query.
    - state: The FSMContext object for managing the conversation state.

    Usage:

    This callback query handler is triggered when the user selects a specific time slot for booking from the available options. 
    It checks if the user has selected the option to pick another date. 
    If so, it restarts the booking process by calling the bookCycle function. 
    Otherwise, it retrieves the selected time slot and performs the necessary database operations to book the slot for the user.
    If the user has not booked the maximum number of slots for themselves on that day, the selected time slot is updated in the database as booked, and a confirmation message is sent to the user. 
    If there are still available slots for booking on that day, the user is prompted with a yes/no question asking if they want to book additional slots. 
    The conversation state is set to Book.additional_time to track the progress of the conversation.

    If the user has already booked the maximum number of slots for themselves on that day, a message is sent to the user indicating that they have reached the maximum limit. 
    The conversation is then finished.

    Example:

    User: [Selects a time slot for booking]

    Bot: Okay booked at [Date] [Time]
        Enjoy your workout!

    Bot: Do you want to book additional slots for this day?
        [Inline keyboard with 'Yes' and 'No' options is displayed]
    In the example above, the user selects a specific time slot for booking. 
    The bot confirms the booking and provides the date and time of the booked slot. 
    It then asks the user if they want to book additional slots for the same day. 
    The user can choose to either book more slots by selecting 'Yes' or finish the booking process by selecting 'No'.
    """
    if call.data == "Pick another date":
        await bookCycle(call.message, state, call.from_user.id)
    else:
        booking_obj = bookings[call.from_user.id]
        booking_obj.time = str(call.data)[5:]
        print(booking_obj.time, booking_obj.date)
        sqlFormula = "SELECT * FROM booking_slots WHERE date = %s AND assoc_teleId = %s"
        data = (booking_obj.date, call.from_user.id, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        if myresult == None or len(myresult) <= 2:
            sqlFormula = "UPDATE booking_slots SET is_booked = 1, assoc_teleId = %s, assoc_nusnet = %s WHERE timeslot = %s AND date = %s"
            data = (call.from_user.id, nusnetRetriever(call.from_user.id), str(call.data)[5:], booking_obj.date, )
            mycursor.execute(sqlFormula, data)
            db.commit()
            await call.message.answer("Okay booked at " + booking_obj.date + " " + booking_obj.time + "\nEnjoy your workout!")

            if myresult == None or len(myresult) < 2:
                responses = ["Yes", "No"]
                buttons = [InlineKeyboardButton(
                    text=md.text(button_label),
                    callback_data=f"{button_label}"
                ) for button_label in responses]
                keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
                await call.message.answer("Do you want to book additional slots for this day", reply_markup=keyboard)
                await state.set_state(Book.additional_time)
            else:
                await state.finish()
        else:
            await call.message.answer("Sorry you have booked the maximum number of slots for yourself that day")
            await state.finish()

@dp.callback_query_handler(state=Book.additional_time)
async def responseHandlerforAdditionalSlots(call: types.CallbackQuery, state : FSMContext):
    """
    Allow user to repick more time slots by activating the bookStageViewSlotsCycle function which is essentially
    a non-CallbackQuery version of bookStageViewSlots.
    """
    if call.data == "Yes":
        #await call.message.answer("Debug")
        #await state.set_state(Book.repicked_date)
        #Have to explicity call function as it is neither from query or user message
        await bookStageViewSlotsCycle(call.message, state, call.from_user.id)
    else:
        await call.message.answer("Thank you! Slots booked, use /checkactive to check your bookings! 😃")
        await state.finish()

@dp.message_handler(state='*', commands=['checkactive'])
async def checkMyGymSlots(message: types.Message):
    """
    Message handler for the /checkactive command to retrieve and display the active gym slots booked by the user.

    Parameters:
    - message: The Message object representing the incoming message.

    Usage:

    User sends the /checkactive command to check their active gym slots.
    The function retrieves the current date and time.
    It queries the database to fetch the active slots booked by the user for the current date and time, as well as future dates.
    If no active slots are found, it sends a message response indicating that there are no active slots.
    If active slots are found, it constructs a response message listing the booked slots' date and time.
    The response message is sent back to the user.

    Example:

    User: /checkactive

    Bot: ⌛ Slots booked on

    2023-05-18 on 09:00 👌

    2023-05-19 on 10:30 👌
    """
    curr_date = datetime.now().date()
    curr_time = datetime.now().strftime("%H:%M:%S")
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date = %s AND timeslot > %s"
    data = (message.from_user.id, nusnetRetriever(message.from_user.id), str(curr_date), str(curr_time), )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    res = []
    for i in myresult:
        res.append(i)
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date > %s"
    data = (message.from_user.id, nusnetRetriever(message.from_user.id), str(curr_date), )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    for i in myresult:
        res.append(i)
    if len(res) == 0:
        await message.reply("No active slots 😕")
    else:
        str1 = "⌛Slots booked on\n\n"
        for i in res:
            str1 += str(i[1]) + " on " + str(i[2])[:-3] + " 👌\n\n"
            #await message.reply("Slot booked on "+ str(i[1]) + "on " + str(i[2]))
        await message.reply(str1)

@dp.message_handler(commands=["unbook"])
async def unBook(message: types.Message, state : FSMContext):
    curr_date = datetime.now().date()
    curr_time = datetime.now().strftime("%H:%M:%S")
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date = %s AND timeslot > %s"
    data = (message.from_user.id, nusnetRetriever(message.from_user.id), str(curr_date), str(curr_time), )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    res = []
    for i in myresult:
        res.append(i)
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date > %s"
    data = (message.from_user.id, nusnetRetriever(message.from_user.id), str(curr_date), )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    for i in myresult:
        res.append(i)
    if len(res) == 0:
        await message.reply("You have no active slots at the moment 😕")
        await state.finish()
    else:
        responses = []
        for i in res:
            responses.append(str(i[1]) + " " + str(i[2]))
        
        buttons = [InlineKeyboardButton(
            text=md.text(button_label),
            callback_data=f"{button_label}"
        ) for button_label in responses]
        keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
        await message.reply("Choose the slot that you wish to unbook", reply_markup=keyboard)
        await state.set_state(Book.picked_unbook_date)

#To be explicity called if user wishes to unbook more slots
async def unBookCycle(message: types.Message, state : FSMContext, id):
    curr_date = datetime.now().date()
    curr_time = datetime.now().strftime("%H:%M:%S")
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date = %s AND timeslot > %s"
    data = (id, nusnetRetriever(id), str(curr_date), str(curr_time), )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    res = []
    for i in myresult:
        res.append(i)
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date > %s"
    data = (id, nusnetRetriever(id), str(curr_date), )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    for i in myresult:
        res.append(i)
    if len(res) == 0:
        await message.reply("You have no active slots at the moment 😕")
        await state.finish()
    else:
        responses = []
        for i in res:
            responses.append(str(i[1]) + " " + str(i[2]))
        
        buttons = [InlineKeyboardButton(
            text=md.text(button_label),
            callback_data=f"{button_label}"
        ) for button_label in responses]
        keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
        await message.reply("Choose the slot that you wish to unbook", reply_markup=keyboard)
        await state.set_state(Book.picked_unbook_date)

@dp.callback_query_handler(state=Book.picked_unbook_date)
async def unBookHandler(call: types.CallbackQuery, state : FSMContext):
    date = str(call.data.split()[0])
    time = str(call.data.split()[1])
    sqlFormula = "UPDATE booking_slots SET is_booked = 0, assoc_teleId = %s, assoc_nusnet = %s WHERE date = %s AND timeslot = %s AND (assoc_teleId = %s OR assoc_nusnet = %s)"
    mycursor.execute(sqlFormula, (None, None, date, time, call.from_user.id, nusnetRetriever(call.from_user.id), ))
    db.commit()
    await call.message.answer("Okay unbooked slot at " + date + " " + time)
    responses = ["Yes", "No"]
    buttons = [InlineKeyboardButton(
        text=md.text(button_label),
        callback_data=f"{button_label}"
            ) for button_label in responses]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    await call.message.answer("Would like you to unbook additional slots?", reply_markup=keyboard)
    await state.set_state(Book.picked_unbook_additional)

@dp.callback_query_handler(state=Book.picked_unbook_additional)
async def unBookMoreHandler(call: types.CallbackQuery, state : FSMContext):
    if call.data == "Yes":
        await unBookCycle(call.message, state, call.from_user.id)
    else:
        await call.message.answer("Okay exiting! Thank you")
        await state.finish()


#Leave this at bottom to catch unknown commands or text input by users
@dp.message_handler(state="*")
async def echo(message: types.Message):
    """
    Message handler for catching unknown commands or text input by users.

    Parameters:
    - message: The Message object representing the user's message.
    """
    await message.reply("Unknown command, use / to check for available commands")

@dp.callback_query_handler(state="*")
async def echo1(call: types.CallbackQuery):
    """
    Callback query handler for catching callbacks from previous inline keyboard buttons.

    Parameters:
    - call: The CallbackQuery object representing the callback query.
    """
    await call.message.answer("You may have clicked on a previous in-line keyboard button")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)