#Package to store profile change functions
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


async def chg_name(message: types.Message, state: FSMContext):
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

async def chg_nameHandler(message: types.Message, state: FSMContext):
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
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    db.commit()
    mycursor.close()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()

async def chg_room(message: types.Message, state: FSMContext):
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

async def chg_roomHandler(message: types.Message, state: FSMContext):
    """
    Handler for changing the user's registered room.

    Usage:
        [User Input] - Provide the new room number in the format XX-XX or XX-XXX.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    s = message.text
    if check_room_format(s):
        sqlFormula = "UPDATE user SET roomNo = %s WHERE teleId = %s"
        data = (s, message.from_id, )
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        mycursor.close()
        db.commit()
        await message.reply("Okay done, use /myinfo to check")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")

async def chg_name1(message: types.Message, state: FSMContext):
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

async def chg_nameHandler1(message: types.Message, state: FSMContext):
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
    mycursor = db.cursor()
    mycursor.execute(sqlFormula, data)
    mycursor.close()
    db.commit()
    await message.reply("Okay done, use /myinfo to check")
    await state.finish()

async def chg_room1(message: types.Message, state: FSMContext):
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

async def chg_roomHandler1(message: types.Message, state: FSMContext):
    """
    Handler for changing the user's spotter's room number.

    Usage:
        [User Input] - Provide the new room number for the spotter.

    Args:
        message (types.Message): The incoming message object.
        state (FSMContext): The state object for managing conversation state.
    """
    s = message.text
    if check_room_format(s):
        sqlFormula = "UPDATE user SET spotterRoomNo = %s WHERE teleId = %s"
        data = (s, message.from_id, )
        mycursor = db.cursor()
        mycursor.execute(sqlFormula, data)
        mycursor.close()
        db.commit()
        await message.reply("Okay done, use /myinfo to check")
        await state.finish()
    else:
        await message.reply("Ensure your string is form XX-XX or XX-XXX depending on type of room e.g 11-12/11-12F")