import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import re
from datetime import datetime

conn = mysql.connector.connect(host="database-1.cxiyqi28i3py.us-east-1.rds.amazonaws.com", user="admin", password="DB20031998", database="DB_Project")

# cursor = conn.cursor()
#
#
# def drop_all_tables(cursor):
#     """
#     Drops all tables from the TV_BroadCast database in the correct order to avoid foreign key constraint errors.
#
#     Args:
#     cursor: A cursor object from an active MySQL database connection.
#
#     Returns:
#     None
#     """
#     try:
#         # Ordered list of tables to drop to avoid foreign key constraint violations
#         tables_to_drop = [
#             'Favorite', 'NetworkedChannels', 'NetworkSystems',
#             'NetworkCountries', 'Network', 'ChannelEncryptions',
#             'ChannelLanguages', 'ChannelSystems', 'ChannelCountries',
#             'Channel', 'Satellite', 'User'
#         ]
#
#         # Drop each table in the correct order
#         for table in tables_to_drop:
#             print(f"Dropping table: {table}")
#             cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
#
#         # Commit the changes to the database
#         conn.commit()
#         print("All tables were dropped successfully.")
#
#     except mysql.connector.Error as err:
#         print(f"Error occurred while dropping tables: {err}")
#
#
# def load_sql_file(filepath):
#
#     with open(filepath, 'r') as file:
#         sql_script = file.read()
#
#     # If your SQL commands are separated by semicolons
#     commands = sql_script.split(';')
#
#     # Execute each command from the SQL file
#     for command in commands:
#         try:
#             if command.strip():
#                 cursor.execute(command)
#         except mysql.connector.Error as err:
#             print(f"Error occurred: {err}")
#
#     # Commit the changes to the database
#     conn.commit()
#
#
# drop_all_tables(cursor)
# load_sql_file('/Users/youssef/Desktop/Semester 6/Database/Project/MileStone 2 Submission/mydatabase_dump copy.sql')

# # Close the connection
# cursor.close()
# conn.close()

current_user_email = None
current_region = None


Q1 = "SELECT C.*, S. PositionDegree FROM Channel C INNER JOIN Satellite S ON C.SatName = S.Name WHERE ABS(S. PositionDegree - %s) <= 10 AND S. PositionDirection = %s;"
Q2 = "SELECT F.ChannelName, F.Frequency, CE.Encryptions FROM Favorite F INNER JOIN Channel C ON F.SatName = C.SatName AND F.ChannelName = C.ChannelName AND F.Frequency = C.Frequency AND F.VideoEncoding = C.VideoEncoding INNER JOIN User U ON F.UserEmail = U.Email INNER JOIN Satellite S ON C.SatName = S.Name INNER JOIN ChannelEncryptions CE ON C.SatName = CE.SatName AND C.ChannelName = CE.ChannelName AND C.Frequency = CE.Frequency AND C.VideoEncoding = CE.VideoEncoding WHERE F.UserEmail = %s AND S.Region = U.Region;"
Q3 = "SELECT PC.NetName, COUNT(*) AS TotalChannels, COUNT( PC.SatName)/COUNT(DISTINCT(PC.NetworkedChannels)) AS AvgSatellites FROM NetworkedChannels PC GROUP BY 1 ORDER BY 2 DESC LIMIT 5;";
Q4 = "SELECT Launch_Rocket, COUNT(*) AS SatelliteNum FROM Satellite GROUP BY Launch_Rocket ORDER BY SatelliteNum DESC LIMIT 5;"
Q5 = "SELECT S.Name, COUNT(*) AS TotalChannels, DATEDIFF(CURRENT_DATE(), S.Launch_Date) AS NumOfDaysSinceLaunch, COUNT(*) / DATEDIFF(CURRENT_DATE(), S.Launch_Date) AS GrowthRatio FROM Satellite S INNER JOIN Channel C ON S.Name = C.SatName GROUP BY S.Name ORDER BY GrowthRatio DESC LIMIT 5;"

def End():
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        Main.destroy()
        conn.close()

def manage_favorites():
    global current_user_email, conn
    if current_user_email is None:
        messagebox.showerror("Error", "No user logged in.")
        return

    manage_fav_win = tk.Toplevel()
    manage_fav_win.title("Manage Favorites")
    manage_fav_win.geometry("800x850")

    tk.Label(manage_fav_win, text="Satellite Name:", font=('Arial', 14)).pack(pady=(10,0))
    sat_name_entry = tk.Entry(manage_fav_win, width=30)
    sat_name_entry.pack(pady=(0,10))

    tk.Label(manage_fav_win, text="Channel Name:", font=('Arial', 14)).pack(pady=(10,0))
    channel_name_entry = tk.Entry(manage_fav_win, width=30)
    channel_name_entry.pack(pady=(0,10))

    tk.Label(manage_fav_win, text="Frequency:", font=('Arial', 14)).pack(pady=(5,0))
    frequency_entry = tk.Entry(manage_fav_win, width=30)
    frequency_entry.pack(pady=(0,10))

    tk.Label(manage_fav_win, text="Video Encoding:", font=('Arial', 14)).pack(pady=(10,0))
    video_encoding_entry = tk.Entry(manage_fav_win, width=30)
    video_encoding_entry.pack(pady=(0,10))

    tree_frame = tk.Frame(manage_fav_win)
    tree_frame.pack(fill='both', expand=True, pady=(20,0))
    tree = ttk.Treeview(tree_frame, columns=('SatName', 'ChannelName', 'Frequency', 'VideoEncoding'), show='headings')
    tree.heading('SatName', text='Satellite Name')
    tree.heading('ChannelName', text='Channel Name')
    tree.heading('Frequency', text='Frequency')
    tree.heading('VideoEncoding', text='Video Encoding')
    tree.pack(fill='both', expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscrollcommand=scrollbar.set)

    load_favorites(tree)

    tk.Button(manage_fav_win, text="Add to Favorites", command=lambda: insert_favorite(
        sat_name_entry.get(), channel_name_entry.get(), frequency_entry.get(), video_encoding_entry.get(), tree)).pack(pady=(20,0))

    tk.Button(manage_fav_win, text="Remove from Favorites", command=lambda: delete_favorite(
        sat_name_entry.get(), channel_name_entry.get(), frequency_entry.get(), video_encoding_entry.get(), tree)).pack(pady=(20,0))

def load_favorites(tree):
    cursor = conn.cursor()
    cursor.execute("SELECT SatName, ChannelName, Frequency, VideoEncoding FROM Favorite WHERE UserEmail = %s;", (current_user_email,))
    rows = cursor.fetchall()
    cursor.close()
    for row in rows:
        tree.insert('', 'end', values=row)

def insert_favorite(sat_name, channel_name, frequency, video_encoding, tree):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Channel WHERE SatName = %s AND ChannelName = %s AND Frequency = %s AND VideoEncoding = %s;",
                   (sat_name, channel_name, frequency, video_encoding))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Error", "Channel details are incorrect or do not exist.")
        cursor.close()
        return

    try:
        cursor.execute("INSERT INTO Favorite (UserEmail, SatName, ChannelName, Frequency, VideoEncoding) VALUES (%s, %s, %s, %s, %s);",
                       (current_user_email, sat_name, channel_name, frequency, video_encoding))
        conn.commit()
        messagebox.showinfo("Success", "Channel added to favorites successfully!")
        tree.insert('', 'end', values=(sat_name, channel_name, frequency, video_encoding))
    finally:
        cursor.close()

def delete_favorite(sat_name, channel_name, frequency, video_encoding, tree):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Favorite WHERE UserEmail = %s AND SatName = %s AND ChannelName = %s AND Frequency = %s AND VideoEncoding = %s;",
                   (current_user_email, sat_name, channel_name, frequency, video_encoding))
    conn.commit()
    if cursor.rowcount < 1:
        messagebox.showinfo("Info", "No such favorite found to delete.")
    else:
        messagebox.showinfo("Success", "Channel removed from favorites successfully!")
        # Refresh the tree view
        for item in tree.get_children():
            if tree.item(item, 'values')[:4] == (sat_name, channel_name, frequency, video_encoding):
                tree.delete(item)
                break
    cursor.close()

def Sub1():
    position_degree = SP.get()
    position_direction = SD.get()


    cursor = conn.cursor()
    cursor.execute(Q1, (position_degree, position_direction))
    values = cursor.fetchall()

    if len(values) == 0:
        messagebox.showerror("", "No channels found for the given position degree and direction.")
        cursor.close()
        return

    cursor.close()

    Do1_2 = tk.Toplevel()
    Do1_2.title("Channels")
    Do1_2.geometry("2000x400")

    columns = ("SatName", "ChannelName", "Frequency", "VideoEncoding", "Website", "Beam",
               "VideoCompression", "SR", "FEC", "EIRP", "PositionDegree")

    tree = ttk.Treeview(Do1_2, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor='center')

    for row in values:
        tree.insert('', tk.END, values=row)

    tree.pack(expand=True, fill='both')

    Do1_2.mainloop()


def Query1():
    global Do1_1, SP, SD  # Declare SD as a global variable for the satellite direction input

    Do1_1 = tk.Toplevel()
    Do1_1.title("Channel Finder")
    Do1_1.geometry("800x400")

    tk.Label(Do1_1, text="Please Enter the Satellite Position Degree", font=('Arial', 20)).pack(pady=10)
    SP = tk.Entry(Do1_1, bd=5)
    SP.pack()

    tk.Label(Do1_1, text="Please Enter the Satellite Position Direction (E/W)", font=('Arial', 20)).pack(pady=10)
    SD = tk.Entry(Do1_1, bd=5)  # SD is the input field for the satellite position direction
    SD.pack()

    tk.Button(Do1_1, text="Enter", font=('Arial', 22), command=Sub1).pack(pady=20)

def Sub2():
    # Check if the current_region is set
    if current_region is None:
        messagebox.showerror("Error", "Region not set. Please log in again or check your settings.")
        return

    cursor = conn.cursor()
    cursor.execute(Q2, (current_user_email,))  # Pass the current_region as a parameter
    values = cursor.fetchall()
    cursor.close()

    if not values:
        messagebox.showerror("Error", "No channels found for your region.")
        return

    # Display the results in a new Treeview within the result window
    result_window = tk.Toplevel()
    result_window.title("Favorite Channels in Your Region")
    result_window.geometry("600x400")
    tree = ttk.Treeview(result_window, columns=('ChannelName', 'Frequency', 'Encryptions'), show='headings')
    tree.heading('ChannelName', text='Channel Name')
    tree.heading('Frequency', text='Frequency')
    tree.heading('Encryptions', text='Encryptions')
    for item in values:
        tree.insert('', 'end', values=item)
    tree.pack(fill='both', expand=True)


def Query2():
    if current_user_email is None or current_region is None:
        messagebox.showerror("Error", "User region not set.")
        return

    # Create a Toplevel window to display the results
    Do2_1 = tk.Toplevel()
    Do2_1.title("TV BroadCasting Info")
    Do2_1.geometry("800x400")

    # Display the current user's email and region
    tk.Label(Do2_1, text="Your Email: " + current_user_email, font=('Arial', 20)).pack(pady=10)
    tk.Label(Do2_1, text="Your Region: " + current_region, font=('Arial', 20)).pack(pady=10)

    # Button to execute the query
    tk.Button(Do2_1, text="Display Results", font=('Arial', 22), command=Sub2).pack(pady=20)

def Query3():
    cursor = conn.cursor()
    cursor.execute(Q3)
    values = cursor.fetchall()
    cursor.close()

    if not values:
        messagebox.showerror("Error", "No results found.")
        return

    # Display results within the function
    result_window = tk.Toplevel()
    result_window.title("Top 5 TV Networks / Providers")
    result_window.geometry("600x400")
    tree = ttk.Treeview(result_window, columns=('NetName', 'ChannelNum', 'AvgSatPerChannel'), show='headings')
    tree.heading('NetName', text='Network Name')
    tree.heading('ChannelNum', text='Number of Channels')
    tree.heading('AvgSatPerChannel', text='Average Satellites Per Channel')
    for item in values:
        tree.insert('', 'end', values=item)
    tree.pack(fill='both', expand=True)


def Query4():
    cursor = conn.cursor()
    cursor.execute(Q4)
    values = cursor.fetchall()
    cursor.close()

    if not values:
        messagebox.showerror("Error", "No results found.")
        return

    result_window = tk.Toplevel()
    result_window.title("Top 5 Rockets by Number of Satellites")
    result_window.geometry("600x400")
    tree = ttk.Treeview(result_window, columns=('Launch_Rocket', 'NumberOfSatellites'), show='headings')
    tree.heading('Launch_Rocket', text='Rocket')
    tree.heading('NumberOfSatellites', text='Number of Satellites')
    for item in values:
        tree.insert('', 'end', values=item)
    tree.pack(fill='both', expand=True)

def Query5():
    cursor = conn.cursor()
    cursor.execute(Q5)
    values = cursor.fetchall()
    cursor.close()

    if not values:
        messagebox.showerror("Error", "No results found.")
        return


    result_window = tk.Toplevel()
    result_window.title("Top 5 Growing Satellites")
    result_window.geometry("800x400")


    tree = ttk.Treeview(result_window, columns=('Name', 'TotalChannels', 'NumOfDaysSinceLaunch', 'GrowthRatio'),
                        show='headings')
    tree.heading('Name', text='Name')
    tree.heading('TotalChannels', text='Total Channels')
    tree.heading('NumOfDaysSinceLaunch', text='Days Since Launch')
    tree.heading('GrowthRatio', text='Growth Ratio')


    for item in values:
        tree.insert('', 'end', values=item)

    tree.pack(fill='both', expand=True)


def Query6(languages):
    def get_top_channels():
        selected_language = language_dropdown.get()
        if not selected_language:
            messagebox.showerror("Error", "Please select a language.")
            return

        cursor = conn.cursor()
        query_top_channels = "SELECT CL.ChannelName, COUNT(DISTINCT C.SatName) AS NumberOfSatellites FROM ChannelLanguages CL JOIN Channel C ON CL.ChannelName = C.ChannelName WHERE CL.Languages = %s GROUP BY CL.ChannelName ORDER BY NumberOfSatellites DESC LIMIT 5;"
        cursor.execute(query_top_channels, (selected_language,))
        results = cursor.fetchall()
        cursor.close()

        if not results:
            messagebox.showinfo("Info", "No channels found for the selected language.")
            return

        result_window = tk.Toplevel()
        result_window.title(f"Top 5 Channels by Satellite Count for {selected_language}")
        result_window.geometry("600x400")

        tree = ttk.Treeview(result_window, columns=('ChannelName', 'NumberOfSatellites'), show='headings')
        tree.heading('ChannelName', text='Channel Name')
        tree.heading('NumberOfSatellites', text='Number of Satellites')

        for item in results:
            tree.insert('', 'end', values=item)

        tree.pack(fill='both', expand=True)

    result_window = tk.Toplevel()
    result_window.title("Select Language")
    result_window.geometry("300x150")

    tk.Label(result_window, text="Select Language:", font=('Arial', 14)).pack(pady=(10, 0))

    language_selection = tk.StringVar(result_window)
    language_dropdown = ttk.Combobox(result_window, textvariable=language_selection, values=languages)
    language_dropdown.pack(pady=(0, 10))

    submit_btn = tk.Button(result_window, text="Submit", font=('Arial', 16), command=get_top_channels)
    submit_btn.pack(pady=(10, 0))

    result_window.mainloop()


def Sub7(selected_regions, satellite_name, video_encoding, language):
    cursor = conn.cursor()

    base_query = "SELECT S.Name AS SatName, S.Region AS Region, C.ChannelName, C.Frequency, C.VideoEncoding, CL.Languages FROM Channel C INNER JOIN Satellite S ON C.SatName = S.Name INNER JOIN ChannelLanguages CL ON C.SatName = CL.SatName AND C.ChannelName = CL.ChannelName AND C.Frequency = CL.Frequency AND C.VideoEncoding = CL.VideoEncoding WHERE 1=1"
    params = []

    if selected_regions:
        region_placeholders = ', '.join(['%s'] * len(selected_regions))
        base_query += " AND S.Region IN ({})".format(region_placeholders)
        params.extend(selected_regions)
    if satellite_name:
        satellite_name_list = satellite_name.split(',')
        satellite_placeholders = ', '.join(['%s'] * len(satellite_name_list))
        base_query += " AND S.Name IN ({})".format(satellite_placeholders)
        params.extend(satellite_name_list)
    if video_encoding:
        video_encoding_list = video_encoding.split(',')
        video_encoding_placeholders = ', '.join(['%s'] * len(video_encoding_list))
        base_query += " AND C.VideoEncoding IN ({})".format(video_encoding_placeholders)
        params.extend(video_encoding_list)
    if language:
        language_list = language.split(',')
        language_placeholders = ', '.join(['%s'] * len(language_list))
        base_query += " AND CL.Languages IN ({})".format(language_placeholders)
        params.extend(language_list)

    cursor.execute(base_query, params)
    values = cursor.fetchall()
    cursor.close()

    if not values:
        messagebox.showerror("Error", "No channels found matching the criteria.")
        return

    result_window = tk.Toplevel()
    result_window.title("Filtered Channels Results")
    result_window.geometry("1200x600")

    tree = ttk.Treeview(result_window, columns=('SatName', 'Region', 'ChannelName', 'Frequency', 'VideoEncoding', 'Languages'), show="headings")
    tree.heading('SatName', text='Satellite Name')
    tree.heading('Region', text='Region')
    tree.heading('ChannelName', text='Channel Name')
    tree.heading('Frequency', text='Frequency')
    tree.heading('VideoEncoding', text='Video Encoding')
    tree.heading('Languages', text='Languages')

    for row in values:
        tree.insert('', 'end', values=row)

    tree.pack(expand=True, fill='both')


def Query7():
    query7_win = tk.Toplevel()
    query7_win.title("Query Channels by Criteria")
    query7_win.geometry("500x500")

    tk.Label(query7_win, text="Select Region(s) (Leave empty for no filter):", font=('Arial', 14)).pack(pady=(10, 0))
    region_options = ["Asia & Pacific", "Europe, Africa & Middle East", "Atlantic", "North & South America"]
    region_dropdown = tk.Listbox(query7_win, selectmode=tk.MULTIPLE, height=len(region_options))
    for region in region_options:
        region_dropdown.insert(tk.END, region)
    region_dropdown.pack(pady=(0, 10))

    tk.Label(query7_win, text="Enter Satellite Name (comma-separated, leave empty for no filter):", font=('Arial', 14)).pack(pady=(10, 0))
    satellite_name_entry = tk.Entry(query7_win, width=30)
    satellite_name_entry.pack(pady=(0, 10))

    tk.Label(query7_win, text="Enter Video Encoding (comma-separated, leave empty for no filter):", font=('Arial', 14)).pack(pady=(10, 0))
    video_encoding_entry = tk.Entry(query7_win, width=30)
    video_encoding_entry.pack(pady=(0, 10))

    tk.Label(query7_win, text="Enter Language (comma-separated, leave empty for no filter):", font=('Arial', 14)).pack(pady=(10, 0))
    language_entry = tk.Entry(query7_win, width=30)
    language_entry.pack(pady=(0, 10))

    submit_btn = tk.Button(query7_win, text="Submit", font=('Arial', 16), command=lambda: Sub7(
        [region_options[i] for i in region_dropdown.curselection()],
        satellite_name_entry.get(),
        video_encoding_entry.get(),
        language_entry.get()))
    submit_btn.pack(pady=(20, 0))


def back_to_main(window):
    global Main
    if window:
        window.destroy()
    if Main:
        Main.deiconify()

def Menu():
    global MenuWindow
    MenuWindow = tk.Toplevel()
    MenuWindow.title("TV Broadcasting Info")
    MenuWindow.geometry("1300x700")

    label = tk.Label(MenuWindow, text="Welcome, What do you want to do?", font=('Arial', 24))
    label.pack(pady=20)

    button_f = tk.Frame(MenuWindow)
    button_f.columnconfigure(0, weight=1)

    cursor = conn.cursor()
    query_languages = "SELECT DISTINCT Languages FROM ChannelLanguages"
    cursor.execute(query_languages)
    languages = [lang[0] for lang in cursor.fetchall()]
    cursor.close()

    btnFav = tk.Button(button_f, text="Edit Favorite Channels", font=('Arial', 22), command=manage_favorites)
    btn1 = tk.Button(button_f, text="Query 1", font=('Arial', 22), command=Query1)
    btn2 = tk.Button(button_f, text="Query 2", font=('Arial', 22), command=Query2)
    btn3 = tk.Button(button_f, text="Query 3", font=('Arial', 22), command=Query3)
    btn4 = tk.Button(button_f, text="Query 4", font=('Arial', 22), command=Query4)
    btn5 = tk.Button(button_f, text="Query 5", font=('Arial', 22), command=Query5)
    btn6 = tk.Button(button_f, text="Query 6", font=('Arial', 22), command=lambda: Query6(languages))
    btn7 = tk.Button(button_f, text="Query 7", font=('Arial', 22), command=Query7)
    btnSignOut = tk.Button(button_f, text="Sign Out", font=('Arial', 22), command= lambda: back_to_main(MenuWindow))
    btn8 = tk.Button(button_f, text="Exit", font=('Arial', 22), command=End)

    wrap_width = 500

    labels_text = [
        "Show all the channels viewable from a certain location",
        "Show the user which of his/her favorite list is covered based on the user location along with the satellites and frequencies where s/he can get the channels on, and whether they are free or encrypted",
        "Show the top 5 TV Networks / Providers by number of channels, and the average number of satellites that each channel is available on",
        "Show the top 5 rockets in terms of the number of satellites they put in orbit",
        "Show the top 5 growing satellites using the number of channels they host compared to their launch date",
        "Show the top 5 channels for language chosen, ordered by the number of satellites they are hosted on",
        "Show the list of channels, filtered by region, satellite, HD/SD and/or language"
    ]

    for index, text in enumerate(labels_text, start=1):
        label = tk.Label(button_f, text=text, font=('Arial', 14), wraplength=wrap_width)
        label.grid(row=index, column=1, sticky="news")

    btnFav.grid(row=0, column=0, sticky="news")
    btn1.grid(row=1, column=0, sticky="news")
    btn2.grid(row=2, column=0, sticky="news")
    btn3.grid(row=3, column=0, sticky="news")
    btn4.grid(row=4, column=0, sticky="news")
    btn5.grid(row=5, column=0, sticky="news")
    btn6.grid(row=6, column=0, sticky="news")
    btn7.grid(row=7, column=0, sticky="news")
    btnSignOut.grid(row=8, column=0, sticky="news")
    btn8.grid(row=9, column=0, sticky="news")

    button_f.pack(pady=70)


def is_float(string):
    try:
        round(float(string), 1)
        return True
    except ValueError:
        return False
def Validate_Email_and_Password(email, password):
    query = "SELECT * FROM User WHERE Email = %s AND Pass = %s;"
    cursor = conn.cursor()
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    cursor.close()
    return result is not None



def Sign_in():
    global current_user_email, current_region
    email = email_input.get()
    password = password_input.get()
    if not Validate_Email_and_Password(email, password):
        messagebox.showerror("Error", "Email or Password incorrect, Please Try Again")
    else:
        current_user_email = email  # Set the global email variable after successful login

        # Fetch the region from the database
        cursor = conn.cursor()
        cursor.execute("SELECT Region FROM User WHERE Email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            current_region = result[0]

        signin.destroy()
        Menu()


def Sign_In_Page():
    global Main, signin, email_input, password_input
    if Main:
        Main.withdraw()

    signin = tk.Toplevel()
    signin.title("TV Broadcasting Info")
    signin.geometry("800x600")


    tk.Label(signin, text="Sign in Page", font=('Arial', 24)).pack(pady=20)
    tk.Label(signin, text="Please Enter Your Email", font=('Arial', 18)).pack(pady=10)

    email_input = tk.Entry(signin, bd=5)
    email_input.pack(pady=5)

    tk.Label(signin, text="Please Enter Your Password", font=('Arial', 18)).pack(pady=10)

    password_input = tk.Entry(signin, bd=5, show='*')
    password_input.pack(pady=5)

    tk.Button(signin, text="Enter", font=('Arial', 22), command=Sign_in).pack(pady=20)
    tk.Button(signin, text="Back", font=('Arial', 22), command=lambda: back_to_main(signin)).pack(pady=2)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) and len(email) <= 50

# Date validation
def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Password validation
def is_valid_password(password):
    return len(password) == 12 and any(not c.isalnum() for c in password)

# Check if email or password already exists
def email_password_exists(email, password):
    cursor = conn.cursor()
    query = "SELECT * FROM User WHERE Email = %s OR Pass = %s;"
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    cursor.close()
    return result is not None
def Sign_up():
    global current_region
    email = UE.get()
    password = UP.get()
    username = UN.get()
    gender = UG.get()
    birthdate = UB.get()
    country = UC.get()
    region = region_var.get()

    if not is_valid_email(email) or email_password_exists(email, password):
        messagebox.showerror("Sign Up Failed", "Invalid email or email/password already exists.")
    elif not is_valid_password(password):
        messagebox.showerror("Sign Up Failed", "Password must be 12 characters with at least one symbol.")
    elif not is_valid_date(birthdate):
        messagebox.showerror("Sign Up Failed", "Date isn't in the correct form: 'YYYY-MM-DD'.")
    elif gender not in ('M', 'F'):
        messagebox.showerror("Sign Up Failed", "Gender isn't in the correct form: 'M' or 'F'.")
    else:
        cursor = conn.cursor()
        query = "INSERT INTO User (Email, Pass, UserName, Gender, Birthdate, country, Region) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (email, password, username, gender, birthdate, country, region))
        conn.commit()
        cursor.close()

        current_region = region
        messagebox.showinfo("Success", "Successfully Signed Up")
        Signup.destroy()
        Start()


def Sign_Up_Page():
    global Main, Signup
    if Main:
        Main.withdraw()

    Signup = tk.Toplevel()
    Signup.title("TV Broadcasting Info")
    Signup.geometry("800x600")

    labelS = tk.Label(Signup, text="Sign Up Page", font=('Arial', 24))
    labelS.pack(pady=30)

    labelS2 = tk.Label(Signup, text="Please Enter Your Info", font=('Arial', 20))
    labelS2.pack(pady=30)

    global UE, UP, UN, UG, UB, UC, region_var

    label1 = tk.Label(Signup, text="Email", font=('Arial', 20)).place(x=120,y=203)
    label2 = tk.Label(Signup, text="Password", font=('Arial', 20)).place(x=120,y=256)
    label3 = tk.Label(Signup, text="Username", font=('Arial', 20)).place(x=120,y=309)
    label4 = tk.Label(Signup, text="Gender", font=('Arial', 20)).place(x=120,y=362)
    label5 = tk.Label(Signup, text="Birthdate", font=('Arial', 20)).place(x=120,y=415)
    label6 = tk.Label(Signup, text="Country", font=('Arial', 20)).place(x=120, y=468)
    label7 = tk.Label(Signup, text="Region", font=('Arial', 20)).place(x=120, y=521)

    UE = tk.Entry(Signup, bd=10)
    UE.place(x=300, y=200)

    UP = tk.Entry(Signup, bd=10)
    UP.place(x=300, y=250)

    UN = tk.Entry(Signup, bd=10)
    UN.place(x=300, y=300)

    UG = tk.Entry(Signup, bd=10)
    UG.place(x=300, y=350)

    UB = tk.Entry(Signup, bd=10)
    UB.place(x=300, y=400)

    UC = tk.Entry(Signup, bd=10)
    UC.place(x=300, y=450)

    region_options = ["Asia & Pacific", "Europe, Africa & Middle East", "Atlantic", "North & South America"]
    region_var = tk.StringVar(Signup)
    region_var.set(region_options[0])
    UR = tk.OptionMenu(Signup, region_var, *region_options)
    UR.config(width=20, font=('Arial', 16), bd=5)
    UR.place(x=300, y=515)

    btnS = tk.Button(Signup, text="Enter", font=('Arial', 22), command=Sign_up).place(x=350,y=550)
    tk.Button(Signup, text="Back", font=('Arial', 22), command=lambda: back_to_main(Signup)).place(x=450,y=550)

def close_application():
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        Main.destroy()
        conn.close()

def Start():
    global Main
    Main = tk.Tk()
    Main.title("TV Broadcasting Info")
    Main.geometry("600x400")

    label = tk.Label(Main, text="Main Page", font=('Arial', 24))
    label.pack(pady=20)

    button_frame = tk.Frame(Main)
    button_frame.columnconfigure(0, weight=1)

    btn1 = tk.Button(button_frame, text="Sign in", font=('Arial', 22), command=Sign_In_Page)
    btn2 = tk.Button(button_frame, text="Sign up", font=('Arial', 22), command=Sign_Up_Page)
    btn_exit = tk.Button(button_frame, text="Exit", font=('Arial', 22), command=close_application)

    btn1.grid(row=0, column=0, sticky="news")
    btn2.grid(row=1, column=0, sticky="news")
    btn_exit.grid(row=2, column=0, sticky="news")

    button_frame.pack(pady=100)
    Main.mainloop()

Start()
