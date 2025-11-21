import movies
import seating
import bookings
import storage
import reports


# Actions for menus
main_actions = { 
    "0": {"value": "admins", "description": "Staff actions"},
    "1": {"value": "schedule", "description": "View Showtime Schedule"},
    "2": {"value": "bookings", "description": "Book viewing"},
    "3": {"value": "unbook", "description": "Cancel booking"}
    }


# Functions for menu navigation and providing user with information
def print_actions(possible_actions: dict) -> None:
    """Prints possible actions user can take."""
    for key, value in possible_actions.items():
        print(key,value["description"])
    
def make_user_pick_action(possible_actions: dict) -> str:
    """Prompts user to pick an action, returns 'invalid' if not valid."""
    return possible_actions.get(input("Enter a number: "),"invalid")

def do_menu(user_prompt,menu_actions):
    print(user_prompt)
    print_actions(menu_actions)
    user_action = make_user_pick_action(menu_actions)
    return user_action
    
    
while True:
    user_choice = do_menu("What would you like to do?", main_actions)
    match user_choice:
        case "invalid":
            print("Invalid selection.\n")
            continue
        case "schedule":
            pass
        case "booking":
            pass
        case "unbooking":
            pass
        case "admin":
            pass
        case _:
            pass
            
