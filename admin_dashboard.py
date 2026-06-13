from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageOps, ImageDraw
import customers 
import users
import inventory
import jobcreation
import vehicles
import completedjobs





def get_dashboard_stats():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return (0, 0, 0, 0)
        
        cursor = connection.cursor()
        
        # Count Total Customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_cust = cursor.fetchone()[0]
        
        # Count Active Jobs 
        cursor.execute("SELECT COUNT(*) FROM service_orders WHERE status='Pending'")
        active_jobs = cursor.fetchone()[0]
        
        #  Count Completed Jobs 
        cursor.execute("SELECT COUNT(*) FROM service_orders WHERE status='Completed'")
        completed_jobs = cursor.fetchone()[0]
        
        # Count Low Stock Items 
        cursor.execute("SELECT COUNT(*) FROM parts WHERE stock_quantity < 10")
        low_stock = cursor.fetchone()[0]
        
        cursor.close()
        return (total_cust, active_jobs, completed_jobs, low_stock)
        
    except Exception as e:
        print(f"Stats Error: {e}")
        return (0, 0, 0, 0)




def add_corners(im, rad):
    """Helper to cut rounded corners on an image"""
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im






    #ui

def draw_home_stats(parent, user_data):
    for widget in parent.winfo_children():
        widget.destroy()
    
    try:
        my_image = Image.open("welcome_bg.jpg")
        
        #  Resize
        target_size = (1210, 220) 
        my_image = ImageOps.fit(my_image, target_size, method=Image.Resampling.LANCZOS)
        
        #  CUT THE CORNERS
        my_image = add_corners(my_image, 30) 
        
        banner_img = ctk.CTkImage(light_image=my_image, dark_image=my_image, size=target_size)
        
        header_label = ctk.CTkLabel(
            parent, 
            text=f"Welcome to Pitstop \n {user_data['username']}", 
            font=("Arial", 32, "bold"), 
            text_color="white",
            image=banner_img,
            compound="center",
            fg_color="transparent")

        header_label.pack(pady=(0, 20), padx=20, fill="x") 
        
    except Exception as e:
        print(e)
        ctk.CTkLabel(parent, text=f"Welcome, {user_data['username']}", font=("Arial", 30)).pack(pady=20)

    # Header
    ctk.CTkLabel(parent, text="System Overview", font=("Arial", 28, "bold")).pack(anchor="w", pady=(0, 20))

    # Fetch Real Numbers
    stats = get_dashboard_stats() # (cust, active, completed, low_stock)

    # Stats Grid Container
    stats_grid = ctk.CTkFrame(parent, fg_color="transparent")
    stats_grid.pack(fill="x", pady=10)
    stats_grid.grid_columnconfigure((0, 1), weight=1)

    # Helper for Big Cards
    def big_card(row, col, title, value, color, icon_text):
        card = ctk.CTkFrame(stats_grid, height=140, fg_color=color, corner_radius=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        card.grid_propagate(False)
        
        # Icon
        ctk.CTkLabel(card, text=icon_text, font=("Arial", 40), text_color="white").place(relx=0.85, rely=0.5, anchor="center")
        
        # Text
        ctk.CTkLabel(card, text=value, font=("Arial", 40, "bold"), text_color="white").place(relx=0.1, rely=0.4, anchor="w")
        ctk.CTkLabel(card, text=title, font=("Arial", 16, "bold"), text_color="#f0f0f0").place(relx=0.1, rely=0.7, anchor="w")

    # Row 1
    big_card(0, 0, "TOTAL CUSTOMERS", str(stats[0]), "#2980b9", "👥") # Blue
    big_card(0, 1, "ACTIVE JOBS", str(stats[1]), "#f39c12", "⚙️")    # Orange

    # Row 2
    big_card(1, 0, "COMPLETED JOBS TO BILL ", str(stats[2]), "#27ae60", "✅")  # Green
    big_card(1, 1, "LOW STOCK ALERTS", str(stats[3]), "#c0392b", "⚠️")  # Red



def draw_admin_dashboard(app, user_data, logout):
   
    for widget in app.winfo_children():
        widget.destroy()

    #  Sidebar (Left) + Main Content (Right)
    app.grid_columnconfigure(0, weight=0) 
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)

   
    sidebar = ctk.CTkFrame(app, width=220, corner_radius=0, fg_color="#1f2630")
    sidebar.grid(row=0, column=0, sticky="nswe")
    sidebar.grid_propagate(False) # Stop it from shrinking

    # Title & User Info
    ctk.CTkLabel(sidebar, text="PITSTOP", font=("Arial", 24, "bold"), text_color="#f39c12").pack(pady=(40, 10))
    ctk.CTkLabel(sidebar, text=f"Admin: {user_data['username']}", font=("Arial", 14), text_color="gray").pack(pady=(0, 40))

    # Sidebar Buttons
    def btn(text, cmd):
        return ctk.CTkButton(sidebar, text=text, fg_color="transparent", hover_color="#2c3e50", anchor="center", 
                             font=("Arial", 16, "bold"), height=40, command=cmd)

    # Main frame (Right side)
    main_view = ctk.CTkFrame(app, fg_color="transparent")
    main_view.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    # show new section
    def switch_view(draw_function):
        for widget in main_view.winfo_children(): 
            widget.destroy()
        draw_function(main_view, lambda: draw_home_stats(main_view, user_data))

    # Add Buttons to Sidebar
    btn("Dashboard Home", lambda: draw_home_stats(main_view, user_data)).pack(fill="x", pady=5)
    btn("Manage Customers", lambda: switch_view(customers.draw_crud_customer_screen)).pack(fill="x", pady=5)
    btn("Manage Vehicles", lambda: switch_view(vehicles.draw_crud_vehicle_screen)).pack(fill="x", pady=5)
    btn("Create Job Card", lambda: switch_view(jobcreation.draw_service_order_screen)).pack(fill="x", pady=5)
    btn("Billing & Reports", lambda: switch_view(completedjobs.draw_completed_jobs_screen)).pack(fill="x", pady=5)
    btn("Manage Users", lambda: switch_view(users.draw_crud_users_screen)).pack(fill="x", pady=5)
    btn("Manage Inventory", lambda: switch_view(inventory.draw_crud_inventory_screen)).pack(fill="x", pady=5)
    
    ctk.CTkFrame(sidebar, height=2, fg_color="gray40").pack(fill="x", pady=30, padx=20) # Divider
    ctk.CTkButton(sidebar, text="LOGOUT", fg_color="#c0392b", hover_color="#e74c3c", command=logout).pack(pady=10)

   
    draw_home_stats(main_view, user_data)
