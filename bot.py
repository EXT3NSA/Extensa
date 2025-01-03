import asyncio
import base64
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Group chat ID and Bot Token
GROUP_CHAT_ID = -4714707874
BOT_TOKEN = "7987733957:AAG7_AjbJd5dWXg_rVF95hFOziK1RhX-NJk"

# API Keys
SPOTIFY_CLIENT_ID = "97930216f7684879b1b432047c3d754d"
SPOTIFY_CLIENT_SECRET = "80fd5171818f4611b0a59d5d9cc461f1"
NEWS_API = "https://newsapi.org/v2/top-headlines?country=us&apiKey=bad2e49f6240492b93122147306c1434"

# Spotify: Get Access Token
def get_spotify_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

# Spotify: Fetch Top Tracks
def get_top_tracks():
    access_token = get_spotify_access_token()
    if not access_token:
        return "❌ Unable to fetch Spotify data."

    url = "https://api.spotify.com/v1/playlists/37i9dQZEVXbMDoHDwVN2tF/tracks"  # Spotify Top 50 Playlist
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tracks = response.json().get('items', [])
        return "\n".join([f"{idx + 1}. {track['track']['name']} by {track['track']['artists'][0]['name']}" for idx, track in enumerate(tracks[:10])])
    else:
        return "❌ Failed to retrieve top tracks."

# NewsAPI: Fetch Latest News
def get_latest_news():
    try:
        response = requests.get(NEWS_API)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            return "\n".join([f"• [{article['title']}]({article['url']})" for article in articles[:5]])
        else:
            return "❌ Unable to fetch news data."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎵 Top Music", callback_data='music')],
        [InlineKeyboardButton("📰 Latest News", callback_data='news')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to *EXTENSA* 🤖! Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'music':
        music_message = get_top_tracks()
        await query.edit_message_text(f"🎵 *Top Tracks* 🎵\n{music_message}", parse_mode="Markdown")
    elif query.data == 'news':
        news_message = get_latest_news()
        await query.edit_message_text(f"📰 *Latest News* 📰\n{news_message}", parse_mode="Markdown")

async def send_online_message(app):
    while True:
        message = "✨ *EXTENSA* is *ONLINE* ✨\n🚀 Always here to assist you with style and functionality! 🌟"
        await app.bot.send_message(chat_id=GROUP_CHAT_ID, text=message, parse_mode="Markdown")
        await asyncio.sleep(3600)  # 1 hour

if __name__ == '__main__':
    # Initialize bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    # Function to run the bot and the periodic task
    async def main():
        # Create a task to send the periodic online message
        asyncio.create_task(send_online_message(app))
        # Run the bot
        await app.run_polling()

    # Run the main coroutine
    asyncio.run(main())