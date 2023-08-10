#Package to store cancel booking functions
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

#Helper function to retrieve nusnet from database using teleId
def nusnetRetriever(id):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    db = create_connection()
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

async def unBook(message: types.Message, state: FSMContext):
    curr_date = datetime.now().date()
    curr_time = datetime.now().strftime("%H:%M:%S")
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date = %s AND timeslot > %s"
    data = (message.from_user.id, nusnetRetriever(
        message.from_user.id), str(curr_date), str(curr_time), )
    db = create_connection()
    mycursor = db.cursor()
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
    db.close()

# To be explicity called if user wishes to unbook more slots
async def unBookCycle(message: types.Message, state: FSMContext, id):
    curr_date = datetime.now().date()
    curr_time = datetime.now().strftime("%H:%M:%S")
    sqlFormula = "SELECT * FROM booking_slots WHERE is_booked = 1 AND (assoc_teleId = %s OR assoc_nusnet = %s) AND date = %s AND timeslot > %s"
    data = (id, nusnetRetriever(id), str(curr_date), str(curr_time), )
    db = create_connection()
    mycursor = db.cursor()
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
    db.close()

async def unBookHandler(call: types.CallbackQuery, state: FSMContext):
    db = create_connection()
    mycursor = db.cursor()
    date = str(call.data.split()[0])
    time = str(call.data.split()[1])
    sqlFormula = "UPDATE booking_slots SET is_booked = 0, assoc_teleId = %s, assoc_nusnet = %s WHERE date = %s AND timeslot = %s AND (assoc_teleId = %s OR assoc_nusnet = %s)"
    mycursor.execute(sqlFormula, (None, None, date, time,
                     call.from_user.id, nusnetRetriever(call.from_user.id), ))
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
    db.close()

async def unBookMoreHandler(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Yes":
        await unBookCycle(call.message, state, call.from_user.id)
    else:
        await call.message.answer("Okay exiting! Thank you")
        await state.finish()