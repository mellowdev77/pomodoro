import time
import requests
from plyer import notification
from io_operations import *

## global variables
load_quotes = True
timers_dont_wait_for_user = True
timers_based_on_average = False
default_quote = ""
default_round = 25
default_break = 5
# (duration, number of rounds)
session_rounds = (0,0)
session_breaks = (0,0)

def get_random_quote():
    if load_quotes:
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
    if timers_dont_wait_for_user:
        print(f"~~~~~~press enter to start the {action}~~~~~~")
        input()

    local_time = time.localtime()
    local_time = f"{local_time.tm_hour}h{local_time.tm_min}m{local_time.tm_sec}s"
    print(f"{action} started at: {local_time}")

def update_session_average(action, duration):
    global session_breaks
    global session_rounds
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

def calculate_time_passed(previous_time):
    return ((time.localtime().tm_hour - previous_time.tm_hour)*24*60 + (time.localtime().tm_min - previous_time.tm_min)*60 + (time.localtime().tm_sec - previous_time.tm_sec))/60

if __name__ == "__main__":
    load_config(True)
    default_quote = load_default_quote()
    default_round, default_break = load_default_lengths()
    round_time = default_round
    break_time = default_break

    if timers_based_on_average:
        round_time, break_time = total_average_round_time(default_round, default_break)
    try:
        while True:
            quote = get_random_quote()
            actions = random_actions()

            # break is over, alert the user to start the round
            if timers_dont_wait_for_user:
                send_notification("Press enter to start the round.", "")

            time_before_start = time.localtime()
            start_action("round")
            # round started
            send_notification(f"Round Started! ({round_time} mins)", quote)
            time.sleep(60 * round_time)
            round_duration = calculate_time_passed(time_before_start)
            update_session_average("round", round_duration)

            # round is over, alert the user to start the break
            break_duration = break_time
            break_text = "break"

            # every 5th break, take an extra 10 mins off
            if session_rounds[1] % 5 == 0:
                break_duration = break_time + 10
                break_text = "long break"

            if timers_dont_wait_for_user:
                send_notification(f"round Over! Start the {str.capitalize(break_text)} ({break_duration} mins)", "")

            time_before_start = time.localtime()
            start_action(break_text)
            send_notification(f"Break Started! ({break_duration} mins)", actions)

            # break or long break started
            time.sleep(60 * break_duration)
            round_duration = calculate_time_passed(time_before_start)
            update_session_average("break", round_duration)

    except KeyboardInterrupt:
        set_default_config()
        save_average_duration_over_time()

        print(f"\ntoday the average round time was: {session_rounds[0]:.2f} mins, and you completed {session_rounds[1]} rounds")
        print(f"today the average break time was: {session_breaks[0]:.2f} mins, and you took {session_breaks[1]} breaks")
        print("\n....closing pomodoro app...")
        exit()
