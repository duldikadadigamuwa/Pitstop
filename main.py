import customtkinter as ctk
from tkinter import messagebox
import login              
import loading            
import admin_dashboard    
import mechanic_dashboard 

# main app window
app = ctk.CTk() 
app.after(0, lambda: app.state("zoomed"))
app.title("PitStop")


def start_app():
    login.draw_login_screen(app, on_login_success)

def on_login_success(user_data):
    role = user_data['role']

    #  ADMIN ROUTE 
    if role == 'admin':

        target_function = lambda: admin_dashboard.draw_admin_dashboard(app, user_data, logout=start_app)
        loading.draw_loading_screen(app, target_function)
    
    #  MECHANIC ROUTE 
    elif role == 'mechanic':

        target_function = lambda: mechanic_dashboard.draw_mechanic_dashboard(app, user_data, logout=start_app)
        loading.draw_loading_screen(app, target_function)
    
    # UNKNOWN ROLE 
    else:
        messagebox.showerror("Error", f"Unknown User Role: {role}")

#  MAIN  
if __name__ == "__main__":
    start_app()
    app.mainloop()