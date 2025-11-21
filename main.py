import movies
import seating
import bookings
# import storage
# import reports

# To-do: Prettier print for viewing schedule. Verify date formats (storage.py?).

# Database path
data_path = "./data/"

# Menu definitions
main_menu = { 
    "prompt": "What would you like to do?",
    "actions": {
        "0": {"value": "admins", "description": "Staff actions"},
        "1": {"value": "schedule", "description": "View scheduled showtimes"},
        "2": {"value": "bookings", "description": "Book viewing"},
        "3": {"value": "unbook", "description": "Cancel booking"}
        }
    }
    
schedule_menu = {
    "prompt": "Which showtimes would you like to see?",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "name", "description": "Showtimes of a specific movie"},
        "2": {"value": "date", "description": "All movies on a specific day"},
        "3": {"value": "all", "description": "All movies"}
        }
    }
    

   
# Menu Display Functions
def print_actions(possible_actions: dict) -> None:
    """Prints possible actions user can take."""
    for key, value in possible_actions.items():
        print(key,value["description"])
        
def make_user_pick_action(possible_actions: dict) -> str:
    """Prompts user to pick an action, returns 'invalid' if not valid."""
    result = possible_actions.get(input("\nEnter a number: "),"invalid")
    if result == "invalid":
        return result
    return result["value"]

def do_menu(menu_data: dict) -> str:
    """Lists possible actions with an optional starting prompt. User must pick an action."""
    print("\n"+menu_data["prompt"])
    print_actions(menu_data["actions"])
    return make_user_pick_action(menu_data["actions"])
  
# Menu Logic Functions  
def schedule_logic(input_action):
    match input_action: 
        case "back":
            return
        case "all":
            search_for = None
        case "date" | "time":
            print("Date format: YYYY-MM-DD\n" * (input_action == "date"), end="")
            search_for = input(f"Enter {input_action}: ")
        case _:
            raise ValueError("Not a recognised action.")
    for showtime in movies.list_showtimes(data_path,input_action,search_for):
        print(showtime)
    input("\n[Enter to continue] ")
    

    
# Run stuff
while True:
    user_action = do_menu(main_menu)
    match user_action: 
        case "invalid":
            print("Invalid selection.")
            continue
        case "schedule":
            user_action = do_menu(schedule_menu)
            schedule_logic()
            continue
        case "booking":
            #bookings.create_booking()
            continue
        case "unbooking":
            #bookings.cancel_booking()
            pass
        case "admin":
            pass
        case _:
            raise ValueError("Not a recognised action.")
            
