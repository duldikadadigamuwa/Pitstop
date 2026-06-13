from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageOps, ImageDraw
import inventory


def get_mechanic_history(mechanic_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return []
        cursor = connection.cursor()
        
        # Fetching finished jobs
        sql = """
            SELECT service_orders.order_id, vehicles.plate_number, vehicles.model, service_orders.created_date
            FROM service_orders
            JOIN vehicles ON service_orders.vehicle_id_fk = vehicles.vehicle_id
            WHERE service_orders.mechanic_id_fk = %s AND service_orders.status = 'Completed'
            ORDER BY service_orders.order_id DESC
        """
        cursor.execute(sql, (mechanic_id,))
        results = cursor.fetchall()
        connection.commit()
        cursor.close()
        return results
    except Exception as e:
        print(f"error : {e}")
        return []

def get_mechanic_jobs(mechanic_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return []
        cursor = connection.cursor()
        sql = """
            SELECT service_orders.order_id, vehicles.plate_number, service_orders.problem_description, service_orders.status
            FROM service_orders
            JOIN vehicles ON service_orders.vehicle_id_fk = vehicles.vehicle_id
            WHERE service_orders.mechanic_id_fk = %s AND service_orders.status = 'Pending'
            ORDER BY service_orders.order_id DESC
        """
        cursor.execute(sql, (mechanic_id,))
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        print(f"error : {e}")
        return []

def get_mechanic_stats(mechanic_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return (0, 0)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM service_orders WHERE mechanic_id_fk = %s AND status = 'Pending'", (mechanic_id,))
        pending = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM service_orders WHERE mechanic_id_fk = %s AND status = 'Completed'", (mechanic_id,))
        completed = cursor.fetchone()[0]
        connection.commit
        cursor.close()
        return (pending, completed)
    except:
        return (0, 0)

def add_part_to_job(order_id, part_name, quantity):

    if  part_name == "Select Part":
        messagebox.showerror("Error", "Please select a valid part from the list.")
        return False
        
    if quantity == "":
        messagebox.showerror("Error", "Please enter a quantity.")
        return False
        
    if not quantity.isdigit() or int(quantity) <= 0:
        messagebox.showerror("Error", "Quantity must be a valid number greater than 0.")
        return False
    
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return False

        cursor = connection.cursor()
        sql_find = "SELECT part_id, price, stock_quantity FROM parts WHERE part_name = %s"
        cursor.execute(sql_find, (part_name,))
        part = cursor.fetchone()
        
        if not part:
            return False 

        part_id, price, current_stock = part
        qty = int(quantity)

        # 2. Check Stock
        if current_stock < qty:
            messagebox.showerror("Error", "Insufficient Stock!")
            return False
        
        # Updates stock
        cursor.execute("UPDATE parts SET stock_quantity = stock_quantity - %s WHERE part_id = %s", (qty, part_id))
        
        # Adds item to job
        sql_insert = "INSERT INTO order_items (order_id_fk, part_id_fk, quantity, unit_price) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert, (order_id, part_id, qty, price))

        connection.commit()
        cursor.close()
        return True 

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection: connection.close()

def update_job_status(order_id, status):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return False
        cursor = connection.cursor()
        cursor.execute("UPDATE service_orders SET status = %s WHERE order_id = %s", (status, order_id))
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False


#crop the welcome bg image
def add_corners(im, rad):
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


# UI DRAWING


def draw_mechanic_dashboard(app, user_data, logout):
    for widget in app.winfo_children():
        widget.destroy()

    
    app.grid_columnconfigure(0, weight=0) # Sidebar
    app.grid_columnconfigure(1, weight=1) # Content
    app.grid_rowconfigure(0, weight=1)

    
    def render_job_cards(parent_scroll_frame, refresh_callback):
        my_jobs = get_mechanic_jobs(user_data['user_id'])
        if not my_jobs:
            ctk.CTkLabel(parent_scroll_frame, text="✅ No active tasks.", font=("Arial", 20, "bold"), text_color="gray").pack(pady=50)
            return

        for job in my_jobs:
            card = ctk.CTkFrame(parent_scroll_frame, fg_color=("white", "#2b2b2b"), corner_radius=10)
            card.pack(fill='x', pady=10, padx=5)

            # Header
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=15)
            ctk.CTkLabel(header, text=f"#{job[0]}", font=("Arial", 12, "bold"), text_color="gray").pack(side="left") #job id
            ctk.CTkLabel(header, text=job[1], font=('Arial', 20, 'bold')).pack(side="left", padx=15)#plate
            ctk.CTkLabel(header, text="PENDING", text_color="#f39c12", font=("Arial", 12, "bold")).pack(side="right")#status
            
            # issue
            ctk.CTkLabel(card, text=f"Issue: {job[2]}", font=('Arial', 14), text_color="gray", anchor="w").pack(fill="x", padx=15, pady=(0, 10))

            # Actions
            actions = ctk.CTkFrame(card, fg_color=("#f0f0f0", "#1f1f1f"), corner_radius=5)
            actions.pack(fill="x", padx=10, pady=10)

            all_parts = inventory.get_all_parts()
            part_names = [p[1] for p in all_parts] if all_parts else []

            combo = ctk.CTkComboBox(actions, values=part_names, width=150)
            combo.set("Select Part")
            combo.pack(side='left', padx=10, pady=10)
            entry = ctk.CTkEntry(actions, placeholder_text='Qty', width=50)
            entry.pack(side='left', padx=5)

            def _add(o=job[0], c=combo, e=entry):
                if add_part_to_job(o, c.get(), e.get()):
                    messagebox.showinfo("Success", "Part Added")
                    c.set("Select Part"); e.delete(0,'end')

            def _done(o=job[0]):
                if messagebox.askyesno("Confirm", "Job Complete?"):
                    if update_job_status(o, 'Completed'):
                        refresh_callback() # Reloads the current view

            ctk.CTkButton(actions, text="+", width=40, command=_add).pack(side='left', padx=5)
            ctk.CTkButton(actions, text="Done ✅", width=80, fg_color="green", command=_done).pack(side='right', padx=10)


    # SIDEBAR
    sidebar = ctk.CTkFrame(app, width=220, corner_radius=0, fg_color="#1f2630")
    sidebar.grid(row=0, column=0, sticky="nswe")
    sidebar.grid_propagate(False)

    ctk.CTkLabel(sidebar, text="PITSTOP\nMECHANIC", font=("Arial", 20, "bold"), text_color="#f39c12").pack(pady=(40, 10))
    ctk.CTkLabel(sidebar, text=f"User: {user_data['username']}", font=("Arial", 14), text_color="gray").pack(pady=(0, 30))

    #  switch views
    def switch_view(view_func):
        for widget in main_view.winfo_children():
            widget.destroy()
        view_func()

   
    def sidebar_btn(text, command):
        
        btn = ctk.CTkButton(sidebar, text=f"  {text}", anchor="center", fg_color="transparent", 
                            hover_color="#2c3e50", height=40, font=("Arial", 14, "bold"), command=command)
        btn.pack(fill="x", pady=5)

    
    sidebar_btn("Dashboard", lambda: switch_view(show_home))
    sidebar_btn("Active Jobs", lambda: switch_view(show_active_jobs))
    sidebar_btn("Job History", lambda: switch_view(show_history))
    
    ctk.CTkFrame(sidebar, height=2, fg_color="gray40").pack(fill="x", pady=30, padx=20) 
    ctk.CTkButton(sidebar, text="Logout", fg_color="#c0392b", hover_color="#e74c3c", command=logout).pack(side="bottom", pady=30, padx=20, fill="x")

    #MAIN CONTENT
    main_view = ctk.CTkFrame(app, fg_color="transparent")
    main_view.grid(row=0, column=1, sticky="nswe", padx=20, pady=10)

   
    def show_home():
        
        try:
            my_image = Image.open("welcome_bg.jpg")
            target_size = (1210, 220) 
            my_image = ImageOps.fit(my_image, target_size, method=Image.Resampling.LANCZOS)
            my_image = add_corners(my_image, 25)
            banner_img = ctk.CTkImage( dark_image=my_image, size=target_size)
            ctk.CTkLabel(main_view, text="Mechanic Workstation", font=("Arial", 28, "bold"), text_color="white",
                image=banner_img, compound="center", fg_color="transparent").pack(fill="x", pady=(10, 20))
        except:
            ctk.CTkLabel(main_view, text="Mechanic Dashboard", font=("Arial", 28, "bold")).pack(pady=20)

        # B. Stats
        stats = get_mechanic_stats(user_data['user_id'])
        stats_frame = ctk.CTkFrame(main_view, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        def draw_stat(col, title, value, color, icon):
            card = ctk.CTkFrame(stats_frame, height=90, fg_color=color, corner_radius=15)
            card.grid(row=0, column=col, padx=10, sticky="ew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=icon, font=("Arial", 28), text_color="white").place(relx=0.88, rely=0.5, anchor="center")
            ctk.CTkLabel(card, text=str(value), font=("Arial", 32, "bold"), text_color="white").place(relx=0.08, rely=0.4, anchor="w")
            ctk.CTkLabel(card, text=title, font=("Arial", 12, "bold"), text_color="#f0f0f0").place(relx=0.08, rely=0.75, anchor="w")

        draw_stat(0, "PENDING JOBS", stats[0], "#f39c12", "⚙️")                                                                                                                                                                                                                                                 
        draw_stat(1, "JOBS COMPLETED", stats[1], "#27ae60", "✅")

       
        ctk.CTkLabel(main_view, text="Active Tasks Overview", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(0, 5))
        scroll_frame = ctk.CTkScrollableFrame(main_view, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True)
        
       
        render_job_cards(scroll_frame, lambda: draw_mechanic_dashboard(app, user_data, logout))

   #active jobs view
    def show_active_jobs():
        ctk.CTkLabel(main_view, text="Active Job List", font=("Arial", 24, "bold")).pack(anchor="w", pady=(20, 20))
        
        scroll_frame = ctk.CTkScrollableFrame(main_view, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True)

       
        render_job_cards(scroll_frame, show_active_jobs)

        #job history view
    def show_history():
        ctk.CTkLabel(main_view, text="My Job History", font=("Arial", 24, "bold")).pack(anchor="w", pady=(20, 20))

        # Header
        header = ctk.CTkFrame(main_view, height=40, fg_color="#34495e")
        header.pack(fill="x", padx=5)
        cols = ["ID", "Plate", "Model", "Date", "Status"]
        for c in cols:
            ctk.CTkLabel(header, text=c, font=("Arial", 12, "bold"), text_color="white").pack(side="left", expand=True)

        scroll_frame = ctk.CTkScrollableFrame(main_view, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True, pady=10)

        history = get_mechanic_history(user_data['user_id'])

        if not history:
            ctk.CTkLabel(scroll_frame, text="No completed jobs found.", text_color="gray").pack(pady=50)
        else:
            for job in history:
                row = ctk.CTkFrame(scroll_frame, fg_color=("white", "#2b2b2b"))
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=str(job[0])).pack(side="left", expand=True, pady=10)
                ctk.CTkLabel(row, text=job[1], font=("Arial", 12, "bold")).pack(side="left", expand=True)
                ctk.CTkLabel(row, text=job[2]).pack(side="left", expand=True)
                ctk.CTkLabel(row, text=str(job[3])).pack(side="left", expand=True)
                ctk.CTkLabel(row, text="COMPLETED", text_color="green", font=("Arial", 10, "bold")).pack(side="left", expand=True)

   
    show_home()







