from main import *
from main import Config
import random

# utils
def string_to_boolean(input):
    input = input.lower().strip()
    match input:
        case "yes":
            return True
        case "y":
            return True
        case "true":
            return True
        case "t":
            return True
        case _:
            return False

# config
def load_config(first_time):
    config = Config()
    with open('config/config.config', 'r') as file:
        for line in file.read().split("\n"):
            line_values = line.split("=")
            if len(line_values) < 2:
                return config

            bool_value = string_to_boolean(line_values[1][:-1])
            config_name = line_values[0]

            match(config_name.strip()):
                case "update_config":
                    if bool_value and first_time:
                        update_config(config)
                        return load_config(False)
                    else:
                        print("not updating config... saved on config/config.config")
                case "create_actions":
                    if bool_value:
                        create_actions()
                case "load_new_quote":
                    config.load_quotes = bool_value
                case "instant_start_timers":
                    config.timers_dont_wait_for_user = bool_value
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

def update_config(config):
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
                    text = "Show a random quote at the start of each round?"
                case "instant_start_timers":
                    text = "Start rounds and breaks automatically?"
                case "change_default_quote":
                    text = "Change your default quote?"
                case "default_timers_based_on_round_average":
                    text = f"Use your average round and break duration instead of the default? ({config.default_round}, {config.default_break})?"
                case "change_default_timers":
                    text = f"Change your default timers length? Current: ({config.default_round}, {config.default_break})?"
                case _:
                    text = f"Please provide a value for: {operation}."

            print(text)
            bool_value = string_to_boolean(input())
            file.write(f"{operation}={bool_value};\n")

def set_default_config():
    flag = False
    with open('config/config.config', 'r') as file:
        if len(file.read()) <= 0:
            flag = True

    # config file is empty, override with default
    if flag:
        with open('config/config.config', 'w') as file:
            file.write("update_config=True;\ncreate_actions=False;\nload_new_quote=False;\ninstant_start_timers=False;\nchange_default_quote=False;\ndefault_timers_based_on_session_average=False;\nchange_default_length=False;")

# break actions
def create_actions():
    with open('config/actions.config', 'w') as file:
        print("Creating actions... (exit, quit, q, e)")
        user_input = ""

        while user_input != "exit" and user_input != "quit" and user_input != "q" and user_input != "e":
            print("New Action: ")
            user_input = input()
            file.write(user_input + ";")

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

# quotes
def load_default_quote():
    with open('config/default_quote.config', 'r') as file:
        return file.read()

def change_default_quote():
    with open('config/default_quote.config', 'w') as file:
        print("insert the new default quote:")
        user_input = input()
        file.write(user_input)
        default_quote = user_input
    return default_quote

# break and round duration
def load_default_lengths():
    with open('config/default_length.config', 'r') as file:
        read = file.read().split(",")
        default_round = float(read[0])
        default_break = float(read[1])
    return default_round, default_break

def change_default_lengths():
    default_round = 25
    default_break = 5
    with open('config/default_length.config', 'w') as file:
        flag = True
        while (flag):
            print("Round Length:")
            round_time = input()
            print("Break Length:")
            break_time = input()
            try:
                round_time = float(round_time)
                break_time = float(break_time)
                file.write(f"{round_time},{break_time}")
                default_round = round_time
                default_break = break_time
                flag = False
            except:
                print("\n...length should be a number...\n")
    return default_round, default_break

def save_average_duration_over_time(session_rounds, session_breaks,):
    if session_rounds[0] != 0 and session_rounds[0] != 0:
        with open('config/average_ratio.config', 'a') as file:
            # average round length, amount of rounds, average break length, amount of breaks
            file.write(f"{session_rounds[0]},{session_rounds[1]},{session_breaks[0]},{session_breaks[1]};")

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
    with open('config/average_ratio.config', 'r') as file:
        for line in file.read().split(";"):
            if line != "" and line != "\n":
                round_sum += float(line.split(",")[0]) * float(line.split(",")[1])
                round_count += float(line.split(",")[1])

                break_sum += float(line.split(",")[2]) * float(line.split(",")[3])
                break_count += float(line.split(",")[3])

    if round_count != 0 and break_count != 0:
        average_round = round_sum / round_count
        average_break = break_sum / break_count

        return average_round, average_break
    return 0,0
