import movies
# import seating
# import bookings
# import storage
# import reports

# Database path
data_path = "./data/"

# Menu definitions
main_menu = { 
    "prompt": "What would you like to do?",
    "actions": {
        "0": {"value": "admins", "description": "Staff actions"},
        "1": {"value": "schedule", "description": "View Showtime Schedule"},
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

   
# Functions for menu navigation and providing user with information
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
    
    
# Run stuff
while True:
    user_action = do_menu(main_menu)
    
    if user_action == "invalid":
        print("Invalid selection.")
        continue
        
    elif user_action == "schedule":
        user_action = do_menu(schedule_menu)
        if user_action == "back":
            continue
        elif user_action == "all":
            showtimes = movies.list_showtimes(data_path,user_action)
        elif user_action == ("date" or "name"):
            showtimes = movies.list_showtimes(data_path,user_action,input(f"Enter {user_action}: "))
        for showtime in showtimes:
            print(showtime)
        input("\n[Enter to continue] ")
        continue
        
    elif user_action == "booking":
        pass
    elif user_action == "unbooking":
        pass
    elif user_action == "admin":
        pass
    else:
        pass
            
