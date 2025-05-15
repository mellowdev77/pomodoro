import sqlite3
import random
import sys
from dataclasses import dataclass
from db import *

@dataclass
class Config:
    load_new_quote: bool = True
    timers_wait_for_user: bool = True
    default_quote: str = "Chop wood"
    default_round: float = 25.0
    default_break: float = 5.0
    timers_based_on_average = True

# utils
def string_to_boolean(input):
    input = input.lower().strip()
    match input:
        case "yes" | "y" | "true" | "t":
            return True
        case _:
            return False

# config
def load_config():
    config = Config()

    if bool(get_first_row("CONFIG", "create_actions")):
        create_actions()

    if bool(get_first_row("CONFIG", "load_new_quote")):
        config.load_new_quote = True

    if bool(get_first_row("CONFIG", "timers_based_on_average")):
        config.timers_based_on_average = True

    if bool(get_first_row("CONFIG", "timers_wait_for_user")):
        config.timers_wait_for_user = True

    if bool(get_first_row("CONFIG", "change_default_timers")):
        config.default_round, config.default_break = change_default_timers()

    if bool(get_first_row("CONFIG", "change_default_quote")):
        print("insert the new default quote:")
        config.default_quote = input()
        update_table("DEFAULT_QUOTE", "default_quote", config.default_quote)

    config.default_round = get_first_row("DEFAULT_LENGTH", "default_round_length")
    config.default_break = get_first_row("DEFAULT_LENGTH", "default_break_length")
    return config

def update_config():
    print("updating the config...")

    rows = get_all_rows("CONFIG")
    default_round = get_first_row("DEFAULT_LENGTH", "default_round_length")
    default_break = get_first_row("DEFAULT_LENGTH", "default_break_length")

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

# break and round duration
def change_default_timers():
    default_round = 25
    default_break = 5
    round_time = 0.0
    break_time = 0.0
    while (True):
        try:
            print("Round Length:")
            round_time = float(input())
            print("Break Length:")
            break_time = float(input())
        except:
            print("\n...length should be a number...\n")
        finally:
            update_table("DEFAULT_LENGTH", "default_round_length", f"'{round_time}'")
            update_table("DEFAULT_LENGTH", "default_break_length", f"'{break_time}'")
            default_round = round_time
            default_break = break_time
            break
    return default_round, default_break

def save_average_duration_over_time(round_avg, round_count, break_avg, break_count):
    total_rounds_sum, total_rounds_count, total_breaks_sum, total_breaks_count = 0, 0, 0, 0
    average_round, average_break, ratio = 0, 0, 0

    if round_avg != 0 and break_avg != 0:
        # average round length, amount of rounds, average break length, amount of breaks
        insert_into_table("AVERAGE_RATIO", f"{round_avg}','{round_count}','{break_avg}','{break_count}")

    for row in get_all_rows("AVERAGE_RATIO"):
        total_rounds_sum += float(row["average_round_length"]) * float(row["average_round_count"])
        total_rounds_count += float(row["average_round_count"])

        total_breaks_sum += float(row["average_break_length"]) * float(row["average_break_count"])
        total_breaks_count += float(row["average_break_count"])

    if total_rounds_count != 0 and total_breaks_count != 0:
        average_round = total_rounds_sum / total_rounds_count
        average_break = total_breaks_sum / total_breaks_count
        ratio = average_round/average_break

    print(f"\nOn average your rounds are {average_round:.1f} mins long.")
    print(f"On average your breaks are {average_break:.1f} mins long.")
    print(f"Your ratio is: {ratio:.1f} The standard pomodoro ratio is: 5.0\n")
    print(f"This session, your {total_rounds_count} rounds were on average {average_round:.1f} mins long each.")
    print(f"This session, your {total_breaks_count} breaks were on average {average_break:.1f} mins long each.")
