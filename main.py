import time
import requests
from plyer import notification
from io_operations import *
from dataclasses import dataclass

@dataclass
class Config:
    load_quotes: bool = True
    timers_dont_wait_for_user: bool = False
    default_quote: str = "Chop wood"
    default_round: float = 25.0
    default_break: float = 5.0
    timers_based_on_average = True

def get_random_quote(default_quote):
    if config.load_quotes:
        try:
            response = requests.get("https://zenquotes.io/api/random")
            response.raise_for_status()  # Raise an error for bad responses
            quote_data = response.json()
            return f'"{quote_data[0]["q"]}" - {quote_data[0]["a"]}'
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return default_quote
    else:
        return default_quote

def send_notification(title, quote):
    notification.notify(title, quote)

def start_action(action):
    if config.timers_dont_wait_for_user:
        print(f"~~~~~~press enter to start the {action}~~~~~~")
        input()

    local_time = time.localtime()
    local_time = f"{local_time.tm_hour}h{local_time.tm_min}m{local_time.tm_sec}s"
    print(f"{action} started at: {local_time}")

def update_session_average(action, duration, session_rounds, session_breaks):
    match action:
        case "break":
            average_duration = session_breaks[0]
            amount_of_breaks = session_breaks[1]
            total = (average_duration * amount_of_breaks) + duration
            new_average = total / (amount_of_breaks + 1)
            session_breaks = (new_average, amount_of_breaks + 1)

        case "round":
            average_duration = session_rounds[0]
            amount_of_rounds = session_rounds[1]
            total = (average_duration * amount_of_rounds) + duration
            new_average = total / (amount_of_rounds + 1)
            session_rounds = (new_average, amount_of_rounds + 1)
    return session_breaks, session_rounds

def calculate_time_passed(previous_time):
    return ((time.localtime().tm_hour - previous_time.tm_hour)*24*60 + (time.localtime().tm_min - previous_time.tm_min)*60 + (time.localtime().tm_sec - previous_time.tm_sec))/60

if __name__ == "__main__":
    config = load_config(True)

    config.default_quote = load_default_quote()
    config.default_round, config.default_break = load_default_lengths()
    round_time = config.default_round
    break_time = config.default_break
    session_rounds = (0,0)
    session_breaks = (0,0)

    if config.timers_based_on_average:
        round_time, break_time = total_average_round_time()
    try:
        while True:
            quote = get_random_quote(config.default_quote)
            actions = random_actions()

            # break is over, alert the user to start the round
            if config.timers_dont_wait_for_user:
                send_notification("Press enter to start the round.", "")

            time_before_start = time.localtime()
            start_action("round")
            # round started
            send_notification(f"Round Started! ({round_time} mins)", quote)
            time.sleep(60 * round_time)
            round_duration = calculate_time_passed(time_before_start)
            session_rounds, session_breaks = update_session_average("round", round_duration, session_rounds, session_breaks)

            # round is over, alert the user to start the break
            break_duration = break_time
            break_text = "break"

            # every 5th break, take an extra 10 mins off
            if session_rounds[1] % 5 == 0:
                break_duration = break_time + 10
                break_text = "long break"

            if config.timers_dont_wait_for_user:
                send_notification(f"Round Over! Start the {str.capitalize(break_text)} ({break_duration} mins)", "")

            time_before_start = time.localtime()
            start_action(break_text)
            send_notification(f"Break Started! ({break_duration} mins)", actions)

            # break or long break started
            time.sleep(60 * break_duration)
            round_duration = calculate_time_passed(time_before_start)
            session_rounds, session_breaks = update_session_average("break", round_duration, session_rounds, session_breaks)

    except KeyboardInterrupt:
        set_default_config()
        save_average_duration_over_time(session_rounds, session_breaks)

        print(f"\nThis session, your {session_rounds[1]} rounds were on average {session_rounds[0]:.1f} mins long each.")
        print(f"This session, your {session_breaks[1]} breaks were on average {session_breaks[0]:.1f} mins long each.")
        print("\n....closing pomodoro app...")
        exit()
