import movies
import seating
import bookings
# import storage
# import reports

# To-do: Prettier print for viewing schedule. Verify date formats (storage.py?).

# Database path
data_path = "./data/"

# Menu definitions
# "": {"value": "", "description": ""},
main_menu = { 
    "prompt": "What would you like to do?",
    "actions": {
        "0": {"value": "admins", "description": "[Staff Access]"},
        "1": {"value": "schedule", "description": "View scheduled showtimes"},
        "2": {"value": "book", "description": "Book a ticket"},
        "3": {"value": "see_bookings", "description": "View current bookings"},
        "4": {"value": "unbook", "description": "Cancel booking"}
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

admin_main = {
    "prompt": "Select sub-menu:",
    "actions": {
        "0": {"value": "back", "description": "[Exit Admin Mode]"},
        "1": {"value": "movies", "description": "Manage movies & showtimes"}, # Another menu
        "2": {"value": "reports", "description": "Manage analytics"}, # Another menu
        "3": {"value": "backups", "description": "Manage database backups"} # Another menu
        }
    }

admin_movies = {
    "prompt": "Manage movies:",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "new_movie", "description": "Add a new movie"}, # Add to movie list. Ask if new schedule should be made.
        "2": {"value": "rem_movie", "description": "Retire a movie"}, # Remove from movie list. Should also remove it from schedule.
        "3": {"value": "new_schedule", "description": "Add new showtime to schedule"},
        "4": {"value": "rem_schedule", "description": "Remove a showing from schedule"}
        }
    }

admin_reports = {
    "prompt": "View and manage analytics:",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "export", "description": "Export all analytics to file"}, # export_report()
        "2": {"value": "occupancy", "description": "View occupancy statistics"}, # occupancy_report()
        "3": {"value": "revenue", "description": "View revenue summary"}, # revenue_summary()
        "4": {"value": "top_movies", "description": "View the most popular 5 movies"} # top_movies()
        }
    }
   
# Menu Display Functions
def do_menu(menu_data: dict) -> str:
    """Lists possible actions with an optional starting prompt. User must pick an action."""
    print("\n"+menu_data["prompt"])
    print_actions(menu_data["actions"])
    return make_user_pick_action(menu_data["actions"])
    
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
    for showing in movies.list_showtimes(data_path,input_action,search_for):
        print(showing)
    input("\n[Enter to continue] ")

def admin_logic(input_action):
    while True:
        match input_action:
            case "back":
                return
            case "movies":
                continue
            case "reports":
                continue
            case "backups":
                continue

# def admin_movies_logic(input_action):
# def admin_reports_logic(input_action):
# def admin_backups_logic(input_action):
    
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
        case "book":
            # bookings.create_booking()
            continue
        case "see_bookings":
            # list_customer_bookings()
            continue
        case "unbooking":
            # bookings.cancel_booking()
            continue
        case "admin":
            user_action = do_menu(admin_main)
            admin_logic(user_action)
            continue
        case _:
            raise ValueError("Not a recognised action.")
            
