import time
import requests
from plyer import notification
from io_operations import *

def get_random_quote(default_quote):
    if config.load_new_quote:
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

def start_action(action):
    if config.timers_wait_for_user:
        print(f"~~~~~~press enter to start the {action}~~~~~~")
        input()

    local_time = time.localtime()
    local_time = f"{local_time.tm_hour}h{local_time.tm_min}m{local_time.tm_sec}s"
    print(f"{action} started at: {local_time}")

def calculate_time_passed(previous_time):
    return ((time.localtime().tm_hour - previous_time.tm_hour)*24*60 + (time.localtime().tm_min - previous_time.tm_min)*60 + (time.localtime().tm_sec - previous_time.tm_sec))/60

if __name__ == "__main__":
    update_config_flag = False
    for arg in sys.argv:
        match (arg.lower()):
            case "-config" | "-c" | "-update_config" | "-update":
                update_config_flag = True
            case "-drop" | "-restart" | "-delete":
                print("dropping tables...")

                drop_tables()
                create_tables()
                empty_tables = get_empty_tables()
                if empty_tables:
                    insert_default_values(empty_tables)
            case _:
                print("not updating config...")
                create_tables()
                empty_tables = get_empty_tables()
                if empty_tables:
                    insert_default_values(empty_tables)

    if update_config_flag:
        update_config()

    config = load_config()
    round_avg = 0
    round_count = 0
    break_avg = 0
    break_count = 0
    first_loop = True
    time_before_start = time.localtime()

    if config.timers_based_on_average:
        round_sum, round_count, break_sum, break_count = 0, 0, 0, 0

        for row in get_all_rows("AVERAGE_RATIO"):
            round_sum += float(row["average_round_length"]) * float(row["average_round_count"])
            break_count += float(row["average_round_count"])

            break_sum += float(row["average_break_length"]) * float(row["average_break_count"])
            break_count += float(row["average_break_count"])

        if round_count != 0 and break_count != 0:
            config.default_round = round_sum / round_count
            config.default_break = break_sum / break_count
    try:
        while True:

            quote = get_random_quote(config.default_quote)
            actions = random_actions()

            # break is over, alert the user to start the round
            if config.timers_wait_for_user:
                notification.notify("Press enter to start the round.", "", timeout = 2)

            start_action("round")
            if not first_loop:
                # round started, add passed time to break average
                total_time_passed = (break_avg * break_count) + calculate_time_passed(time_before_start)
                break_count += 1
                break_avg = total_time_passed / break_count

            notification.notify(f"Round Started! ({config.default_round} mins)", quote)
            time_before_start = time.localtime()
            time.sleep(config.default_round * 60)

            # round is over, alert the user to start the break
            break_duration = config.default_break
            break_text = "break"

            # every 5th break, take an extra 10 mins off
            if round_count != 0 and break_count % 5 == 0:
                break_duration = config.default_break + 10
                break_text = "long break"

            if config.timers_wait_for_user:
                notification.notify(f"Round Over! Start the {str.capitalize(break_text)} ({break_duration} mins)", "", timeout = 5)

            start_action(break_text)
            total_time_passed = (round_avg * round_count) + calculate_time_passed(time_before_start)
            round_count += 1
            round_avg = total_time_passed / round_count
            notification.notify(f"Break Started! ({break_duration} mins)", actions, timeout = 15)

            # break or long break started
            time_before_start = time.localtime()
            time.sleep(break_duration * 60)
            first_loop = False

    except KeyboardInterrupt:
        save_average_duration_over_time(round_avg, round_count, break_avg, break_count)

        print("\n....closing pomodoro app...")
        exit()
