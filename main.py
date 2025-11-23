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
main_menu_data = { 
    "prompt": "What would you like to do?",
    "actions": {
        "0": {"value": "admin", "description": "[Staff Access]"},
        "1": {"value": "schedule", "description": "View scheduled showtimes"},
        "2": {"value": "book", "description": "Book a ticket"},
        "3": {"value": "see_bookings", "description": "View current bookings"},
        "4": {"value": "unbook", "description": "Cancel booking"}
        }
    }
    
schedule_menu_data = {
    "prompt": "Which showtimes would you like to see?",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "name", "description": "Showtimes of a specific movie"},
        "2": {"value": "date", "description": "All movies on a specific day"},
        "3": {"value": "all", "description": "All movies"}
        }
    }

admin_main_data = {
    "prompt": "Select sub-menu:",
    "actions": {
        "0": {"value": "back", "description": "[Exit Admin Mode]"},
        "1": {"value": "movies", "description": "Manage movies & showtimes"}, # Another menu
        "2": {"value": "reports", "description": "Manage analytics"}, # Another menu
        "3": {"value": "backups", "description": "Manage database backups"} # Another menu
        }
    }

admin_movies_data = {
    "prompt": "Manage movies and showtimes:",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "new_movie", "description": "Add a new movie"}, # Add to movie list. Ask if new schedule should be made.
        "2": {"value": "rem_movie", "description": "Retire a movie"}, # Remove from movie list. Should also remove it from schedule.
        "3": {"value": "new_showing", "description": "Add new showing to schedule"},
        "4": {"value": "rem_showing", "description": "Remove a showing from schedule"}
        }
    }

admin_reports_data = {
    "prompt": "View or export analytics:",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "export", "description": "Export all analytics to file"}, # reports.export_report()
        "2": {"value": "occupancy", "description": "View occupancy statistics"}, # reports.occupancy_report()
        "3": {"value": "revenue", "description": "View revenue summary"}, # reports.revenue_summary()
        "4": {"value": "top_movies", "description": "View the most popular 5 movies"} # reports.top_movies()
        }
    }

admin_backups_data = {
    "prompt": "Manage backups:",
    "actions": {
        "0": {"value": "back", "description": "[Go back]"},
        "1": {"value": "save_backup", "description": "Create a manual backup of data"} # storage.backup_state()
        # "2": {"value": "", "description": ""},
        # "3": {"value": "", "description": ""},
        # "4": {"value": "", "description": ""} 
        }
    }
        
   
### Menu Display Functions
def show_menu(menu_data: dict) -> str:
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

  
### Menus
def schedule_menu():
    """Menu to view and search the showtime schedule"""
    while True:
        menu_action = show_menu(schedule_menu_data)
        match menu_action: 
            case "back":
                return
            case "all":
                [print(showing) for showing in movies.list_showtimes(data_path, menu_action)]
                input("\n[Enter to continue] ")
            case "date" | "name":
                print("Date format: YYYY-MM-DD\n" * (menu_action == "date"), end="")
                search_for = input(f"Enter {menu_action}: ")
                [print(showing) for showing in movies.list_showtimes(data_path, menu_action, search_for)]
                input("\n[Enter to continue] ")
            case _:
                print("Not a recognised action.")

def admin_menu():
    """Admin main menu (directory of sub-menus)"""
    while True:
        menu_action = show_menu(admin_main_data)
        match menu_action:
            case "back":
                return
            case "movies":
                admin_movies_menu()
            case "reports":
                admin_reports_menu()
            case "backups":
                admin_backups_menu()
            case _:
                print("Invalid selection.")
                
def admin_movies_menu():
    """Admin menu to manage movies and showings"""
    while True:
        menu_action = show_menu(admin_movies_data)
        match menu_action:
            case "back":
                return
            case "new_movie":
                # movies.add_movie(...)
                print("[Placeholder]")
                input("Enter movie to add: ")
                input("Schedule viewings right away? (y/n) ")
                print("Movie has been added")
                input("[Enter to continue] ")
            case "rem_movie":
                # movies.removie_movie(...)
                print("[Placeholder]")
                print("Scheduled viewings for this movie will also be removed")
                input("Enter movie to retire: ")
                print("Movie has been retired")
                input("[Enter to continue] ")
            case "new_showing":
                # movies.schedule_showtime(...) 
                print("[Placeholder]")
                movies.list_showtimes(data_path,"all",None)
                input("Enter showtime to add: ") # This will require a series of inputs
                print("New showtime has been added to schedule")
                input("[Enter to continue] ")
            case "rem_showing":
                # movies.update_showtime
                print("[Placeholder]")
                movies.list_showtimes(data_path,"all",None)
                input("Enter showtime to remove: ") # This will require a series of inputs
                print("Showtime has been removed from schedule")
                input("[Enter to continue] ")
            case _:
                print("Not a recognised action.")
           
def admin_reports_menu():
    """Admin menu to view and export analytics"""
    while True:
        menu_action = show_menu(admin_reports_data)
        match menu_action:
            case "back":
                return
            case "export":
                # reports.export_report(...)
                print("[Placeholder]")
                print("Data exported to /path/file.json")
                input("[Enter to continue] ")
            case "occupancy":
                # reports.occupancy_report(...)
                print("[Placeholder]")
                print("Theatre is 100% booked")
                input("[Enter to continue] ")
            case "revenue":
                # reports.revenue_summary(...)
                print("[Placeholder]")
                print("Theatre has made 1 brouzouf")
                input("[Enter to continue] ")
            case "top_movies":
                # reports.top_movies(...)
                print("[Placeholder]")
                print(f"Most popular movie is {movies.load_movies(data_path)[0]}")
                input("[Enter to continue] ")
            case _:
                print("Not a recognised action.")
     
def admin_backups_menu():
    """Admin menu to export backups"""
    while True:
        menu_action = show_menu(admin_backups_data)
        match menu_action:
            case "back":
                return
            case "save_backup":
                # storage.backup_state(...)
                print("[Placeholder]")
                print("Backup saved to /path/file.json")
            case _:
                print("Not a recognised action.")
        input("[Enter to continue] ")
        
        
# Main menu
while True:
    user_action = show_menu(main_menu_data)
    match user_action: 
        case "schedule":
            schedule_menu()
        case "book":
            # bookings.create_booking()
            input("To do")
        case "see_bookings":
            # list_customer_bookings()
            input("To do")
        case "unbook":
            # bookings.cancel_booking()
            input("To do")
        case "admin":
            admin_menu()
        case _:
            print("Not a recognised action.")
