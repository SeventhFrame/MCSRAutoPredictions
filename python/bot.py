import time
import datetime as dt
import requests
import threading

stop_bot_check = threading.Event()
TWITCH_PREDICTIONS_URL = "https://api.twitch.tv/helix/predictions"
run_status = "idle"
run_message = ""

def set_run_status(status, message=""):
    global run_status, run_message
    run_status = status
    run_message = message

def timestamp():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y/%m/%d %H:%M")

def parse_match_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))

def get_latest_match(player):
    response = requests.get(
        f"https://api.mcsrranked.com/users/{player}/matches",
        timeout=5,
    )
    if not response.ok:
        raise RuntimeError(f"MCSR request failed with status {response.status_code}")

    data = response.json().get("data", [])
    return data[0] if data else None

def match_check(player_id, latest_time):
    latest_match = get_latest_match(player_id)
    if latest_match is None:
        return None

    updated_latest_time = parse_match_time(latest_match["date"])
    winner_uuid = latest_match["result"]["uuid"]

    if updated_latest_time > latest_time:
        return winner_uuid, updated_latest_time
    else:
        return None

def check_winner(player_id, winner_uuid):
    if winner_uuid == player_id:
        return f"{timestamp()} twitch: player is winner"
    else:
        return f"{timestamp()} twitch: player is not winner"

def twitch_headers(bearer_id, client_id):
    return {
        "Authorization": f"Bearer {bearer_id}",
        "Client-Id": client_id,
        "Content-Type": "application/json",
    }

def create_prediction(bearer_id, client_id, broadcaster_id):
    response = requests.post(
        TWITCH_PREDICTIONS_URL,
        headers=twitch_headers(bearer_id, client_id),
        json={
            "broadcaster_id": broadcaster_id,
            "title": "WILL I WIN?",
            "outcomes": [
                {"title": "YES"},
                {"title": "NO"},
            ],
            "prediction_window": 120,
        },
        timeout=5,
    )
    if not response.ok:
        raise RuntimeError(
            f"Twitch create prediction failed with status {response.status_code}"
        )

    data = response.json().get("data", [])
    if not data or not data[0].get("id"):
        raise RuntimeError("Twitch response had no prediction ID")

    prediction = data[0]
    outcomes = {
        outcome.get("title"): outcome.get("id")
        for outcome in prediction.get("outcomes", [])
    }
    if not outcomes.get("YES") or not outcomes.get("NO"):
        raise RuntimeError("Twitch response had incomplete prediction outcomes")

    return {
        "id": prediction["id"],
        "yes_id": outcomes["YES"],
        "no_id": outcomes["NO"],
    }

def end_prediction(
    prediction,
    bearer_id,
    client_id,
    broadcaster_id,
    status,
    winning_outcome_id=None,
):
    params = {
        "broadcaster_id": broadcaster_id,
        "id": prediction["id"],
        "status": status,
    }
    if winning_outcome_id is not None:
        params["winning_outcome_id"] = winning_outcome_id

    response = requests.patch(
        TWITCH_PREDICTIONS_URL,
        params=params,
        headers=twitch_headers(bearer_id, client_id),
        timeout=5,
    )
    if not response.ok:
        raise RuntimeError(
            f"Twitch prediction {status.lower()} failed with status {response.status_code}"
        )

def start_bot(player_id, bearer_id, client_id, broadcaster_id):
    active_prediction = None
    set_run_status("running")

    try:
        latest_time = dt.datetime.now(dt.timezone.utc)
        while not stop_bot_check.is_set():
            active_prediction = create_prediction(
                bearer_id,
                client_id,
                broadcaster_id,
            )
            print(f"{timestamp()} twitch: prediction started")

            while not stop_bot_check.is_set():
                try:
                    result = match_check(player_id, latest_time)
                except (
                    requests.RequestException,
                    ValueError,
                    KeyError,
                    TypeError,
                    RuntimeError,
                ) as error:
                    print(f"{timestamp()} MCSR check failed: {error}")
                    if stop_bot_check.wait(5):
                        break
                    continue

                if result is None:
                    if stop_bot_check.wait(5):
                        break
                    continue

                winner_uuid, latest_time = result
                winning_outcome_id = (
                    active_prediction["yes_id"]
                    if winner_uuid == player_id
                    else active_prediction["no_id"]
                )
                print(f"{timestamp()} {check_winner(player_id, winner_uuid)}")
                end_prediction(
                    active_prediction,
                    bearer_id,
                    client_id,
                    broadcaster_id,
                    "RESOLVED",
                    winning_outcome_id,
                )
                active_prediction = None
                break
    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        RuntimeError,
    ) as error:
        print(f"{timestamp()} bot stopped after error: {error}")
        set_run_status("error", str(error))
    finally:
        if active_prediction is not None:
            try:
                end_prediction(
                    active_prediction,
                    bearer_id,
                    client_id,
                    broadcaster_id,
                    "CANCELED",
                )
            except (requests.RequestException, ValueError, RuntimeError) as error:
                print(f"{timestamp()} could not cancel prediction: {error}")
        if run_status != "error":
            set_run_status("stopped")
        print(f"{timestamp()} bot stopped")



