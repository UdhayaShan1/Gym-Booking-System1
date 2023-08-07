# Rolex Beta 0.3.6

# Modules to be imported
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

#Import database and dispatcher from package
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

# Force exit out of any state


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

#Helper function to retrieve nusnet from database using teleId
def nusnetRetriever(id):
    sqlFormula = "SELECT * FROM user WHERE teleId = %s"
    data = (id, )
    mycursor = create_connection().cursor()
    mycursor.execute(sqlFormula, data)
    myresult = mycursor.fetchone()
    mycursor.close()
    return myresult[-2]



#Profile Creation
from botfunctions.start_profile import start, set_nusnet, set_name, set_room, set_spotter_name, set_spotter_room, myinfo
dp.register_message_handler(start, commands=['start'])

dp.register_message_handler(set_nusnet, state=Form.set_nusnet)

dp.register_message_handler(set_name, state=Form.set_name)

dp.register_message_handler(set_room, state=Form.set_room)

dp.register_message_handler(set_spotter_name, state=Form.set_spotter_name)

dp.register_message_handler(set_spotter_room, state=Form.set_spotter_room)

dp.register_message_handler(myinfo, commands=['myinfo'])

#Change profile
from botfunctions.change_profile import (
    chg_name,
    chg_nameHandler,
    chg_room,
    chg_roomHandler,
    chg_name1,
    chg_nameHandler1,
    chg_room1,
    chg_roomHandler1,
)

dp.register_message_handler(chg_name, commands=['namechg'])
dp.register_message_handler(chg_nameHandler, state=Form.change_name)

dp.register_message_handler(chg_room, commands=['roomchg'])
dp.register_message_handler(chg_roomHandler, state=Form.change_room)

dp.register_message_handler(chg_name1, commands=['spotternamechg'])
dp.register_message_handler(chg_nameHandler1, state=Form.change_spotter_name)

dp.register_message_handler(chg_room1, commands=['spotterroomchg'])
dp.register_message_handler(chg_roomHandler1, state=Form.change_spotter_room)

from botfunctions.verify_delete import verify, otp_handler, deleteMyDetails, deleteHandler2
dp.register_message_handler(verify, commands=['verify'])

dp.register_message_handler(otp_handler, state=Form.otp_verify)

dp.register_message_handler(deleteMyDetails, state='*', commands=['delete'])

dp.register_callback_query_handler(deleteHandler2, state=Form.delete_details)



#Booking

from botfunctions.booking import (
    book,
    bookCycle,
    bookStageViewSlots,
    bookStageViewSlotsCycle,
    bookStageSelectedTime,
    responseHandlerforAdditionalSlots,
    checkMyGymSlots
)

dp.register_message_handler(book, commands=['book'])

dp.register_callback_query_handler(bookStageViewSlots, state=Book.picked_date)

dp.register_callback_query_handler(bookStageSelectedTime, state=Book.picked_time)

dp.register_callback_query_handler(responseHandlerforAdditionalSlots, state=Book.additional_time)

dp.register_message_handler(checkMyGymSlots, state='*', commands=['checkactive'])


#Cancel booking
from botfunctions.unbook import (
    unBook,
    unBookCycle,
    unBookHandler,
    unBookMoreHandler
)

dp.register_message_handler(unBook, commands=['unbook'])

dp.register_callback_query_handler(unBookHandler, state=Book.picked_unbook_date)

dp.register_callback_query_handler(unBookMoreHandler, state=Book.picked_unbook_additional)


from botfunctions.report import (
    authenticate,
    upload_photo,
    report,
    feedbackHandler,
    photoReponseHandler,
    reportIdRetriever,
    photoSubmissionHandler,
    viewResponses,
    viewResponseHandler
)

dp.register_message_handler(report, commands=["report"])

dp.register_message_handler(feedbackHandler, state=Reporting.await_feedback)

dp.register_callback_query_handler(photoReponseHandler, state=Reporting.await_photo_response)

dp.register_message_handler(photoSubmissionHandler, state=Reporting.await_photo, content_types=["any"])

dp.register_message_handler(viewResponses, commands=["viewresponse"])

dp.register_callback_query_handler(viewResponseHandler, state=viewReport.clicked_id)


@dp.message_handler(commands=["equipment"])
async def equipmentCheck(message: types.Message, state: FSMContext):
    sqlFormulaWeights = "SELECT * FROM equipment WHERE weight IS NOT NULL"
    connection = create_connection().create_connection();
    mycursor = connection.cursor()
    mycursor.execute(sqlFormulaWeights)
    myresult = mycursor.fetchall()
    dict_weight = {}
    for i in myresult:
        if i[1] not in dict_weight:
            dict_weight[i[1]] = {}
        else:
            if i[2] == 1:
                if i[3] not in dict_weight[i[1]]:
                    dict_weight[i[1]][i[3]] = 1
                else:
                    dict_weight[i[1]][i[3]] += 1
    # print(dict_weight)
    str1 = "<b><u>Functioning Weights</u></b>\n\n"
    for i in dict_weight:
        if len(dict_weight[i]) != 0:
            str1 += "<b>" + i + "</b>" + "\n\n"
            for j in dict_weight[i]:
                str1 += str(j) + "kg" + " Count:" + str(dict_weight[i][j]) + "\n\n"
    

    sqlFormulaWeights = "SELECT * FROM equipment WHERE weight IS NULL"
    mycursor.execute(sqlFormulaWeights)
    myresult = mycursor.fetchall()
    dict_nonweight = {}
    str1 += "<b><u>Other Equipment</u></b>\n\n"
    for i in myresult:
        str1 += "<b>" + i[1] + "</b>" + "\n\n"
        if i[2] == 1:
            str1 += "Working Condition\n\n"
        else:
            str1 += "Not usable 😔\n" + "Comments: " + i[4] + "\n\n"
    connection.close()
    await message.reply(str1, parse_mode="HTML") 

# Leave this at bottom to catch unknown commands or text input by users
@dp.message_handler(state="*")
async def echo(message: types.Message, state: FSMContext):
    """
    Message handler for catching unknown commands or text input by users.

    Parameters:
    - message: The Message object representing the user's message.
    """
    current_state = await state.get_state()
    print(f"Current state: {current_state}")
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
