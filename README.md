# CS101: Movie Ticket Booking System

A terminal-driven movie booking platform written in Python.
* **View current theatre schedule.** *Optionally search by date or title.*
* **Book tickets.** *A seat map is rendered for convenience. Discounts are handled automatically.*
* **View and cancel current bookings.** *Cancellations must abide by theatre policy.*  
* **Add or retire movies.** *Staff only.*
* **Update theatre schedule.** *Staff only.*
* **View and export analytics.** *Staff only.*
* **Create manual backups of database.** *Staff only.*


## Setup

**Written for Python 3.12**  
Clone via `git clone`. Run via `python main.py` in main directory. This project doesn't require any external libraries,
so a virtual environment is not necessary.

Most of the configuration, including the password for the admin menu, is stored within the first few lines of `main.py`.
 The password is `123` by default.

Upon launching, script will automatically create required paths and json files within its current directory.   
*Note:* If you edit the json files manually, make sure they aren't completely blank and include at least a pair of square brackets (`[]`).




## Usage

### Example booking flow:

**Booking:** Upon launching the script, press **1** to access the customer menu. Then, press **3** to start the booking process.  
You will be prompted to pick a showing, followed by a prompt to select seats. Next you will be prompted for personal details.  
After entering your personal info, the cost of your ticket will be shown to you, and you'll be asked to pay. If you fail to
pay at this time, and your seats are still reserved, you will be given a code to continue the booking process at a later time.
 Make sure you do this before your reservation expires.  
Once you pay, you'll be provided with a ticket ID. Make absolutely sure that you save this for later.

**Refund:** To get a refund, you must select option **5** within the customer menu. Once you provide your booking ID,
the system will issue a refund if it's allowed by theater policy; otherwise, you'll be told why a refund is not possible at this time.

## Code Details

The applet revolves around the management of three classes; **Movie**, **Showtime**, **Booking**.  
Objects of these class can be serialised into a dictionary, which is how they're written to .json for data persistence.

The menus are handled by a fourth class, the **MenuSelector**. Using the `run()` method on objects of this class will print
 out the prompt and the available options for a given menu, and make user select one of the options. The options are single 
key-value dictionaries. The value is what gets printed on the screen, and the key is what's actually selected.  
For most menus, a match-case is used to match the returned key value to its appropriate logic.

Seat reservation is handled through a Booking object which has it's `confirmed` attribute to false. These bookings are deleted 
when expired.