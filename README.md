# 🎬 Movie Ticket Booking System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20MacOS-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/CLI-Application-orange" alt="CLI">
</p>

A feature-rich Movie Ticket Booking System written in Python, supporting both user and admin functionalities. This project is designed for the command-line and is ideal for learning, demos, or as a base for further development.

## Features

### 🧑‍💼 User Features
- Browse available movies
- View showtimes for each movie
- Book seats with a visual seat map
- Cancel bookings
- View your booking history and loyalty points

### 👩‍💼 Admin Features
- All user features, plus:
- Add new movies
- Remove movies
- Add showtimes to movies
- Remove showtimes
- View all bookings in the system

## Demo Accounts
- **Admin:**
  - Username: `admin`
  - Password: `12345`
- **User:**
  - Username: `sudip`
  - No password required

## Screenshots

<p align="center">
  <img src="screenshots/main_menu.png" alt="Main Menu" width="600">
  <br>
  <img src="screenshots/browse_movies.png" alt="Browse Movies" width="600">
  <br>
  <img src="screenshots/seat_map.png" alt="Seat Map" width="600">
</p>

> _Add your own screenshots in the `screenshots/` folder for best results._

## How to Run

1. **Clone the repository or download the script.**
2. Make sure you have Python 3.7+ installed.
3. Open a terminal and navigate to the project directory.
4. Run the script:
   ```bash
   python "Movie_Ticket_Booking system.py"
   ```
5. Follow the on-screen menu to login, register, or use the system.

## Data Persistence
- All data (movies, users, bookings) is stored in a local JSON file (`movie_system_data.json`).
- On first run, the system initializes with sample movies and demo accounts.

## Fun Extras
- 🎲 Lucky Draw: Random chance to win a popcorn coupon when booking!
- 🍿 Easter Egg: Type `popcorn` at any menu for a surprise.
- 💡 Fun facts about movies are shown when browsing.

## Code Structure
- `Movie`, `ShowTime`, `Booking`, `User`: Core data classes
- `MovieBookingSystem`: Main logic and data management
- `main()`: Command-line interface and menu system

## Requirements
- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## License
This project is licensed under the MIT License.

---

**Enjoy booking your movie tickets!** 🍿
