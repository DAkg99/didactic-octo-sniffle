
def print_actions(possible_actions: dict) -> None:
    """Prints possible actions user can take"""
    for key, value in possible_actions.items():
        print(key,value["description"])
    
def make_user_pick_action(possible_actions: dict) -> str:
    return possible_actions.get(input("Enter a number: "),"invalid")


actions = { 
    "0": {"value": "admins", "description": "Staff actions"},
    "1": {"value": "schedule", "description": "View Showtime Schedule"},
    "2": {"value": "bookings", "description": "Book viewing"},
    "3": {"value": "unbook", "description": "Cancel booking"}
    }

while True:
    print("What would you like to do?")
    print_actions(actions)
    user_action = make_user_pick_action(actions)
    
    match user_action:
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