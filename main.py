import time
import requests
import random
from plyer import notification

load_quotes = True
timers_wait_for_user = True
default_quote = ""
# (duration, number of sessions)
todays_average_session = (0,0)
todays_average_break = (0,0)

def get_random_quote():
    if not load_quotes:
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
    notification.notify(
        title=title,
        message=quote,
        app_name="Notifier"
    )

def start(action):
    if timers_wait_for_user:
        print(f"~~~~~~press enter to start the {action}~~~~~~")
        input()

    print_time(action)

def random_actions():
    actions = []
    return_string = ""

    with open('config/actions.config', 'r') as file:
        actions = file.read().split(";")[:-2]

    random.shuffle(actions)
    length = len(actions)
    if length > 6:
        extra = length - 6
        actions = actions[:-extra]

    for action in actions:
        if action not in return_string:
            return_string += action + "; "

    return return_string

def print_time(action):
    local_time = time.localtime()
    local_time = f"{local_time.tm_hour}h{local_time.tm_min}m{local_time.tm_sec}s"
    print(f"{action} started at: {local_time}")

def create_actions():
    with open('config/actions.config', 'w') as file:
        print("Creating actions... (exit, quit, q, e)")
        user_input = ""

        while user_input != "exit" and user_input != "quit" and user_input != "q" and user_input != "e":
            print("New Action: ")
            user_input = input()
            file.write(user_input + ";")

def update_config():
    print("updating the config...")
    operations = []
    with open('config/config.config', 'r') as file:
        for line in file.read().split("\n"):
            line_values = line.split("=")
            config_name = line_values[0]
            if len(config_name) > 1:
                operations.append(config_name.strip())

    with open('config/config.config', 'w') as file:
        for operation in operations:
            text = ""
            match operation:
                case "update_config":
                    text = "Customize the configuration on the next launch?"
                case "create_actions":
                    text = "Create new actions for breaks?"
                case "load_new_quote":
                    text = "Show a random quote at the start of each session?"
                case "instant_start_timers":
                    text = "Start sessions and breaks automatically?"
                case "change_default_quote":
                    text = "Change your default quote?"
                case _:
                    text = f"Please provide a value for: {operation}."

            print(text)
            bool_value = string_to_boolean(input())
            file.write(f"{operation}={bool_value};\n")

    load_config(False)

def string_to_boolean(input):
    input = input.lower().strip()
    match input:
        case "yes":
            return True
        case "y":
            return True
        case "true":
            return True
        case _:
            return False

def load_config(first_time):
    global load_quotes
    global timers_wait_for_user

    with open('config/config.config', 'r') as file:
        for line in file.read().split("\n"):
            line_values = line.split("=")
            if len(line_values) < 2:
                return

            bool_value = string_to_boolean(line_values[1][:-1])
            config_name = line_values[0]

            match(config_name.strip()):
                case "update_config":
                    if bool_value and first_time:
                        update_config()
                        return
                    else:
                        print("not updating config... saved on config/config.config")
                case "create_actions":
                    if bool_value:
                        create_actions()
                case "load_new_quote":
                    load_quotes = bool_value
                case "instant_start_timers":
                    timers_wait_for_user = not bool_value
                case "change_default_quote":
                    if bool_value:
                        change_default_quote()
                case _:
                    pass
    return

def change_default_quote():
    global default_quote
    with open('config/default_quote.config', 'w') as file:
        print("insert the new default quote:")
        user_input = input()
        file.write(user_input)
        default_quote = user_input

def load_default_quote():
    global default_quote
    with open('config/default_quote.config', 'r') as file:
        default_quote = file.read()

def set_default_config():
    flag = False
    with open('config/config.config', 'r') as file:
        if len(file.read()) <= 0:
            flag = True

    # config file is empty, override with default
    if flag:
        with open('config/config.config', 'w') as file:
            file.write("update_config=True;\ncreate_actions=False;\nload_new_quote=False;\ninstant_start_timers=False;\nchange_default_quote=False;")

def calculate_average_session_time(action, duration):
    global todays_average_break
    global todays_average_session
    match action:
        case "break":
            average_duration = todays_average_break[0]
            amount_of_breaks = todays_average_break[1]
            total = (average_duration * amount_of_breaks) + duration
            new_average = total / (amount_of_breaks + 1)
            todays_average_break = (new_average, amount_of_breaks + 1)

        case "session":
            average_duration = todays_average_session[0]
            amount_of_sessions = todays_average_session[1]
            total = (average_duration * amount_of_sessions) + duration
            new_average = total / (amount_of_sessions + 1)
            todays_average_session = (new_average, amount_of_sessions + 1)

def calculate_time_passed(previous_time):
    return ((time.localtime().tm_hour - previous_time.tm_hour)*24*60 + (time.localtime().tm_min - previous_time.tm_min)*60 + (time.localtime().tm_sec - previous_time.tm_sec))/60

def print_todays_averages():
    print(f"\ntoday the average session time was: {todays_average_session[0]:.2f} mins, and you completed {todays_average_session[1]} sessions")
    print(f"today the average break time was: {todays_average_break[0]:.2f} mins, and you took {todays_average_break[1]} breaks")

def save_average_duration_over_time():
    if todays_average_session[0] != 0 and todays_average_session[0] != 0:
        with open('config/average_ratio.config', 'a') as file:
            # average session length, amount of sessions, average break length, amount of breaks
            file.write(f"{todays_average_session[0]},{todays_average_session[1]},{todays_average_break[0]},{todays_average_break[1]};")

        session_sum = 0
        session_count = 0
        break_sum = 0
        break_count = 0
        with open('config/average_ratio.config', 'r') as file:
            for line in file.read().split(";"):
                if line != "" and line != "\n":
                    session_sum += float(line.split(",")[0]) * float(line.split(",")[1])
                    session_count += float(line.split(",")[1])

                    break_sum += float(line.split(",")[2]) * float(line.split(",")[3])
                    break_count += float(line.split(",")[3])

        if session_count != 0 and break_count != 0:
            average_session = session_sum / session_count
            average_break = break_sum / break_count
            print(f"your total average work session is: {average_session:.2f}.")
            print(f"your total average break is: {average_break:.2f}.")
            if (average_break != 0):
                print(f"your ratio is: {(average_session/average_break):.2f}. The standard pomodoro ratio is: 5.")

if __name__ == "__main__":

    load_config(True)
    load_default_quote()
    try:
        while True:
            quote = get_random_quote()
            actions = random_actions()

            # break is over, alert the user to start the session
            if timers_wait_for_user:
                send_notification("Press enter to start the session.", "")

            time_before_start = time.localtime()
            start("session")

            # session started
            send_notification("Session Started! (25 mins)", quote)
            time.sleep(60*25)
            session_duration = calculate_time_passed(time_before_start)
            calculate_average_session_time("session", session_duration)

            # session is over, alert the user to start the break
            brake_duration = 5
            brake_text = "brake"

            # every 5th break, take an extra 10 mins off
            if todays_average_session[1] % 5 == 0:
                brake_duration = 15
                brake_text = "long brake"

            if timers_wait_for_user:
                send_notification(f"Session Over! Start the {str.capitalize(brake_text)} ({brake_duration} mins)", "")

            time_before_start = time.localtime()
            start(brake_text)
            send_notification(f"Break Started! ({brake_duration} mins)", actions)

            # break or long break started
            time.sleep(60 * brake_duration)
            session_duration = calculate_time_passed(time_before_start)
            calculate_average_session_time("break", session_duration)

    except KeyboardInterrupt:
        set_default_config()
        print_todays_averages()
        save_average_duration_over_time()
        print("\n....closing pomodoro app...")
        exit()
