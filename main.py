from aiogram import Bot, Dispatcher, Router, types,F
from aiogram.types import ContentType, File, Message
from tok import tok
import logging
import sys
import asyncio
from pydub import AudioSegment
import speech_recognition as sr
import json

async def save_voice_as_mp3(bot: Bot, voice: types.Voice) -> str:
    voice_file_info = await bot.get_file(voice.file_id)
    voice_path = f'voice-{voice.file_id}.ogg'
    await bot.download(voice_file_info, voice_path)
    voice_wav_path = f'voice-{voice.file_unique_id}.wav'
    AudioSegment.from_file(voice_path, format="ogg").export(voice_wav_path, format="wav")
    return voice_wav_path

async def recognition(voice):
    recognizer = sr.Recognizer()
    voice_mp3_path = sr.AudioFile(voice)

    with voice_mp3_path as source:
        audio_data = recognizer.record(source)
        text = json.loads(recognizer.recognize_vosk(audio_data, language="ru-RU"))['text']
    print(text)
    return text


router: Router = Router()

@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Принимает все голосовые сообщения и транскрибирует их в текст."""
    voice_path = await save_voice_as_mp3(bot, message.voice)
    text = await recognition(voice_path)
    await bot.send_message(message.from_user.id, text, reply_to_message_id=message.message_id)


async def main():
    bot: Bot = Bot(token=tok)
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())