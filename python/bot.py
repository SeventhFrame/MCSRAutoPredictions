import time
import datetime as dt
import requests
import sys
import threading

player = "7a5d462c58f74bc98bde83dd5c346e03"

stop_bot_check = threading.Event()

def timestamp():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y/%m/%d %H:%M")

def get_latest_match(player):
    r = requests.get(f"https://api.mcsrranked.com/users/{player}/matches", timeout=5)
    latest = r.json()["data"][0]
    
    return latest

def match_check(latest_time):
    latest_match = get_latest_match(player)

    updated_latest_time = latest_match["date"]
    winner_uuid = latest_match["result"]["uuid"]

    if updated_latest_time > latest_time:
        return winner_uuid, updated_latest_time
    else:
        return None

def check_winner(winner_uuid):
    if winner_uuid == player:
        return f"{timestamp()} twitch: player is winner"
    else:
        return f"{timestamp()} twitch: player is not winner"

def start_bot():
    
    latest_time = int(time.time())
    print(f"{timestamp()} twitch: start new prediction")
    
    while not stop_bot_check.is_set():
        result = match_check(latest_time)

        if result is not None:
            
            winner_uuid, updated_latest_time = result
            print(f"{timestamp()} {check_winner(winner_uuid)}")
            latest_time = updated_latest_time

            if stop_bot_check.wait(5):
                break

            print(f"{timestamp()} twitch: start new prediction")

        stop_bot_check.wait(5)
        
    print(f"{timestamp()} bot stopped")



