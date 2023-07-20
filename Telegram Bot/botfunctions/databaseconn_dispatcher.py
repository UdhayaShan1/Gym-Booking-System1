#Package to establish connection to mySQL and set up bot dispatcher
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

pwd = None
with open("includes\database_pwd.txt") as f:
    pwd = f.read().strip()
db = mysql.connector.connect(
    host="localhost",
    user='root',
    passwd=pwd,
    database="testdatabase"
)

# Set up dispatcher
TOKEN = None
with open("includes\dot_token.txt") as f:
    TOKEN = f.read().strip()

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)