#Package to store report functions
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

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_photo(file_path, id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': id,
        'parents': [PARENT_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=file_path
    ).execute()

async def report(message: types.Message, state: FSMContext):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await message.reply("You are not registered!")
    else:
        await message.reply("Please state your feedback")
        reportObj = Report(message.from_user.id)
        reports[message.from_user.id] = reportObj
        await state.set_state(Reporting.await_feedback)

async def feedbackHandler(message: types.Message, state: FSMContext):
    reportObj = reports[message.from_user.id]
    reportObj.text = message.text
    sqlFormula = "INSERT INTO reports (report, teleId, nusnet) VALUES (%s, %s, %s)"
    data = (message.text, message.from_user.id,
            nusnetRetriever(message.from_user.id))
    mycursor.execute(sqlFormula, data)
    db.commit()
    responses = ["Yes", "No"]
    buttons = [InlineKeyboardButton(
        text=md.text(button_label),
        callback_data=f"{button_label}"
    ) for button_label in responses]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    await message.reply("Do you wish to submit a photo as well?", reply_markup=keyboard)
    await state.set_state(Reporting.await_photo_response)

async def photoReponseHandler(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Yes":
        await call.message.answer("Okay, please submit your photo")
        await state.set_state(Reporting.await_photo)
    else:
        await call.message.answer("Okay your report has been submitted, thank you!")
        await state.finish()

# Helper function to retrieve reportid for tagging of photos to match the report in db
def reportIdRetriever(id):
    sqlFormula = "SELECT * FROM reports WHERE teleId = %s"
    mycursor.execute(sqlFormula, (id, ))
    myresult = mycursor.fetchall()
    return myresult[-1][-1]

async def photoSubmissionHandler(message: types.Message, state: FSMContext):
    print(message.content_type)
    if message.content_type != 'photo':
        await message.reply("Please submit a photo, if you do not wish to, please /exit, your text feedback will still be submitted!")
    else:
        # Create a unique folder for each user so as to prevent overriding of photo by other users
        user_folder = os.path.join("includes/", str(message.from_user.id))
        os.makedirs(user_folder, exist_ok=True)
        photo = await message.photo[-1].download("includes/" + str(message.from_user.id) + "/" + str(reportIdRetriever(message.from_user.id)) + ".jpg")
        # Left below as commented to track my progress to getting this done, was a pain :p

        # files = glob.glob(os.path.join("includes/" + str(message.from_user.id) + "/photos", '*'))
        # last_file = max(files, key=os.path.getctime)
        # print(last_file)
        # file_path = "includes/" + str(message.from_user.id) + "/photos/file_0.jpg"
        # file_id = message.photo[-1].file_id
        # file = await bot.get_file(file_id)
        # file_path = file.file_path
        # print(file_path)
        # file_path = os.path.join("includes/", photo.file_path)
        try:
            upload_photo("includes/" + str(message.from_user.id) + "/" + str(reportIdRetriever(
                message.from_user.id)) + ".jpg", reportIdRetriever(message.from_user.id))
            await state.finish()
            await message.reply("Okay feedback submitted with photo thank you!")
        except:
            await message.reply("Sorry, error when submitting do submit again or /exit")
        photo.close()
        # Delete the folder so as to free up space
        shutil.rmtree("includes/" + str(message.from_user.id))

async def viewResponses(message: types.Message, state: FSMContext):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (message.from_user.id, )
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        await message.reply("You are not registred!")
    else:
        nusnet = nusnetRetriever(message.from_user.id)
        sqlFormula = "SELECT * FROM reports WHERE nusnet = %s"
        data = (nusnet, )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            await message.reply("You have not submitted any feedback!")
        else:
            res = []
            str1 = "You may click on the report id to check on responses by clubsoc members!\n\n"
            keyboard_responses = []
            for i in myresult:
                str1 += "Report ID: " + str(i[-2]) + "\n\n"
                if i[-1] == 0:
                    # str1 += "Report ID: " + str(i[-2]) + "\n"
                    str1 += i[0] + "\nNot responded to yet 😔\n\n"
                else:
                    # str1 += "Report ID: " + i[-2] + "\n"
                    str1 += i[0] + "\nResponded! 🔥\n\n"
                    keyboard_responses.append(str(i[-2]))
            keyboard_responses.append("Exit")
            buttons = [InlineKeyboardButton(
                text=md.text(button_label),
                callback_data=f"{button_label}"
            ) for button_label in keyboard_responses]
            keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
            await message.reply(str1, reply_markup=keyboard)
            await state.set_state(viewReport.clicked_id)

async def viewResponseHandler(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Exit":
        await state.finish()
        await call.message.answer("Okay exited!")
    else:
        sqlFormula = "SELECT * FROM reports_response WHERE reportId = %s"
        data = (int(call.data), )
        mycursor.execute(sqlFormula, data)
        myresult = mycursor.fetchall()
        str1 = "Responses to report ID: " + call.data + "\n\n"
        for i in myresult:
            str1 += i[-1] + "\n\n"
        await call.message.answer(str1)
        await state.finish()