"""
🎮 FIRST CREATION BOT - COMPLETE FIXED VERSION
Using Reply Keyboard for proper Web App data handling
"""

import requests
import time
import json
import random
import datetime
import os
from collections import defaultdict

# ============================================
# CONFIGURATION
# ============================================
TOKEN = "8663428877:AAFjYaQs7TyRajIGhR3kA8wdsqSVwcdlybw"
SAVE_FILE = "bot_complete_data.json"

# ============================================
# YOUR FILE IDs
# ============================================
FILE_IDS = {
    'welcome': 'AgACAgQAAxkBAAORabi0Qmyl4X1zOK6xvrbGf8T7mUEAAoANaxvmFsFRN6a6j6J-6ycBAAMCAAN5AAM6BA',
    'mine': 'AgACAgQAAxkBAAOTabi0T1v-V-k0daQb3V3dUd9haOQAAn4NaxvmFsFRjbZqZUEJx6cBAAMCAAN5AAM6BA',
    'critical': 'AgACAgQAAxkBAAOVabi0cCrMIabBcTgytLvln0WDyu0AAoINaxvmFsFR8aMlDVDO1FYBAAMCAAN5AAM6BA',
    'levelup': 'AgACAgQAAxkBAAOXabi0f7I20O02OmmbPe3Pqo1lRAsAAoENaxvmFsFRA2wF8eL7znoBAAMCAAN5AAM6BA',
    'daily': 'AgACAgQAAxkBAAOZabi0mKqsQ6EImVrR4xd3Afk2HNQAAoMNaxvmFsFRAAFtMu76PeoeAQADAgADeQADOgQ',
    'leaderboard': 'AgACAgQAAxkBAAObabi0nwyyXN8Q9spW-n_BD-Ta9bUAAoQNaxvmFsFRrjNN2yHnlDgBAAMCAAN5AAM6BA'
}

# ============================================
# LOAD SAVED DATA
# ============================================
user_points = {}
daily_claimed = {}
user_wallets = {}
user_referrals = defaultdict(list)

if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, 'r') as f:
            saved_data = json.load(f)
            # Convert string keys back to integers
            user_points = {int(k): v for k, v in saved_data.get('points', {}).items()}
            daily_claimed = saved_data.get('daily', {})
            user_wallets = {int(k): v for k, v in saved_data.get('wallets', {}).items()}
            user_referrals = defaultdict(list, {int(k): v for k, v in saved_data.get('referrals', {}).items()})
            print(f"✅ Loaded {len(user_points)} players!")
            print(f"✅ {len(user_wallets)} wallets connected")
    except Exception as e:
        print(f"⚠️ Error loading save file: {e}")
        print("⚠️ Starting fresh save file")

def save_data():
    try:
        data = {
            'points': user_points,
            'daily': daily_claimed,
            'wallets': user_wallets,
            'referrals': dict(user_referrals),
            'last_save': str(datetime.datetime.now())
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

# ============================================
# TELEGRAM FUNCTIONS
# ============================================

def send_photo(chat_id, file_id, caption="", buttons=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    data = {
        'chat_id': chat_id,
        'photo': file_id,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    
    if buttons:
        data['reply_markup'] = json.dumps({
            'inline_keyboard': buttons,
            'resize_keyboard': True
        })
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"Photo send failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending photo: {e}")
        return False

def send_message(chat_id, text, buttons=None, reply_keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    if buttons:
        data['reply_markup'] = json.dumps({
            'inline_keyboard': buttons,
            'resize_keyboard': True
        })
    elif reply_keyboard:
        data['reply_markup'] = json.dumps(reply_keyboard)
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"Message send failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

# ============================================
# GAME LOGIC
# ============================================

def get_user_level(points):
    if points < 100:
        return 1, "🥉 Novice"
    elif points < 500:
        return 2, "🥈 Apprentice"
    elif points < 1000:
        return 3, "🥇 Journeyman"
    elif points < 5000:
        return 4, "💎 Expert"
    elif points < 10000:
        return 5, "👑 Master"
    else:
        return 6, "⚡ Legendary"

def get_mining_power(level):
    return level

def format_number(num):
    return f"{num:,}"

def validate_wallet(address):
    address = address.strip()
    if address.startswith('0x') and len(address) == 42:
        return 'evm', address.lower()
    elif address.startswith(('EQ', 'UQ')) and len(address) == 48:
        return 'ton', address
    else:
        return None, None

# ============================================
# MAIN BOT LOOP
# ============================================

def main():
    last_update = 0
    last_save = time.time()
    
    print("=" * 60)
    print("🎮 FIRST CREATION BOT - REPLY KEYBOARD EDITION")
    print("=" * 60)
    print(f"✅ Bot: @firstcreationbot")
    print(f"✅ Loaded {len(user_points)} players")
    print(f"✅ {len(user_wallets)} wallets connected")
    print(f"✅ Miner Dino Game: ACTIVE (Reply Keyboard)")
    print("=" * 60)
    
    while True:
        try:
            if time.time() - last_save > 60:
                save_data()
                last_save = time.time()
                print(f"💾 Auto-saved {len(user_points)} players")
            
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            params = {'offset': last_update + 1, 'timeout': 30}
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get('ok'):
                for update in data.get('result', []):
                    last_update = update['update_id']
                    
                    # ======== HANDLE MESSAGES ========
                    if 'message' in update:
                        chat_id = update['message']['chat']['id']
                        user_id = update['message']['from']['id']
                        text = update['message'].get('text', '')
                        first_name = update['message']['from'].get('first_name', 'Player')
                        
                        print(f"\n📨 Message from {first_name}: {text}")
                        
                        # ===== /START COMMAND =====
                        if text == '/start':
                            if user_id not in user_points:
                                user_points[user_id] = 0
                                save_data()
                                print(f"✅ New player: {first_name}")
                            
                            level, level_name = get_user_level(user_points[user_id])
                            
                            wallet_status = "✅ Connected" if user_id in user_wallets else "❌ Not connected"
                            
                            buttons = [
                                [{'text': f'⛏️ MINE (Lv.{level})', 'callback_data': 'mine'}],
                                [
                                    {'text': '💰 STATS', 'callback_data': 'stats'},
                                    {'text': '🎁 DAILY', 'callback_data': 'daily'}
                                ],
                                [
                                    {'text': '🦖 PLAY MINER DINO', 'callback_data': 'play_dino'},
                                    {'text': '🔗 WALLET', 'callback_data': 'connect_wallet'}
                                ],
                                [
                                    {'text': '🏆 LEADERBOARD', 'callback_data': 'leaderboard'},
                                    {'text': '👥 REFERRALS', 'callback_data': 'referrals'}
                                ]
                            ]
                            
                            caption = (
                                f"🚀 <b>Welcome back, {first_name}!</b>\n\n"
                                f"💰 Points: {format_number(user_points[user_id])}\n"
                                f"📊 Level: {level_name}\n"
                                f"⚡ Power: {get_mining_power(level)}x\n"
                                f"🔗 Wallet: {wallet_status}\n\n"
                                f"<i>Play Miner Dino to earn big points!</i>"
                            )
                            
                            send_photo(chat_id, FILE_IDS['welcome'], caption, buttons)
                            print("✅ Welcome sent")
                        
                        # ===== WALLET CONNECTION =====
                        elif text.startswith('/wallet'):
                            parts = text.split()
                            if len(parts) == 2:
                                wallet = parts[1]
                                chain_type, valid_wallet = validate_wallet(wallet)
                                
                                if valid_wallet:
                                    user_wallets[user_id] = valid_wallet
                                    save_data()
                                    send_message(chat_id, f"✅ Wallet connected!\nAddress: {valid_wallet[:10]}...")
                                    print(f"✅ Wallet connected for user {user_id}")
                                else:
                                    send_message(chat_id, "❌ Invalid wallet address")
                        
                        # ===== HANDLE WEB APP DATA (FROM GAME) =====
                        elif 'web_app_data' in update['message']:
                            try:
                                # Get the raw data
                                raw_data = update['message']['web_app_data']['data']
                                print(f"\n🎮 WEB APP DATA RECEIVED!")
                                print(f"📦 Raw data: {raw_data}")
                                
                                # Parse JSON
                                game_data = json.loads(raw_data)
                                print(f"📊 Parsed data: {game_data}")
                                
                                if game_data.get('action') == 'game_complete':
                                    score = int(game_data.get('score', 0))
                                    
                                    print(f"💰 Score: {score}")
                                    print(f"👤 User ID: {user_id}")
                                    
                                    # Get current points
                                    current_points = user_points.get(user_id, 0)
                                    print(f"💎 Current points: {current_points}")
                                    
                                    # ADD THE POINTS!
                                    user_points[user_id] = current_points + score
                                    
                                    print(f"💎 New total: {user_points[user_id]}")
                                    
                                    # Save to file
                                    save_data()
                                    print("✅ Data saved!")
                                    
                                    # Send confirmation
                                    send_message(
                                        chat_id,
                                        f"🎮 <b>Game Complete!</b>\n\n"
                                        f"💰 Points earned: {score}\n"
                                        f"💎 New balance: {format_number(user_points[user_id])}\n\n"
                                        f"Play again to earn more!"
                                    )
                                    
                                    # Remove the reply keyboard
                                    remove_keyboard = {
                                        'remove_keyboard': True
                                    }
                                    requests.post(
                                        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                        json={
                                            'chat_id': chat_id,
                                            'text': "You can continue with the main menu:",
                                            'reply_markup': json.dumps(remove_keyboard)
                                        }
                                    )
                                    
                                    print("✅ Confirmation sent")
                                    
                            except Exception as e:
                                print(f"❌ Error processing game data: {e}")
                                import traceback
                                traceback.print_exc()
                    
                    # ======== HANDLE BUTTON CLICKS ========
                    elif 'callback_query' in update:
                        query = update['callback_query']
                        chat_id = query['message']['chat']['id']
                        user_id = query['from']['id']
                        action = query['data']
                        
                        print(f"🖱️ Button: {action}")
                        
                        # ===== MINING GAME =====
                        if action == 'mine':
                            level, level_name = get_user_level(user_points.get(user_id, 0))
                            mining_power = get_mining_power(level)
                            
                            points_earned = random.randint(1, 5) * mining_power
                            critical = random.random() < 0.1
                            if critical:
                                points_earned *= 2
                            
                            user_points[user_id] = user_points.get(user_id, 0) + points_earned
                            
                            image_key = 'critical' if critical else 'mine'
                            buttons = [[{'text': '⛏️ MINE AGAIN', 'callback_data': 'mine'}]]
                            
                            send_photo(chat_id, FILE_IDS[image_key], 
                                     f"{'⚡ CRITICAL! ' if critical else ''}+{points_earned} points!", 
                                     buttons)
                            
                            if user_points[user_id] % 5 == 0:
                                save_data()
                            
                            print(f"✅ Mining: +{points_earned} points")
                        
                        # ===== PLAY MINER DINO GAME (USING REPLY KEYBOARD) =====
                        elif action == 'play_dino':
                            game_url = "https://kayceedking001.github.io/miner-dino-game/game.html"
                            
                            # IMPORTANT: Use Reply Keyboard, NOT Inline Keyboard
                            reply_keyboard = {
                                'keyboard': [[{
                                    'text': '🦖 PLAY MINER DINO',
                                    'web_app': {'url': game_url}
                                }]],
                                'resize_keyboard': True,
                                'one_time_keyboard': True
                            }
                            
                            send_message(
                                chat_id,
                                "🎮 <b>MINER DINO</b>\n\n"
                                "Jump over obstacles and earn points!\n\n"
                                "• Tap anywhere to jump\n"
                                "• Easy difficulty - perfect for everyone\n"
                                "• Points go to your balance!\n\n"
                                "Tap the button below to play:",
                                reply_keyboard=reply_keyboard
                            )
                            print("✅ Game link sent with Reply Keyboard")
                        
                        # ===== WALLET MENU =====
                        elif action == 'connect_wallet':
                            if user_id in user_wallets:
                                send_message(
                                    chat_id,
                                    f"🔗 <b>Wallet Connected</b>\n\n"
                                    f"Address: <code>{user_wallets[user_id][:10]}...{user_wallets[user_id][-6:]}</code>\n\n"
                                    f"Benefits:\n"
                                    f"• 20% bonus points in games\n"
                                    f"• Future airdrop eligibility"
                                )
                            else:
                                send_message(
                                    chat_id,
                                    "🔗 <b>Connect Your Wallet</b>\n\n"
                                    "Send your wallet address:\n"
                                    "<code>/wallet 0xYourEthereumAddress</code>\n\n"
                                    "Supported:\n"
                                    "• EVM: 0x... (MetaMask)\n"
                                    "• TON: EQ... (Tonkeeper)"
                                )
                        
                        # ===== STATS =====
                        elif action == 'stats':
                            points = user_points.get(user_id, 0)
                            level, level_name = get_user_level(points)
                            
                            sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
                            rank = 1
                            for uid, _ in sorted_users:
                                if uid == user_id:
                                    break
                                rank += 1
                            
                            wallet_status = "✅ Connected" if user_id in user_wallets else "❌ Not connected"
                            
                            send_message(
                                chat_id,
                                f"📊 <b>YOUR STATS</b>\n\n"
                                f"💰 Points: {format_number(points)}\n"
                                f"📈 Level: {level_name}\n"
                                f"⚡ Power: {get_mining_power(level)}x\n"
                                f"🏆 Rank: #{rank}\n"
                                f"🔗 Wallet: {wallet_status}"
                            )
                        
                        # ===== DAILY BONUS =====
                        elif action == 'daily':
                            today = str(datetime.date.today())
                            
                            if user_id not in daily_claimed or daily_claimed[user_id] != today:
                                level, level_name = get_user_level(user_points.get(user_id, 0))
                                bonus = 50 * level
                                
                                user_points[user_id] = user_points.get(user_id, 0) + bonus
                                daily_claimed[user_id] = today
                                
                                send_photo(chat_id, FILE_IDS['daily'], f"🎁 +{bonus} points!")
                                save_data()
                                print(f"✅ Daily bonus: +{bonus}")
                            else:
                                send_message(chat_id, "⏰ Already claimed today!")
                        
                        # ===== LEADERBOARD =====
                        elif action == 'leaderboard':
                            top_players = sorted(user_points.items(), key=lambda x: x[1], reverse=True)[:10]
                            
                            sorted_all = sorted(user_points.items(), key=lambda x: x[1], reverse=True)
                            user_rank = 1
                            for uid, _ in sorted_all:
                                if uid == user_id:
                                    break
                                user_rank += 1
                            
                            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                            lb_text = "🏆 <b>LEADERBOARD</b> 🏆\n\n"
                            
                            for i, (uid, points) in enumerate(top_players):
                                level, _ = get_user_level(points)
                                wallet_icon = "🔗" if uid in user_wallets else "👤"
                                lb_text += f"{medals[i]} <b>Level {level}</b> {wallet_icon}: {format_number(points)} pts\n"
                            
                            lb_text += f"\n⭐ Your Rank: #{user_rank}"
                            
                            send_photo(chat_id, FILE_IDS['leaderboard'], lb_text)
                            print("✅ Leaderboard sent")
                        
                        # ===== REFERRALS =====
                        elif action == 'referrals':
                            ref_count = len(user_referrals[user_id])
                            ref_points = ref_count * 50
                            
                            ref_link = f"https://t.me/firstcreationbot?start={user_id}"
                            
                            send_message(
                                chat_id,
                                f"👥 <b>REFERRALS</b>\n\n"
                                f"Your referrals: {ref_count}\n"
                                f"Bonus points: {ref_points}\n\n"
                                f"Your link:\n<code>{ref_link}</code>"
                            )
                        
                        print("✅ Response sent")
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n\n👋 Stopping bot...")
            save_data()
            print(f"✅ Final save: {len(user_points)} players")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        save_data()
        print("\n👋 Goodbye!")