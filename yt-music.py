from pyrogram import Client, filters
import yt_dlp
from urllib.parse import urlparse
import os
import shutil


app = Client(
    "yt_to_musci_bot",
    api_id=23951485,
    api_hash="1b0ed878b1df1665f7f370453cd44125",
    bot_token="6363321961:AAElDYS4hDWu1WHrxIcKCD8XOSJb6Sw_6QM"
)

overview_message = (
    "🎵 Welcome to YT to Music Bot! 🎵\n\n"
    "I'm here to help you convert YouTube videos and playlists to MP3 format. Just send me a YouTube link "
    "or playlist, and I'll convert it for you in a snap! 😊\n\n"
    "Here are the available commands:\n"
    "/start - Get a brief introduction to the bot.\n"
    "/help or /info - Get more detailed information on how to use the bot.\n"
    "/admin - Reach out to the bot creator with your doubts or questions.\n\n"
    "Let's get grooving! 🎶"
)

help_message = (
    "To use the YT to Music Bot, simply follow these steps:\n\n"
    "1. Send me a YouTube link or playlist you want to convert to Music.\n"
    "2. I will process the link and convert it for you.\n"
    "3. Once the conversion is complete, I'll send you the Music file.\n\n"
    "That's it! Enjoy the music! 🎶\n\n"
    "Note: Please make sure the YouTube link or playlist is valid and public."
)

admin_username = "bingewatcher"
contact_admin = (
    f"If you have any doubts or questions, feel free to contact the bot administrator @{admin_username}!"
)


def download_hook(d: dict, msg):
    if d["status"] == "downloading":
        downloaded_bytes = d["downloaded_bytes"]
        total_bytes = d["total_bytes"]
        title = d["info_dict"]["title"]

        # Calculate progress for the segmented progress bar
        progress = int(100 * downloaded_bytes / total_bytes)
        segments = int(progress / 10)
        progress_bar = "■" * segments + "▒" * (10 - segments)
        try:
            msg.edit_text(
                f"Title: {title}\n\n{progress_bar}\n\nDownloading: {progress}%")
        except:
            pass


def upload_hook(sent_messages, total_messages, msg):
    # Calculate progress for the segmented progress bar
    progress = int(100 * sent_messages / total_messages)
    segments = int(progress / 10)
    progress_bar = "■" * segments + "▒" * (10-segments)
    try:
        msg.edit_text(f"Uploading:  {progress}% {progress_bar}")
    except:
        pass


@app.on_message(filters.command('start'))
def start(app, message):
    app.send_message(
        message.chat.id, overview_message)


@app.on_message(filters.command(['help', 'info']))
def help(app, message):
    app.send_message(
        message.chat.id, help_message)


@app.on_message(filters.command("admin"))
def contact(app, message):
    app.send_message(
        message.chat.id, contact_admin
    )


@app.on_message(filters.text)
def convertion(app, message):
    url = message.text
    if "list" in url:
        folder_name = f"{message.chat.id}"
        msg = message.reply_text("Downloading...")
        ydl_opts = {
            "progress_hooks": [lambda d: download_hook(d, msg)],
            "format": "bestaudio/best",
            'outtmpl': os.path.join(folder_name, '%(title)s.%(ext)s'),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": "192",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        msg.edit_text("Uploading...")
        send_messages = 0
        total_messages = len(os.listdir(folder_name))
        for filename in os.listdir(folder_name):
            audio_file = os.path.join(folder_name, filename)
            message.reply_audio(audio_file)
            send_messages += 1
            upload_hook(send_messages, total_messages, msg)
        shutil.rmtree(folder_name)
        msg.delete()

    else:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if "youtu.be" in domain or "youtube.com" in domain or "www.youtube.comm" in domain:
            msg = message.reply_text("Downloading...")
            ydl_opts = {
                "progress_hooks": [lambda d: download_hook(d, msg)],
                "format": "bestaudio/best",
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "m4a",
                        "preferredquality": "192",

                    }
                ],
            }
            done = "false"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_file = ydl.prepare_filename(info_dict)
                audio_file = video_file.replace("webm", "m4a")
                print(audio_file)
                ydl.download([url])
                msg.edit_text("Uploading...")
                message.reply_audio(audio_file)
                msg.delete()
        else:
            app.send_message(message.chat.id, "Not a valid yt link😕")


app.run()
