#Package with profile creation functions
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

from botfunctions.databaseconn_dispatcher import create_connection, dp


logging.basicConfig(level=logging.INFO)



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


async def start(message: types.Message, state: FSMContext):
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
    await message.reply("Thank you for using our gym booking bot, powered by Aiogram, Python and MySQL.\nVersion: 0.3.6 Track progress and read patch notes on GitHub!\nCreated by Rolex\nContact @frostbitepillars and @ for any queries")
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

async def set_nusnet(message: types.Message, state: FSMContext):
    users[message.from_user.id] = User(message.from_user.id)
    user = users[message.from_user.id]
    # user = users[message.from_user.id]
    nusnet = str(message.text).lower()
    db = create_connection()
    mycursor = db.cursor()
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

        sqlFormula = "SELECT * FROM user WHERE nusnet = %s AND teleId IS NULL"
        data = (nusnet, )
        mycursor.execute(sqlFormula, data)
        myresult2 = mycursor.fetchone()
        if myresult == None:
            user.nusnet = nusnet
            await message.reply("You have not been registered yet! Begin by typing your name")
            await state.set_state(Form.set_name)
        elif myresult1 == None:
            user.nusnet = nusnet
            await message.reply("Your profile creation has not been completed! Begin by typing your name")
            await state.set_state(Form.set_name)
        elif myresult2 != None:
            await message.reply("Appears you probably have registered on the website! We will tag your Telegram handle to that profile!")
            sqlFormula = "UPDATE user SET teleId = %s WHERE nusnet = %s"
            data = (message.from_user.id, nusnet, )
            mycursor.execute(sqlFormula, data)
            db.commit()
            await state.finish()
        else:
            await message.reply("You have already been registered! Use /myinfo to check again")
            await state.finish()
    mycursor.close()

async def set_name(message: types.Message, state: FSMContext):
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

async def set_room(message: types.Message, state: FSMContext):
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
    if check_room_format(s):
        user.room = s
        await message.reply("Okay, what is your spotter's name?")
        await state.set_state(Form.set_spotter_name)
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

async def set_spotter_name(message: types.Message, state: FSMContext):
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

async def set_spotter_room(message: types.Message, state: FSMContext):
    db = create_connection()
    mycursor = db.cursor()
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
    if check_room_format(s):
        user.spotter_room = s
        sqlFormula = "SELECT * FROM user WHERE nusnet = %s"
        data = (user.nusnet, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchone()
        if myresult == None:
            # Insert into SQL database
            sqlFormula = "INSERT INTO user (teleId, roomNo, name, spotterName, spotterRoomNo, nusnet) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (message.from_user.id, user.room, user.name,
                    user.spotter_name, user.spotter_room, user.nusnet)
            mycursor.execute(sqlFormula, data)
            db.commit()
        else:
            sqlFormula = "UPDATE user SET teleId = %s, roomNo = %s, name = %s, spotterName = %s, spotterRoomNo = %s WHERE nusnet = %s"
            data = (message.from_user.id, user.room, user.name,
                    user.spotter_name, user.spotter_room, user.nusnet, )
            mycursor.execute(sqlFormula, data)
            db.commit()
        await message.reply("Okay info set, check via /myinfo")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")
    mycursor.close()

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
    db = create_connection()
    mycursor = db.cursor()
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
        await message.reply("Your NUSNET is " + myresult[-2] + "\n\nYour name is " + myresult[3] + "\n\nYour room number is " + myresult[2] + "\n\nYour spotter is " + myresult[-4] + "\n\nYour spotter room number is " + myresult[-3] + verifiedStr)
    mycursor.close()