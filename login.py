from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox
ctk.set_default_color_theme('green')

def validate_login(username, password):
    connection = connect_to_database()
    if connection is None:
        print("error: could not connect to database")
        return False
    
    cursor = connection.cursor(dictionary=True)

    sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    values = (username, password)

    try:
        cursor.execute(sql, values)
        user_data = cursor.fetchone()
        return user_data 
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
   

def draw_login_screen(app, login):
    app.geometry("400x400")
    app.title('Pitstop')
    ctk.set_appearance_mode('system')

    for widget in app.winfo_children():
        widget.destroy()

    #  CENTER THE MAIN FRAME
 
    frame = ctk.CTkFrame(app, width=350, height=400, corner_radius=15, fg_color='transparent')
    frame.place(relx=0.5, rely=0.5, anchor="center")
    

    lbl_title = ctk.CTkLabel(frame, text='LOGIN', font=('arial', 26, 'bold'))
    lbl_title.pack(pady=(20, 30)) 
   
    entry_user = ctk.CTkEntry(frame, placeholder_text='Username', width=220, height=35)
    entry_user.pack(pady=10)

    enrty_pw = ctk.CTkEntry(frame, placeholder_text='Password', width=220, height=35, show='*')
    enrty_pw.pack(pady=10)


    def attempt_login():
        username = entry_user.get()
        password = enrty_pw.get()
        
        if not username or not password:
            messagebox.showwarning("Missing information", "Please enter both username and password.")
            return
        
        user_data = validate_login(username, password)

        if user_data:
            login(user_data)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


    btn_login = ctk.CTkButton(frame, text='Login', command=attempt_login, width=220, height=35)
    btn_login.pack(pady=30)