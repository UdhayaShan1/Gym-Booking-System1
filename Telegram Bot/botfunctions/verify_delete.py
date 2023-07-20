#Package to store verify and delete functions
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


logging.basicConfig(level=logging.INFO)

# Set up dispatcher
TOKEN = None
with open("includes\dot_token.txt") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


########################################### <<<MAIN CODE>>>###########################################

############## <<<USER CREATION>>>##############

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


async def verify(message: types.Message, state: FSMContext):
    print(message.from_user.id)
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor = db.cursor()
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
    mycursor.close()

async def otp_handler(message: types.Message, state: FSMContext):
    # print(users)
    mycursor = db.cursor()
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
    mycursor.close()

async def deleteMyDetails(message: types.Message, state: FSMContext):
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
    mycursor = db.cursor()
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    if myresult == None:
        await message.reply("You are not registered in the system.")
    else:
        # Attempt at InLineKeyboard instead
        button3 = InlineKeyboardButton(text="Yes!", callback_data="Yes!")
        button4 = InlineKeyboardButton(text="No!", callback_data="No!")
        keyboard2 = InlineKeyboardMarkup().add(button3).add(button4)
        await message.reply("Are you sure you want to delete your details, this is not undoable\nWe will delete your records from our mySQL database and any attached bookings", reply_markup=keyboard2)
        await state.set_state(Form.delete_details)
    mycursor.close()

#Helper function to retrieve nusnet from database using teleId
def nusnetRetriever(id):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    return myresult[-2]


async def deleteHandler2(call: types.CallbackQuery, state: FSMContext):
    """
    Callback handler for confirming the deletion of user details.

    Usage:
        [CallbackData] - "Yes!" or "No!"

    Args:
        call (types.CallbackQuery): The incoming callback query object.
        state (FSMContext): The state object for managing conversation state.
    """
    mycursor = db.cursor()
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
    # Add code to ammend all associated bookings to have teleId and spotterId to None.
    mycursor.close()
    await state.finish()