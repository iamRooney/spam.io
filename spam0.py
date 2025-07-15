import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

# === CONFIG ===
api_id = 1234567  # <-- Replace with YOUR API ID
api_hash = 'YOUR_API_HASH'
session_name = 'spam_cleaner'

# Keywords to detect spam groups
spam_keywords = [
    'free', 'crypto', 'porn', 'xxx', 'betting', 'casino',
    'earn money', 'click here', 'adult', 'bitcoin', 'nude'
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
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def is_spam(group, safe_list):
    name = (group.name or '').lower()
    about = (group.about or '').lower()
    if name in safe_list:
        return False
    combined = f"{name} {about}"
    return any(keyword in combined for keyword in spam_keywords)

async def leave_group(group):
    print(f"🚩 Leaving: {group.name}")
    await client.delete_dialog(group.id)
    log_action(f"Left group: {group.name} (ID: {group.id})")

async def main():
    await client.start()

    safe_list = load_safe_list()
    dialogs = await client.get_dialogs()
    groups = [d for d in dialogs if d.is_group]

    print(f"\n🔍 Found {len(groups)} groups total.\n")

    spam_groups = []
    for group in groups:
        entity = await client.get_entity(group.id)

        # Try to get full channel for about text
        about = ''
        if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
            try:
                full = await client(GetFullChannelRequest(entity))
                about = full.full_chat.about or ''
            except Exception as e:
                print(f"⚠️  Could not get about for {group.name}: {e}")

        group.entity = entity
        group.about = about

        print("━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📌 Group: {group.name}")
        print(f"About: {about if about else '[no about]'}")
        
        if is_spam(group, safe_list):
            print(f"🚩 MATCHED: Marked as spam")
            spam_groups.append(group)
        else:
            print(f"✅ SAFE: Not spam")

    if not spam_groups:
        print("\n✅ No spam groups detected.")
        log_action("No spam groups detected.")
        return

    print(f"\n🚩 Detected {len(spam_groups)} spam groups.\n")
    log_action(f"Detected {len(spam_groups)} spam groups.")

    for i in range(0, len(spam_groups), BATCH_SIZE):
        batch = spam_groups[i:i + BATCH_SIZE]
        tasks = [asyncio.create_task(leave_group(g)) for g in batch]
        await asyncio.gather(*tasks)

        if i + BATCH_SIZE < len(spam_groups):
            print(f"⏳ Waiting {BATCH_DELAY} seconds before next batch...")
            await asyncio.sleep(BATCH_DELAY)

    print("\n✅ All spam groups left.")
    log_action("Left all spam groups.")

with client:
    client.loop.run_until_complete(main())
