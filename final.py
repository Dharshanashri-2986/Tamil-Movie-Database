import customtkinter as ctk
import mysql.connector
import pyttsx3
import os
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
import pandas as pd  # For easier data handling with the graph


# Initialize CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

# Establish database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Dharshana_8778",
        database="TamilMoviesDB"
    )

# Initialize Text-to-Speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Set speaking rate

# Set voice based on user selection
def set_voice():
    voices = engine.getProperty("voices")
    selected_voice = voice_var.get()
    if selected_voice == "Male":
        engine.setProperty("voice", voices[0].id)  # Male voice
    elif selected_voice == "Female":
        engine.setProperty("voice", voices[1].id)  # Female voice

# Speak function for text-to-speech
def speak(text):
    set_voice()
    engine.say(text)
    engine.runAndWait()

# Function to search movies
def search_movies():
    global last_results  # Keep track of last search results
    filter_type = filter_var.get()
    user_input = search_entry.get()
    
    if filter_type == "Year of Release":
        year = year_var.get()
        if not year:
            speak("Please specify a year to search.")
            return
        query = "SELECT name, lead1, genre, director, rating, year_of_release FROM movies WHERE year_of_release = %s"
        params = (year,)
    else:
        if not user_input:
            speak("Please specify your search.")
            return
        column_name = filter_to_column[filter_type]
        query = f"SELECT name, lead1, genre, director, rating, year_of_release FROM movies WHERE {column_name} LIKE %s"
        params = (f"%{user_input}%",)
    
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    last_results = cursor.fetchall()  # Store results globally
    db.close()
    
    display_results(last_results, speak_text=True)
    
def show_rating_vs_genre_graph():
    if not last_results:
        messagebox.showinfo("Graph Error", "No results to display in the graph.")
        return
    
    # Convert results to DataFrame for easier processing
    data = pd.DataFrame(last_results, columns=["Name", "Lead", "Genre", "Director", "Rating", "Year of Release"])
    
    # Calculate average rating per genre
    genre_ratings = data.groupby("Genre")["Rating"].mean()
    
    # Plotting with enhanced customization
    plt.figure(figsize=(12, 8))  # Bigger figure for better visibility
    bars = genre_ratings.plot(kind='bar', color='pink', edgecolor='black', fontsize=14)  # Set color and font size

    # Adding title and labels with custom font sizes
    plt.title("Average Rating by Genre", fontsize=20, fontweight='bold', color='Black')
    plt.xlabel("Genre", fontsize=16, fontweight='bold', color='darkred')
    plt.ylabel("Average Rating", fontsize=16, fontweight='bold', color='darkred')

    # Customizing x-ticks and y-ticks
    plt.xticks(rotation=45, ha='right', fontsize=14, color='black')
    plt.yticks(fontsize=14, color='black')

    # Adding gridlines for better readability
    plt.grid(axis='y', linestyle='--', color='darkgray', alpha=0.7)

    # Add value labels on top of the bars
    for p in bars.patches:
        height = p.get_height()
        plt.text(p.get_x() + p.get_width() / 2, height + 0.05, f'{height:.2f}', ha='center', fontsize=14, color='black', fontweight='bold')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Show the plot
    plt.show()


# Display search results in the GUI
def display_results(results, speak_text=True):
    clear_results_area()
    if results:
        if speak_text:  # Only speak if flag is True
            speak("Here are the results for your search. Hope you enjoy your movie.")
        for idx, movie in enumerate(results):
            movie_details = f"{movie[0]} || Lead: {movie[1]} || Genre: {movie[2]} || Director: {movie[3]} || Rating: {movie[4]} || Year: {movie[5]}"
            movie_label = ctk.CTkLabel(results_frame, text=movie_details, font=("Comic Sans MS", 18))
            movie_label.pack(pady=10)

            # Add "Watch Later" button for each movie
            watch_later_button = ctk.CTkButton(results_frame, text="Add to Watch Later",
                                               command=lambda m=movie: add_to_watch_later(m), font=("Comic Sans MS", 16))
            watch_later_button.pack(pady=10)
        
        # Show the "Show Graph" button after displaying search results
        show_graph_button.pack(pady=10)  
        
    else:
        speak("Sorry, we couldn't find any matching movies. Try refining your search.")
        show_graph_button.pack_forget()  # Hide graph button if no results
# Clear previous results
def clear_results_area():
    for widget in results_frame.winfo_children():
        widget.destroy()

# Function to add movie to "Watch Later" list
def add_to_watch_later(movie_details):
    movie_name = movie_details[0]
    watch_later_file = "watch_later.txt"

    if os.path.exists(watch_later_file):
        with open(watch_later_file, "r") as file:
            watch_later_movies = file.readlines()
            for line in watch_later_movies:
                if movie_name in line:
                    messagebox.showinfo("Watch Later", f"Movie '{movie_name}' is already in Watch Later.")
                    return

    with open(watch_later_file, "a") as file:
        file.write(" || ".join(map(str, movie_details)) + "\n")
    messagebox.showinfo("Watch Later", f"Movie '{movie_name}' added to Watch Later.")

# Function to display the "Watch Later" list
def display_watch_later():
    clear_results_area()
    try:
        with open("watch_later.txt", "r") as file:
            watch_later_movies = file.readlines()
        
        if watch_later_movies:
            for idx, movie in enumerate(watch_later_movies, start=1):
                movie_label = ctk.CTkLabel(results_frame, text=f"{idx}. {movie.strip()}", font=("Comic Sans MS", 18))
                movie_label.pack(pady=10)
                
                # Add "Remove" button for each movie in Watch Later
                remove_button = ctk.CTkButton(results_frame, text="Remove from Watch Later",
                                              command=lambda m=movie: remove_from_watch_later(m), font=("Comic Sans MS", 16))
                remove_button.pack(pady=10)
        else:
            messagebox.showinfo("Watch Later", "No movies in Watch Later list.")
        
        # Show Back to Results button when viewing Watch Later list
        back_to_results_button.pack(pady=10)
    except FileNotFoundError:
        messagebox.showinfo("Watch Later", "No movies in Watch Later list.")
        back_to_results_button.pack_forget()  # Hide back button if no movies

# Function to remove a movie from "Watch Later" list
def remove_from_watch_later(movie_details):
    try:
        with open("watch_later.txt", "r") as file:
            lines = file.readlines()
        
        with open("watch_later.txt", "w") as file:
            for line in lines:
                if line.strip() != movie_details.strip():
                    file.write(line)
        
        messagebox.showinfo("Watch Later", f"Movie '{movie_details.strip()}' removed from Watch Later.")
        display_watch_later()
    except FileNotFoundError:
        messagebox.showinfo("Watch Later", "No movies in Watch Later list.")

# Function to go back to the results page
def back_to_results():
    back_to_results_button.pack_forget()  # Hide Back to Results button
    view_watch_later_button.pack(side="right", padx=10)  # Show View Watch Later button again
    display_results(last_results, speak_text=False)  # Redisplay the last search results without speaking

# CustomTkinter UI setup
root = ctk.CTk()
root.title("KOLLYWOOD HUB : DISCOVER, WATCH, ENJOY!")
root.geometry("1024x768")  # Larger window size

# Title Label
title_label = ctk.CTkLabel(root, text="KOLLYWOOD HUB : DISCOVER, WATCH, ENJOY!", font=("Imprint MT Shadow", 24,"bold"))
title_label.pack(pady=30)

# Voice selection dropdown
voice_var = ctk.StringVar(value="Select Voice")
voice_menu = ctk.CTkOptionMenu(root, variable=voice_var, values=["Male", "Female"], font=("Agency FB", 22))
voice_menu.pack(pady=35)

# Filter options and mapping to database columns
filter_options = ["Lead", "Genre", "Director", "Year of Release", "Movie Name"]  # Removed "Rating"
filter_to_column = {
    "Lead": "lead1",
    "Genre": "genre",
    "Director": "director",
    "Year of Release": "year_of_release",
    "Movie Name": "name"
}

# Dropdown for filters
filter_var = ctk.StringVar(value="Choose a Category:")
filter_menu = ctk.CTkOptionMenu(root, variable=filter_var, values=filter_options, font=("Agency FB", 22))
filter_menu.pack(pady=25)

# Frame for filtering options and text input area
input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=10)

# Entry box for user input
search_entry = ctk.CTkEntry(input_frame, width=400, font=("Agency FB", 22))
search_entry.grid(row=0, column=0, padx=20)

# Dropdown for year selection if "Year of Release" is selected
year_var = ctk.StringVar(value="Choose Year")
year_menu = ctk.CTkOptionMenu(input_frame, variable=year_var, values=[str(y) for y in range(2017, 2025)], font=("Agency FB", 22))

# Initially hide the year dropdown menu
year_menu.grid_forget()

# Update interface when filter is selected
def update_input(event=None):
    if filter_var.get() == "Year of Release":
        search_entry.grid_forget()  # Hide the text entry field
        year_menu.grid(row=0, column=0, padx=20)  # Show the year dropdown above the search button
    else:
        year_menu.grid_forget()  # Hide the year dropdown
        search_entry.grid(row=0, column=0, padx=20)  # Show the text entry field above the search button

filter_var.trace("w", lambda *args: update_input())

# Search button
search_button = ctk.CTkButton(root, text="Search", command=search_movies, font=("Agency FB", 22))
search_button.pack(pady=10)

# Frame for the buttons
buttons_frame = ctk.CTkFrame(root)
buttons_frame.pack(pady=10)

# View Watch Later button
view_watch_later_button = ctk.CTkButton(buttons_frame, text="View Watch Later", command=display_watch_later, font=("Agency FB", 22))
view_watch_later_button.pack(side="right", padx=10)

# Back to Results Button
back_to_results_button = ctk.CTkButton(root, text="Back to Results", command=back_to_results, font=("Agency FB", 22))
back_to_results_button.pack_forget()  # Hidden by default

# Frame to display results with scrolling
results_frame = ctk.CTkScrollableFrame(root)
results_frame.pack(pady=20, fill="both", expand=True)

# Button to show Rating vs Genre graph
show_graph_button = ctk.CTkButton(buttons_frame, text="Show Rating vs Genre Graph", command=show_rating_vs_genre_graph, font=("Agency FB", 22))
show_graph_button.pack_forget()  # Hidden initially, shown after a search


root.mainloop()