from main import *
from db import *
import sqlite3
import random

# utils
def string_to_boolean(input):
    input = input.lower().strip()
    match input:
        case "yes" | "y" | "true" | "t":
            return True
        case _:
            return False

def start_db():
    create_tables()
    empty_tables = get_empty_tables()
    if empty_tables:
        insert_default_values(empty_tables)

def recieve_arguments():
    for arg in sys.argv:
        match (arg.lower()):
            case "-config" | "-c" | "-update_config" | "-update":
                update_config()
            case "-drop" | "-restart" | "-delete":
                drop_tables()
                start_db()
            case _:
                print("not updating config...")

# config
def load_config():
    config = Config()
    configs = get_all_rows("CONFIG")

    for config_name in configs[0].keys():
        bool_value = bool(configs[0][config_name])

        match(config_name):
            case "create_actions":
                if bool_value:
                    create_actions()
            case "load_new_quote":
                config.load_quotes = bool_value
            case "instant_start_timers":
                config.timers_dont_wait_for_user = not bool_value
            case "change_default_quote":
                if bool_value:
                    config.default_quote = change_default_quote()
            case "default_timers_based_on_round_average":
                config.timers_based_on_average = bool_value
            case "change_default_timers":
                if bool_value:
                    config.default_round, config.default_break = change_default_lengths()
            case _:
                pass
    return config

def update_config():
    print("updating the config...")

    rows = get_all_rows("CONFIG")
    default_round, default_break = load_default_lengths()
    for config_name in rows[0].keys():
        text = ""
        match config_name:
            case "create_actions":
                text = "Create new actions for breaks?"
            case "load_new_quote":
                text = "Show a random quote at the start of each round?"
            case "instant_start_timers":
                text = "Start rounds and breaks automatically?"
            case "change_default_quote":
                text = "Change your default quote?"
            case "default_timers_based_on_round_average":
                text = f"Use your average round and break duration instead of the default? ({default_round}, {default_break})"
            case "change_default_timers":
                text = f"Change your default timers length? Current: ({default_round}, {default_break})"
            case _:
                text = f"Please provide a value for: {config_name}."

        print(text)
        bool_value = string_to_boolean(input())
        update_table("CONFIG", config_name, int(bool_value))

# break actions
def create_actions():
    print("Creating actions... (exit, quit, q, e)")
    user_input = ""

    while True:
        print("New Action: ")
        user_input = input()
        if user_input == "exit" or user_input == "quit" or user_input == "q" or user_input == "e":
            break
        insert_into_table("ACTIONS", user_input)

def random_actions():
    actions = []
    return_string = ""

    rows = get_all_rows("ACTIONS")
    actions = []
    for action in rows:
        actions.append(action["actions"])

    random.shuffle(actions)
    length = len(actions)
    if length > 6:
        extra = length - 6
        actions = actions[:-extra]

    for action in actions:
        if action not in return_string:
            return_string += action + "; "

    return return_string

# quotes
def load_default_quote():
    return get_first_row("DEFAULT_QUOTE", "default_quote")

def change_default_quote():
    print("insert the new default quote:")
    default_quote = input()
    update_table("DEFAULT_QUOTE", "default_quote", default_quote)

    return default_quote

# break and round duration
def load_default_lengths():
    default_round = get_first_row("DEFAULT_LENGTH", "default_round_length")
    default_break = get_first_row("DEFAULT_LENGTH", "default_break_length")
    return default_round, default_break

def change_default_lengths():
    default_round = 25
    default_break = 5
    while (True):
        print("Round Length:")
        round_time = input()
        print("Break Length:")
        break_time = input()
        try:
            round_time = float(round_time)
            break_time = float(break_time)
        except:
            print("\n...length should be a number...\n")
        finally:
            update_table("DEFAULT_LENGTH", "default_round_length", f"'{round_time}'")
            update_table("DEFAULT_LENGTH", "default_break_length", f"'{break_time}'")
            default_round = round_time
            default_break = break_time
            break
    return default_round, default_break

def save_average_duration_over_time(session_rounds, session_breaks):
    if session_rounds[0] != 0 and session_rounds[0] != 0:
        # average round length, amount of rounds, average break length, amount of breaks
        insert_into_table("AVERAGE_RATIO", f"{session_rounds[0]}','{session_rounds[1]}','{session_breaks[0]}','{session_breaks[1]}")

    average_round, average_break = total_average_round_time()
    print(f"\nOn average your rounds are {average_round:.1f} mins long.")
    print(f"On average your breaks are {average_break:.1f} mins long.")
    if (average_break != 0):
        print(f"your ratio is: {(average_round/average_break):.1f}. The standard pomodoro ratio is: 5.")
    return session_rounds, session_breaks

def total_average_round_time():
    round_sum = 0
    round_count = 0
    break_sum = 0
    break_count = 0

    rows = get_all_rows("AVERAGE_RATIO")
    for row in rows:
        round_sum += float(row["average_round_length"]) * float(row["average_round_count"])
        round_count += float(row["average_round_count"])

        break_sum += float(row["average_break_length"]) * float(row["average_break_count"])
        break_count += float(row["average_break_count"])

    if round_count != 0 and break_count != 0:
        average_round = round_sum / round_count
        average_break = break_sum / break_count

        return average_round, average_break
    return 0,0
