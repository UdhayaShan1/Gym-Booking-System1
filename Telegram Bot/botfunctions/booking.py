#Package to store booking functions
import mysql.connector
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
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
import glob
import shutil
from botfunctions.helper_functions import validnusNet, check_room_format, dateValidator, timeValidator, generate_otp, send_otp

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'includes/service_account.json'
PARENT_FOLDER_ID = "1wb4h1vSTqsXxYB3-ah_r4cREMQc1ySPR"

# Database connection, we will use mySQL and localhost for now

from botfunctions.databaseconn_dispatcher import db, dp
mycursor = db.cursor()


logging.basicConfig(level=logging.INFO)

#Helper function to retrieve nusnet from database using teleId
def nusnetRetriever(id):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    return myresult[-2]


########################################### <<<MAIN CODE>>>###########################################


# State machines for booking process to create user profile
class Form(StatesGroup):
    set_nusnet = State()
    set_name = State()
    # set_phone = State()
    set_room = State()
    set_spotter_name = State()
    set_spotter_room = State()
    change_name = State()
    change_room = State()
    change_spotter_name = State()
    change_spotter_room = State()
    otp_verify = State()
    delete_details = State()

# State machines for booking process to create a sequential process (in progress)


class Book(StatesGroup):
    picked_date = State()
    picked_time = State()
    additional_time = State()
    repicked_date = State()
    picked_unbook_date = State()
    picked_unbook_additional = State()

# State machines for reporting


class Reporting(StatesGroup):
    await_feedback = State()
    await_photo_response = State()
    await_photo = State()

# State machines for viewing response to reports


class viewReport(StatesGroup):
    clicked_id = State()


# Dictionary for user creation Useful for profile creation.
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


# Dictionary for booking creation. No proper use yet... probably will be deprecated.
bookings = {}


class Booking:
    def __init__(self, teleId):
        self.teleId = teleId
        self.date = None
        self.time = None


reports = {}


class Report:
    def __init__(self, teleId) -> None:
        self.teleId = teleId
        self.text = None
        self.photo = None


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
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult != None and myresult[-1] == 0:
        await message.reply("You are not verified yet, proceed to /verify")
    elif myresult == None:
        await message.reply("You are not registered, use /start to begin profile creation")
    else:
        # Create local booking object
        booking_obj = Booking(message.from_user.id)
        bookings[message.from_user.id] = booking_obj
        # Fetch current time, current date and date in 2 weeks for SQL query, not sure if need adjust GMT looks like based on IDE
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.date()
        current_date_14_forward = (now.date()+timedelta(days=14))
        dates = [current_date + timedelta(days=i) for i in range(14)]
        await message.reply("Sure, let's display available dates\n" + "Current date is " + str(current_date) + "\nTime is " + str(current_time))

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
    mycursor.close()

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
    # Check if user is in the system in the first place
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered, use /start to begin profile creation")
    else:
        # Fetch current time, current date and date in 2 weeks for SQL query, not sure if need adjust GMT looks like based on IDE
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.date()
        current_date_14_forward = (now.date()+timedelta(days=14))
        dates = [current_date + timedelta(days=i) for i in range(14)]
        await message.reply("Sure, let's display available dates\n" + "Current date is " + str(current_date) + "\nTime is " + str(current_time))

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
    mycursor.close()


async def bookStageViewSlots(call: types.CallbackQuery, state: FSMContext):
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
    # await call.message.answer(call.data)
    mycursor = db.cursor()
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
            button1 = InlineKeyboardButton(
                text="Pick another date", callback_data="Pick another date")
            calendar_keyboard = InlineKeyboardMarkup(
                row_width=2).add(*buttons).add(button1)
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
                button1 = InlineKeyboardButton(
                    text="Pick another date", callback_data="Pick another date")
                calendar_keyboard = InlineKeyboardMarkup(
                    row_width=2).add(*buttons).add(button1)
                await call.message.answer(str1, reply_markup=calendar_keyboard)
                await state.set_state(Book.picked_time)
    mycursor.close()
# This function must be explicitly called if and only if user asks to book agn for same day


async def bookStageViewSlotsCycle(message: types.Message, state: FSMContext, id):
    # await message.reply(message.text)
    # print((bookings.keys()))
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

            button1 = InlineKeyboardButton(
                text="Pick another date", callback_data="Pick another date")
            calendar_keyboard = InlineKeyboardMarkup(
                row_width=2).add(*buttons).add(button1)
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

                button1 = InlineKeyboardButton(
                    text="Pick another date", callback_data="Pick another date")
                calendar_keyboard = InlineKeyboardMarkup(
                    row_width=2).add(*buttons).add(button1)
                await message.reply(str1, reply_markup=calendar_keyboard)
                await state.set_state(Book.picked_time)

async def bookStageSelectedTime(call: types.CallbackQuery, state: FSMContext):
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
            data = (call.from_user.id, nusnetRetriever(
                call.from_user.id), str(call.data)[5:], booking_obj.date, )
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

async def responseHandlerforAdditionalSlots(call: types.CallbackQuery, state: FSMContext):
    """
    Allow user to repick more time slots by activating the bookStageViewSlotsCycle function which is essentially
    a non-CallbackQuery version of bookStageViewSlots.
    """
    if call.data == "Yes":
        # await call.message.answer("Debug")
        # await state.set_state(Book.repicked_date)
        # Have to explicity call function as it is neither from query or user message
        await bookStageViewSlotsCycle(call.message, state, call.from_user.id)
    else:
        await call.message.answer("Thank you! Slots booked, use /checkactive to check your bookings! 😃")
        await state.finish()

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
    sqlFormula = "SELECT * FROM user where teleId = %s"
    mycursor.execute(sqlFormula, (message.from_user.id, ))
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await message.reply("You are not registered yet, please use /start")
    else:
        curr_date = datetime.now().date()
        curr_time = datetime.now().strftime("%H:%M:%S")
        sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date = %s AND timeslot > %s"
        data = (message.from_user.id, nusnetRetriever(
            message.from_user.id), str(curr_date), str(curr_time), )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        res = []
        for i in myresult:
            res.append(i)
        sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date > %s"
        data = (message.from_user.id, nusnetRetriever(
            message.from_user.id), str(curr_date), )
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
                # await message.reply("Slot booked on "+ str(i[1]) + "on " + str(i[2]))
            await message.reply(str1)