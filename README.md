# CS101: Movie Ticket Booking System

A terminal-driven movie booking platform written in Python that allows users to:
* **View movie details.** *Movies in theatre database are printed for user selection.*
* **View current theatre schedule.** *Includes optional search by date or title.*
* **Book tickets.** *A seat map is rendered for convenience. Discounts are handled automatically.*
* **View and cancel current bookings.** *Cancellations must abide by theatre policy.*
* **Resume interrupted booking.** *Customers who quit the booking process can resume it if their seats are still reserved.*
* **Add or remove movies.** *Staff only. Removed movies will have their showings removed as well.*
* **Update theatre schedule.** *Staff only. Automatically checks for conflicts.*
* **View and export analytics.** *Staff only.*
* **Create manual backups of database.** *Staff only.*


## Setup

**Written for Python 3.12**  
Clone the repository and run `main.py` using Python using a terminal.  
The script will generate required subdirectories and json files within its current working directory.

The theater name and the admin password are both defined within `main.py` (at the top) and can be changed. Admin password is `123` by default.

*Note:* If you edit the json files manually, make sure they aren't completely blank and include at least a pair of square brackets (`[]`).




## Usage

### Example booking flow:

#### New Booking: 
<img width="296" height="274" alt="image" src="https://github.com/user-attachments/assets/5f6887ab-893e-48c4-ba17-c4ea2a559187" />

Enter the *Customer Menu* and select *New Booking*.  
 * You will be prompted to select showtime, select seats, and enter personal info.
 * You will be prompted for payment. If successful, your booking will finalize and a booking ID will be generated.
 * If your payment is not successful (and your selected seats are still reserved) you will be given a code so you can continue booking later.

#### Cancel Booking: 
<img width="471" height="177" alt="image" src="https://github.com/user-attachments/assets/c7d3f3cc-66be-4951-b066-594689e70269" />

In the *Customer Menu*, select *Refund Booking*.

* You will be prompted for your booking ID.
* A refund will be provided if you're eligible according to theater policy.

## Code Details

The applet revolves around the management of three classes; **Movie**, **Showtime**, **Booking**.  
Objects are serialised into a dictionary, which is how they're written to .json for data persistence.  
*Reserved seats* are handled through **Booking** objects which have their `confirmed` attribute set to `False`.

Menu options are handled by a fourth class called **MenuSelector**.  
**MenuSelector** objects contain the prompt & options for a given menu. The `.run()` method will print these and make user select a valid option (using integer inputs).  
`.run()` automatically splits options into multiple pages for when there are more than 10 options, although this seldom happens in practice.  
The key value of the selected option is returned by the method.  

Menu logic is handled with match-case statements (contained in respective `..._menu()` functions), wherein the returned key is matched to the appropriate logic.
