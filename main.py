import movies
# import seating
# import bookings
# import storage
# import reports

# Database path
data_path = "./data/"

# Actions for menus
main_actions = { 
    "0": {"value": "admins", "description": "Staff actions"},
    "1": {"value": "schedule", "description": "View Showtime Schedule"},
    "2": {"value": "bookings", "description": "Book viewing"},
    "3": {"value": "unbook", "description": "Cancel booking"}
    }
schedule_actions = { 
    "0": {"value": "back", "description": "[Go back]"},
    "1": {"value": "name", "description": "Showtimes of a specific movie"},
    "2": {"value": "date", "description": "All movies on a specific day"},
    "3": {"value": "all", "description": "All movies"}
    }


# Functions for menu navigation and providing user with information
def print_actions(possible_actions: dict) -> None:
    """Prints possible actions user can take."""
    for key, value in possible_actions.items():
        print(key,value["description"])
        
def make_user_pick_action(possible_actions: dict) -> str:
    """Prompts user to pick an action, returns 'invalid' if not valid."""
    result = possible_actions.get(input("Enter a number: "),"invalid")
    if result == "invalid":
        return result
    return result["value"]

def do_menu(user_prompt: str,menu_actions: dict) -> str:
    """Shows a menu with given prompt & actions, asks user to pick action."""
    print(user_prompt)
    print_actions(menu_actions)
    user_choice = make_user_pick_action(menu_actions)
    return user_choice
    
    
# Run stuff
while True:
    user_action = do_menu("What would you like to do?", main_actions)
    
    if user_action == "invalid":
        print("Invalid selection.\n")
        continue
        
    elif user_action == "schedule":
        user_action = do_menu("\nWhich showtimes would you like to see?", schedule_actions)
        if user_action == "back":
            continue
        if user_action == "all":
            user_want = None
        else:
            user_want = input(f"Enter {user_action}: ")
        result = movies.list_showtimes(data_path,user_action,user_want)
        for item in result:
            print(item)
        input("\nEnter to continue")
        continue
        
    elif user_action == "booking":
        pass
    elif user_action == "unbooking":
        pass
    elif user_action == "admin":
        pass
    else:
        pass
            
