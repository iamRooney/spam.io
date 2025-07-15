import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

# === CONFIG ===
api_id =   # <-- Replace with YOUR API ID
api_hash = ''
session_name = 'spam_cleaner'

spam_keywords = [
    'free', 'crypto', 'porn', 'xxx', 'betting', 'casino',
    'earn money', 'click here', 'adult', 'bitcoin', 'nude',
    'forex', 'trading', 'signals', 'profit', 'account handling',
    'broker', 'broking', 'investment', 'stock tips',
    'expert tips', 'big profit', 'intraday', 'nifty', 'calls', 'online money'
]


SAFE_LIST_FILE = 'safe_list.txt'
LOG_FILE = 'spam_cleaner.log'

BATCH_SIZE = 5
BATCH_DELAY = 2

client = TelegramClient(session_name, api_id, api_hash)

def load_safe_list():
    try:
        with open(SAFE_LIST_FILE, 'r') as f:
            lines = f.read().splitlines()
            return [line.strip().lower() for line in lines if line.strip()]
    except FileNotFoundError:
        return []

def log_action(message):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")


def is_spam(channel, safe_list):
    name = (channel.name or '').lower()
    about = (channel.about or '').lower()
    if name in safe_list:
        return False
    combined = f"{name} {about}"
    return any(keyword in combined for keyword in spam_keywords)

async def leave_channel(channel):
    print(f"🚩 Leaving: {channel.name}")
    await client.delete_dialog(channel.id)
    log_action(f"Left channel: {channel.name} (ID: {channel.id})")

async def main():
    await client.start()

    safe_list = load_safe_list()
    dialogs = await client.get_dialogs()

    # === ONLY CHANNELS (not groups) ===
    channels = [d for d in dialogs if d.is_channel and not d.is_group]

    print(f"\n🔍 Found {len(channels)} channels total.\n")

    spam_channels = []
    for channel in channels:
        entity = await client.get_entity(channel.id)

        about = ''
        if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
            try:
                full = await client(GetFullChannelRequest(entity))
                about = full.full_chat.about or ''
            except Exception as e:
                print(f"⚠️  Could not get about for {channel.name}: {e}")

        channel.entity = entity
        channel.about = about

        print("━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📌 Channel: {channel.name}")
        print(f"About: {about if about else '[no about]'}")

        if is_spam(channel, safe_list):
            print(f"🚩 MATCHED: Marked as spam")
            spam_channels.append(channel)
        else:
            print(f"✅ SAFE: Not spam")

    if not spam_channels:
        print("\n✅ No spam channels detected.")
        log_action("No spam channels detected.")
        return

    print(f"\n🚩 Detected {len(spam_channels)} spam channels.\n")
    log_action(f"Detected {len(spam_channels)} spam channels.")

    for i in range(0, len(spam_channels), BATCH_SIZE):
        batch = spam_channels[i:i + BATCH_SIZE]
        tasks = [asyncio.create_task(leave_channel(c)) for c in batch]
        await asyncio.gather(*tasks)

        if i + BATCH_SIZE < len(spam_channels):
            print(f"⏳ Waiting {BATCH_DELAY} seconds before next batch...")
            await asyncio.sleep(BATCH_DELAY)

    print("\n✅ All spam channels left.")
    log_action("Left all spam channels.")

with client:
    client.loop.run_until_complete(main())
