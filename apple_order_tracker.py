#!/usr/bin/env python
# -*- coding: utf-8 -*-
# By Magomed Gamadaev <ts@strat.zone>

import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import json
import logging
from pathlib import Path

Path("/app/logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("/app/logs/apple_order_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))
TOKEN = os.getenv('TOKEN')
ORDER_STATUS_URL = os.getenv('ORDER_STATUS_URL')

last_known_status = None

STATUS_EMOJIS = {
    "PLACED": "📝",
    "PROCESSING": "⚙️",
    "SHIPPING_TO_STORE": "🚚",
    "READY_FOR_PICKUP": "📦",
    "PICKED_UP": "✅",
    "UNDER_REVIEW": "🔍"
}

keyboard = [[KeyboardButton("Check Order Status")]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def get_order_status():
    try:
        response = requests.get(ORDER_STATUS_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'id': 'init_data'})
        
        if script_tag:
            data = json.loads(script_tag.string)
            status_tracker = data['orderDetail']['orderItems']['orderItem-0000101']['orderItemStatusTracker']['d']
            
            current_status = status_tracker['currentStatus']
            possible_statuses = status_tracker['possibleStatuses']
            
            logger.info(f"Successfully fetched order status: {current_status}")
            return current_status, possible_statuses
        else:
            logger.warning("Could not find status information in the response")
            return None, None
        
    except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error fetching order status: {e}")
        return None, None

def format_status_message(current_status, possible_statuses):
   order_id = ORDER_STATUS_URL.split('/guest/')[1].split('/')[0]
   
   message = f"🎯 Order {order_id}\n"
   message += f"Status: {current_status.replace('_',' ').title()}\n\n"
   message += "Progress:\n"
   
   current_found = False
   for i, status in enumerate(possible_statuses, 1):
       emoji = STATUS_EMOJIS.get(status)
       if status == current_status:
           marker = "▶️"
           current_found = True
       else:
           marker = "✅" if not current_found else "⭕️"
           
       message += f"{marker} {emoji} {status.replace('_',' ').title()}\n"
   
   return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Unauthorized access attempt by user ID: {user_id}")
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return
    logger.info(f"Bot started by authorized user: {user_id}")
    await update.message.reply_text("Welcome! Use the button below to check your order status.", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Unauthorized message from user ID: {user_id}")
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    if update.message.text == "Check Order Status":
        logger.info("Manual status check requested")
        current_status, possible_statuses = await get_order_status()
        
        if current_status and possible_statuses:
            message = format_status_message(current_status, possible_statuses)
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            logger.warning("Unable to fetch order status")
            await update.message.reply_text("Unable to fetch order status at the moment.", reply_markup=reply_markup)

async def periodic_status_check(context: ContextTypes.DEFAULT_TYPE):
    global last_known_status
    logger.info("Performing periodic status check")
    current_status, possible_statuses = await get_order_status()
    
    if current_status and possible_statuses:
        if current_status != last_known_status:
            logger.info(f"Status changed from {last_known_status} to {current_status}")
            if last_known_status is not None:
                message = f"Order status has changed!\n"
                message += f"Previous status: {last_known_status}\n"
                message += f"New status: {current_status}\n\n"
                message += format_status_message(current_status, possible_statuses)
                await context.bot.send_message(chat_id=ALLOWED_USER_ID, text=message, reply_markup=reply_markup)
            last_known_status = current_status
        else:
            logger.info(f"No status change. Current status: {current_status}")
    else:
        logger.warning("Failed to fetch status during periodic check")

def main() -> None:
    logger.info("Starting the bot")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.job_queue.run_repeating(periodic_status_check, interval=1350, first=10)

    logger.info("Bot is running")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()