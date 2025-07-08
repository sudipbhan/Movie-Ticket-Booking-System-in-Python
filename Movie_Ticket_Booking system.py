
"""
Movie Ticket Booking System in Python, featuring both:

🧑‍💼 User Features:
    - Browse available movies
    - View showtimes
    - Book seats
    - Cancel bookings

👩‍💼 Admin Features:
    -All User's Features +
    - Add/remove movies
    - Manage showtimes
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class Movie:
    """Represents a movie with its details."""
    
    def __init__(self, movie_id: str, title: str, genre: str, duration: int, 
                 rating: str, description: str = "", price: float = 12.50):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre
        self.duration = duration  # in minutes
        self.rating = rating
        self.description = description
        self.price = price
        self.showtimes = []  # List of ShowTime objects
    
    def to_dict(self) -> Dict:
        """Convert movie to dictionary for JSON serialization."""
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'genre': self.genre,
            'duration': self.duration,
            'rating': self.rating,
            'description': self.description,
            'price': self.price,
            'showtimes': [st.to_dict() for st in self.showtimes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Movie':
        """Create movie from dictionary."""
        movie = cls(
            data['movie_id'], data['title'], data['genre'],
            data['duration'], data['rating'], data.get('description', ''),
            data.get('price', 12.50)
        )
        movie.showtimes = [ShowTime.from_dict(st) for st in data.get('showtimes', [])]
        return movie

class ShowTime:
    """Represents a movie showtime with seating arrangement."""
    
    def __init__(self, showtime_id: str, movie_id: str, date: str, time: str, 
                 theater: str, total_seats: int = 50):
        self.showtime_id = showtime_id
        self.movie_id = movie_id
        self.date = date
        self.time = time
        self.theater = theater
        self.total_seats = total_seats
        self.booked_seats = set()  # Set of booked seat numbers
    
    def get_available_seats(self) -> List[int]:
        """Get list of available seat numbers."""
        return [i for i in range(1, self.total_seats + 1) if i not in self.booked_seats]
    
    def book_seats(self, seat_numbers: List[int]) -> bool:
        """Book specified seats if available."""
        if all(seat in self.get_available_seats() for seat in seat_numbers):
            self.booked_seats.update(seat_numbers)
            return True
        return False
    
    def cancel_seats(self, seat_numbers: List[int]) -> bool:
        """Cancel booking for specified seats."""
        if all(seat in self.booked_seats for seat in seat_numbers):
            self.booked_seats.difference_update(seat_numbers)
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convert showtime to dictionary for JSON serialization."""
        return {
            'showtime_id': self.showtime_id,
            'movie_id': self.movie_id,
            'date': self.date,
            'time': self.time,
            'theater': self.theater,
            'total_seats': self.total_seats,
            'booked_seats': list(self.booked_seats)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ShowTime':
        """Create showtime from dictionary."""
        showtime = cls(
            data['showtime_id'], data['movie_id'], data['date'],
            data['time'], data['theater'], data.get('total_seats', 50)
        )
        showtime.booked_seats = set(data.get('booked_seats', []))
        return showtime

class Booking:
    """Represents a ticket booking."""
    
    def __init__(self, booking_id: str, user_id: str, movie_title: str, 
                 showtime_id: str, seat_numbers: List[int], total_amount: float):
        self.booking_id = booking_id
        self.user_id = user_id
        self.movie_title = movie_title
        self.showtime_id = showtime_id
        self.seat_numbers = seat_numbers
        self.total_amount = total_amount
        self.booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "Confirmed"
    
    def to_dict(self) -> Dict:
        """Convert booking to dictionary for JSON serialization."""
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'movie_title': self.movie_title,
            'showtime_id': self.showtime_id,
            'seat_numbers': self.seat_numbers,
            'total_amount': self.total_amount,
            'booking_date': self.booking_date,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Booking':
        """Create booking from dictionary."""
        booking = cls(
            data['booking_id'], data['user_id'], data['movie_title'],
            data['showtime_id'], data['seat_numbers'], data['total_amount']
        )
        booking.booking_date = data.get('booking_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        booking.status = data.get('status', 'Confirmed')
        return booking

class User:
    """Represents a system user."""
    
    def __init__(self, user_id: str, username: str, email: str, is_admin: bool = False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.bookings = []  # List of booking IDs
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'bookings': self.bookings
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary."""
        user = cls(data['user_id'], data['username'], data['email'], data.get('is_admin', False))
        user.bookings = data.get('bookings', [])
        return user

class MovieBookingSystem:
    """Main system class that manages all operations."""
    
    def __init__(self, data_file: str = "movie_system_data.json"):
        self.data_file = data_file
        self.movies = {}  # movie_id -> Movie
        self.users = {}   # user_id -> User
        self.bookings = {}  # booking_id -> Booking
        self.current_user = None
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load movies
                for movie_data in data.get('movies', []):
                    movie = Movie.from_dict(movie_data)
                    self.movies[movie.movie_id] = movie
                
                # Load users
                for user_data in data.get('users', []):
                    user = User.from_dict(user_data)
                    self.users[user.user_id] = user
                
                # Load bookings
                for booking_data in data.get('bookings', []):
                    booking = Booking.from_dict(booking_data)
                    self.bookings[booking.booking_id] = booking
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}. Starting with fresh data.")
                self._initialize_sample_data()
        else:
            self._initialize_sample_data()
    
    def save_data(self):
        """Save data to JSON file."""
        data = {
            'movies': [movie.to_dict() for movie in self.movies.values()],
            'users': [user.to_dict() for user in self.users.values()],
            'bookings': [booking.to_dict() for booking in self.bookings.values()]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_sample_data(self):
        """Initialize system with sample data."""
        # Create sample admin user
        admin_user = User("admin_001", "admin", "admin@cinema.com", True)
        self.users[admin_user.user_id] = admin_user
        
        # Create sample regular user

        regular_user = User("user_001", "SUDIP", "sudip@email.com", False)
        self.users[regular_user.user_id] = regular_user
        
        # Create sample movies with showtimes
        sample_movies = [
            {
                'title': 'Avengers: Endgame',
                'genre': 'Action/Adventure',
                'duration': 181,
                'rating': 'PG-13',
                'description': 'The Avengers assemble once more to reverse Thanos\' actions.',
                'price': 15.00
            },
            {
                'title': 'The Dark Knight',
                'genre': 'Action/Crime',
                'duration': 152,
                'rating': 'PG-13',
                'description': 'Batman faces the Joker in this epic crime thriller.',
                'price': 12.50
            },
            {
                'title': 'Inception',
                'genre': 'Sci-Fi/Thriller',
                'duration': 148,
                'rating': 'PG-13',
                'description': 'A thief who steals secrets through dream-sharing technology.',
                'price': 13.00
            },
            {
                'title': 'Parasite',
                'genre': 'Thriller/Drama',
                'duration': 132,
                'rating': 'R',
                'description': 'A poor family schemes to become employed by a wealthy family.',
                'price': 11.50
            }
        ]
        
        theaters = ["Theater A", "Theater B", "Theater C"]
        times = ["10:00", "13:30", "16:00", "19:30", "22:00"]
        
        for i, movie_data in enumerate(sample_movies):
            movie_id = f"movie_{i+1:03d}"
            movie = Movie(movie_id, **movie_data)
            
            # Add showtimes for next 3 days
            for day in range(3):
                date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
                for j, time in enumerate(times[:3]):  # 3 showtimes per day
                    showtime_id = f"show_{movie_id}_{day}_{j}"
                    theater = theaters[j % len(theaters)]
                    
                    showtime = ShowTime(
                        showtime_id, movie_id, date, time, theater, 50
                    )
                    movie.showtimes.append(showtime)
            
            self.movies[movie_id] = movie
        
        self.save_data()
    
    def login(self, username: str) -> bool:
        """Login user by username."""
        for user in self.users.values():
            if user.username == username:
                self.current_user = user
                return True
        return False
    
    def logout(self):
        """Logout current user."""
        self.current_user = None
    
    def register_user(self, username: str, email: str) -> bool:
        """Register a new user."""
        # Check if username already exists
        for user in self.users.values():
            if user.username == username:
                return False
        
        user_id = f"user_{len(self.users)+1:03d}"
        user = User(user_id, username, email)
        self.users[user_id] = user
        self.save_data()
        return True
    
    # User Methods
    def browse_movies(self) -> List[Movie]:
        """Get all available movies."""
        return list(self.movies.values())
    
    def get_movie_showtimes(self, movie_id: str) -> List[ShowTime]:
        """Get all showtimes for a specific movie."""
        if movie_id in self.movies:
            return self.movies[movie_id].showtimes
        return []
    
    def book_tickets(self, showtime_id: str, seat_numbers: List[int]) -> Optional[str]:
        """Book tickets for a showtime."""
        if not self.current_user:
            return None
        
        # Find the showtime and movie
        showtime = None
        movie = None
        for m in self.movies.values():
            for st in m.showtimes:
                if st.showtime_id == showtime_id:
                    showtime = st
                    movie = m
                    break
            if showtime:
                break
        
        if not showtime or not movie:
            return None
        
        # Check if seats are available and book them
        if showtime.book_seats(seat_numbers):
            booking_id = str(uuid.uuid4())[:8]  # Short ID for display
            total_amount = len(seat_numbers) * movie.price
            
            booking = Booking(
                booking_id, self.current_user.user_id, movie.title,
                showtime_id, seat_numbers, total_amount
            )
            
            self.bookings[booking_id] = booking
            self.current_user.bookings.append(booking_id)
            self.save_data()
            
            return booking_id
        
        return None
    
    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking."""
        if booking_id not in self.bookings:
            return False
        
        booking = self.bookings[booking_id]
        
        # Check if user owns this booking or is admin
        if (self.current_user and 
            booking.user_id != self.current_user.user_id and 
            not self.current_user.is_admin):
            return False
        
        # Find and cancel seats in showtime
        for movie in self.movies.values():
            for showtime in movie.showtimes:
                if showtime.showtime_id == booking.showtime_id:
                    if showtime.cancel_seats(booking.seat_numbers):
                        booking.status = "Cancelled"
                        self.save_data()
                        return True
        
        return False
    
    def get_user_bookings(self) -> List[Booking]:
        """Get all bookings for current user."""
        if not self.current_user:
            return []
        
        return [self.bookings[booking_id] for booking_id in self.current_user.bookings 
                if booking_id in self.bookings]
    
    # Admin Methods
    def add_movie(self, title: str, genre: str, duration: int, rating: str, 
                  description: str = "", price: float = 12.50) -> Optional[str]:
        """Add a new movie (admin only)."""
        if not self.current_user or not self.current_user.is_admin:
            return None
        
        movie_id = f"movie_{len(self.movies)+1:03d}"
        movie = Movie(movie_id, title, genre, duration, rating, description, price)
        self.movies[movie_id] = movie
        self.save_data()
        return movie_id
    
    def remove_movie(self, movie_id: str) -> bool:
        """Remove a movie (admin only)."""
        if not self.current_user or not self.current_user.is_admin:
            return False
        
        if movie_id in self.movies:
            del self.movies[movie_id]
            self.save_data()
            return True
        return False
    
    def add_showtime(self, movie_id: str, date: str, time: str, theater: str, 
                     total_seats: int = 50) -> Optional[str]:
        """Add a new showtime (admin only)."""
        if not self.current_user or not self.current_user.is_admin:
            return None
        
        if movie_id not in self.movies:
            return None
        
        showtime_id = f"show_{movie_id}_{len(self.movies[movie_id].showtimes)+1:03d}"
        showtime = ShowTime(showtime_id, movie_id, date, time, theater, total_seats)
        self.movies[movie_id].showtimes.append(showtime)
        self.save_data()
        return showtime_id
    
    def remove_showtime(self, showtime_id: str) -> bool:
        """Remove a showtime (admin only)."""
        if not self.current_user or not self.current_user.is_admin:
            return False
        
        for movie in self.movies.values():
            for i, showtime in enumerate(movie.showtimes):
                if showtime.showtime_id == showtime_id:
                    del movie.showtimes[i]
                    self.save_data()
                    return True
        return False
    
    def get_all_bookings(self) -> List[Booking]:
        """Get all bookings (admin only)."""
        if not self.current_user or not self.current_user.is_admin:
            return []
        
        return list(self.bookings.values())


def wait_for_user():
    """Wait for user to press Enter before continuing."""
    input("\n🔄 Press Enter to return to menu...")

def main():
    """Main application entry point."""
    system = MovieBookingSystem()
    
    def print_header():
        print("\n" + "="*60)
        print("🎬 MOVIE TICKET BOOKING SYSTEM 🎬")
        print("="*60)
        print(r"""
   ____  __  __  ____  _   _  ___  ____     _   _  _   _  ____  _  __
  |  _ \|  \/  |/ ___|| | | |/ _ \|  _ \   | | | || | | |/ ___|| |/ /
  | | | | |\/| | |  _ | |_| | | | | |_) |  | |_| || |_| | |  _ | ' / 
  | |_| | |  | | |_| ||  _  | |_| |  _ <   |  _  ||  _  | |_| || . \ 
  |____/|_|  |_|\____||_| |_|\___/|_| \_\  |_| |_||_| |_|\____||_|\_\
        """
        )
        print("🍿 Welcome to the most fun way to book your movie tickets! 🍿")
    
    def print_menu():
        if system.current_user:
            role = "ADMIN" if system.current_user.is_admin else "USER"
            print(f"\n👋 Welcome, {system.current_user.username}! ({role})")
            print("📋 MENU OPTIONS:")
            print("1. 🎬 Browse Movies")
            print("2. 🎭 View Movie Showtimes")
            print("3. 🎫 Book Tickets")
            print("4. 📋 My Bookings")
            print("5. ❌ Cancel Booking")
            
            if system.current_user.is_admin:
                print("--- ADMIN OPTIONS ---")
                print("6. ➕ Add Movie")
                print("7. ➖ Remove Movie")
                print("8. 🕐 Add Showtime")
                print("9. 🗑️ Remove Showtime")
                print("10. 📊 View All Bookings")
                print("11. 🚪 Logout")
            else:
                print("6. 🚪 Logout")
        else:
            print("\n📋 MAIN MENU:")
            print("1. 🔐 Login")
            print("2. 📝 Register")
            print("3. 👋 Exit")
    
    def display_movies():
        movies = system.browse_movies()
        if not movies:
            print("❌ No movies available.")
            return
        
        print("\n🎬 AVAILABLE MOVIES:")
        print("="*80)
        import random
        fun_facts = [
            "Did you know? The longest movie ever made is over 85 hours long!",
            "🍿 Popcorn was first sold in movie theaters in 1912!",
            "🎬 The first public movie screening was in 1895.",
            "🎥 The most expensive movie ever made is Pirates of the Caribbean: On Stranger Tides.",
            "🦖 Jurassic Park's dinosaur roars were made from tortoise mating sounds!",
            "🎭 The Oscar statuette's official name is the 'Academy Award of Merit'."
        ]
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie.title}")
            print(f"   ID: {movie.movie_id}")
            print(f"   Genre: {movie.genre}")
            print(f"   Duration: {movie.duration} minutes")
            print(f"   Rating: {movie.rating}")
            # Always show price in dollars (force $ even if old data has ₹)
            price_str = f"${movie.price:.2f}"
            print(f"   Price: {price_str}")
            print(f"   Description: {movie.description}")
            # Show a fun fact for each movie
            print(f"💡 Fun Fact: {random.choice(fun_facts)}")
            print("-" * 80)
    
    def display_showtimes(movie_id: str):
        showtimes = system.get_movie_showtimes(movie_id)
        if not showtimes:
            print("❌ No showtimes available for this movie.")
            return
        
        movie = system.movies.get(movie_id)
        if movie:
            print(f"\n🎭 SHOWTIMES for '{movie.title}':")
            print("="*80)
            for i, showtime in enumerate(showtimes, 1):
                available = len(showtime.get_available_seats())
                print(f"{i}. Showtime ID: {showtime.showtime_id}")
                print(f"   📅 Date: {showtime.date}")
                print(f"   🕐 Time: {showtime.time}")
                print(f"   🏢 Theater: {showtime.theater}")
                print(f"   💺 Available Seats: {available}/{showtime.total_seats}")
                print(f"   💰 Price: ${movie.price:.2f} per seat")
                print("-" * 80)
    
    def display_bookings(bookings: List[Booking]):
        if not bookings:
            print("❌ No bookings found.")
            return
        
        print("\n🎫 BOOKINGS:")
        print("="*80)
        for i, booking in enumerate(bookings, 1):
            print(f"{i}. Booking ID: {booking.booking_id}")
            print(f"   🎬 Movie: {booking.movie_title}")
            print(f"   🎭 Showtime: {booking.showtime_id}")
            print(f"   💺 Seats: {', '.join(map(str, booking.seat_numbers))}")
            print(f"   💰 Total: ${booking.total_amount:.2f}")
            print(f"   📅 Date: {booking.booking_date}")
            print(f"   📊 Status: {booking.status}")
            # Loyalty points: 1 point per seat
            points = len(booking.seat_numbers)
            print(f"   🏆 Loyalty Points Earned: {points}")
            print("-" * 80)
    
    def get_seat_display(showtime: ShowTime) -> str:
        """Generate visual seat map with row/column labels and emojis."""
        seats_per_row = 10
        total_rows = (showtime.total_seats + seats_per_row - 1) // seats_per_row
        display = "\n💺 SEAT MAP (🎟️ Available, ❌ Booked):\n"
        display += "     " + " ".join(f"{col+1:2d}" for col in range(seats_per_row)) + "\n"
        for row in range(total_rows):
            row_letter = chr(ord('A') + row)
            display += f" {row_letter} : "
            for col in range(seats_per_row):
                seat_num = row * seats_per_row + col + 1
                if seat_num <= showtime.total_seats:
                    if seat_num in showtime.booked_seats:
                        display += "❌ "
                    else:
                        display += "🎟️ "
                else:
                    display += "   "
            display += "\n"
        display += "\n👉 To book, enter seats as e.g. A,1 or B,5 (row letter, column number). Multiple seats: A,1;B,2;C,3\n"
        return display
    
    print_header()
    print("🎭 Welcome to the Movie Ticket Booking System!")
    print("ℹ️  Demo accounts: 'admin' (admin) or 'sudip' (user)")
    # Easter egg: popcorn command
    print("🍀 Type 'popcorn' at any menu for a surprise!")
    
    while True:
        print_menu()
        choice = input("\n🔽 Enter your choice: ").strip()
        # Easter egg: popcorn
        if choice.lower() == 'popcorn':
            print("🍿 You found the secret popcorn! Enjoy your snack while watching the movie! 🍿")
            wait_for_user()
            continue
        
        try:
            if not system.current_user:
                if choice == '1':  # Login
                    username = input("👤 Enter username: ").strip()
                    if username == 'admin':
                        password = input("🔑 Enter password for admin: ").strip()
                        if password != '12345':
                            print("❌ Incorrect password for admin.")
                            wait_for_user()
                            continue
                    if system.login(username):
                        print("✅ Login successful!")
                    else:
                        print("❌ Invalid username. Please try again.")
                    wait_for_user()
                
                elif choice == '2':  # Register
                    username = input("👤 Enter username: ").strip()
                    email = input("📧 Enter email: ").strip()
                    if system.register_user(username, email):
                        print("✅ Registration successful! You can now login.")
                    else:
                        print("❌ Username already exists. Please choose a different one.")
                    wait_for_user()
                
                elif choice == '3':  # Exit
                    print("👋 Thank you for using Movie Ticket Booking System!")
                    break
                
                else:
                    print("❌ Invalid choice. Please try again.")
                    wait_for_user()
            
            else:
                if choice == '1':  # Browse Movies
                    display_movies()
                    wait_for_user()
                
                elif choice == '2':  # View Movie Showtimes
                    movie_id = input("🎬 Enter movie ID: ").strip()
                    display_showtimes(movie_id)
                    wait_for_user()
                
                elif choice == '3':  # Book Tickets
                    showtime_id = input("🎭 Enter showtime ID: ").strip()
                    
                    # Find and display showtime details
                    showtime = None
                    movie = None
                    for m in system.movies.values():
                        for st in m.showtimes:
                            if st.showtime_id == showtime_id:
                                showtime = st
                                movie = m
                                break
                        if showtime:
                            break
                    
                    if not showtime or not movie:
                        print("❌ Invalid showtime ID.")
                        wait_for_user()
                        continue
                    
                    print(get_seat_display(showtime))
                    print(f"💰 Price per seat: ${movie.price:.2f}")
                    
                    seat_input = input("💺 Enter seat(s) (e.g. A,1 or B,2;C,3): ").strip()
                    # Accept both comma or semicolon as separator for multiple seats
                    seat_strs = []
                    # If only one comma, treat as single seat (e.g. B,2)
                    if ';' in seat_input:
                        seat_strs = [s.strip() for s in seat_input.split(';') if s.strip()]
                    elif seat_input.count(',') == 1:
                        seat_strs = [seat_input.strip()]
                    elif ',' in seat_input and seat_input.count(',') > 1:
                        # If user enters A,1,B,2, treat as A,1;B,2
                        parts = [p.strip() for p in seat_input.split(',')]
                        seat_strs = [f"{parts[i]},{parts[i+1]}" for i in range(0, len(parts), 2) if i+1 < len(parts)]
                    else:
                        seat_strs = [seat_input.strip()] if seat_input else []
                    seat_numbers = []
                    invalid_seats = []
                    booked_seats = []
                    for seat_str in seat_strs:
                        if ',' not in seat_str:
                            invalid_seats.append(seat_str)
                            continue
                        row_part, col_part = seat_str.split(',', 1)
                        row_part = row_part.strip().upper()
                        col_part = col_part.strip()
                        if not row_part.isalpha() or not col_part.isdigit():
                            invalid_seats.append(seat_str)
                            continue
                        row = ord(row_part) - ord('A')
                        col = int(col_part) - 1
                        if row < 0 or col < 0 or col >= 10:
                            invalid_seats.append(seat_str)
                            continue
                        seat_num = row * 10 + col + 1
                        if seat_num > showtime.total_seats:
                            invalid_seats.append(seat_str)
                            continue
                        if seat_num in showtime.booked_seats:
                            booked_seats.append(seat_str)
                            continue
                        seat_numbers.append(seat_num)
                    if invalid_seats:
                        print(f"❌ Invalid seat(s) format or out of range: {invalid_seats}\n   ➡️  Please enter as A,1 or B,2;C,3 (row letter, column number; separate multiple seats with semicolons or commas)")
                        wait_for_user()
                        continue
                    if booked_seats:
                        print(f"❌ Seats already booked: {booked_seats}")
                        wait_for_user()
                        continue
                    total_cost = len(seat_numbers) * movie.price
                    print(f"💰 Total cost: ${total_cost:.2f}")
                    confirm = input("✅ Confirm booking? (y/n): ").strip().lower()
                    if confirm == 'y':
                        booking_id = system.book_tickets(showtime_id, seat_numbers)
                        if booking_id:
                            print(f"🎉 Booking successful! Booking ID: {booking_id}")
                            # Mini-game: Lucky Draw
                            import random
                            if random.randint(1, 5) == 3:
                                print("🎲 Lucky Draw! You won a free popcorn coupon! 🍿 Use code: POPCORN2025")
                        else:
                            print("❌ Booking failed. Please try again.")
                    else:
                        print("❌ Booking cancelled.")
                    wait_for_user()
                
                elif choice == '4':  # My Bookings
                    bookings = system.get_user_bookings()
                    display_bookings(bookings)
                    wait_for_user()
                
                elif choice == '5':  # Cancel Booking
                    booking_id = input("🎫 Enter booking ID to cancel: ").strip()
                    if system.cancel_booking(booking_id):
                        print("✅ Booking cancelled successfully!")
                    else:
                        print("❌ Failed to cancel booking. Please check booking ID.")
                    wait_for_user()
                
                elif choice == '6':  # Logout or Add Movie (admin)
                    if system.current_user.is_admin:
                        # Add Movie
                        print("\n➕ ADD NEW MOVIE:")
                        title = input("🎬 Movie title: ").strip()
                        genre = input("🎭 Genre: ").strip()
                        duration = int(input("⏱️ Duration (minutes): ").strip())
                        rating = input("⭐ Rating (G/PG/PG-13/R): ").strip()
                        description = input("📝 Description: ").strip()
                        price = float(input("💰 Ticket price: $").strip())
                        
                        movie_id = system.add_movie(title, genre, duration, rating, description, price)
                        if movie_id:
                            print(f"✅ Movie added successfully! Movie ID: {movie_id}")
                        else:
                            print("❌ Failed to add movie.")
                        wait_for_user()
                    else:
                        # Logout
                        system.logout()
                        print("👋 Logged out successfully!")
                        wait_for_user()
                
                elif choice == '7' and system.current_user.is_admin:  # Remove Movie
                    movie_id = input("🎬 Enter movie ID to remove: ").strip()
                    if system.remove_movie(movie_id):
                        print("✅ Movie removed successfully!")
                    else:
                        print("❌ Failed to remove movie.")
                    wait_for_user()
                
                elif choice == '8' and system.current_user.is_admin:  # Add Showtime
                    movie_id = input("🎬 Enter movie ID: ").strip()
                    if movie_id not in system.movies:
                        print("❌ Invalid movie ID.")
                        wait_for_user()
                        continue

                    date = input("📅 Enter date (YYYY-MM-DD): ").strip()
                    time = input("🕐 Enter time (HH:MM): ").strip()
                    theater = input("🏢 Enter theater name: ").strip()
                    total_seats_input = input("💺 Enter total seats (default 50): ").strip()
                    if total_seats_input == '':
                        total_seats = 50
                    else:
                        try:
                            total_seats = int(total_seats_input)
                        except ValueError:
                            print("❌ Invalid number for total seats. Using default 50.")
                            total_seats = 50

                    showtime_id = system.add_showtime(movie_id, date, time, theater, total_seats)
                    if showtime_id:
                        print(f"✅ Showtime added successfully! Showtime ID: {showtime_id}")
                    else:
                        print("❌ Failed to add showtime.")
                    wait_for_user()
                
                elif choice == '9' and system.current_user.is_admin:  # Remove Showtime
                    showtime_id = input("🎭 Enter showtime ID to remove: ").strip()
                    if system.remove_showtime(showtime_id):
                        print("✅ Showtime removed successfully!")
                    else:
                        print("❌ Failed to remove showtime.")
                    wait_for_user()
                
                elif choice == '10' and system.current_user.is_admin:  # View All Bookings
                    bookings = system.get_all_bookings()
                    display_bookings(bookings)
                    wait_for_user()
                
                elif choice == '11' and system.current_user.is_admin:  # Logout
                    system.logout()
                    print("👋 Logged out successfully!")
                    wait_for_user()
                
                else:
                    print("❌ Invalid choice. Please try again.")
                    wait_for_user()
        
        except Exception as e:
            print(f"❌ Error: {e}. Please try again.")
            wait_for_user()

if __name__ == "__main__":
    main()