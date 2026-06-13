from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox
from vehicles import get_all_plates

def get_mechanics_dict():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return {}
        cursor = connection.cursor()
        sql = "SELECT user_id, username FROM users WHERE role = 'mechanic'"
        cursor.execute(sql)
        results = cursor.fetchall()
        return {row[1]: row[0] for row in results}
    except Exception as e:
        print(f"Error: {e}")
        return {}
    finally:
        if connection: connection.close()

def create_service_order(plate, description, mechanic_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return False
        cursor = connection.cursor()
        
        # Get Vehicle ID
        sql = "SELECT vehicle_id FROM vehicles WHERE plate_number = %s"
        cursor.execute(sql,(plate,))
        result = cursor.fetchone()
        if not result: return False
        vehicle_id = result[0]

        # Insert Order (Default status = Pending)
        sql = """INSERT INTO service_orders (vehicle_id_fk, mechanic_id_fk, problem_description, status, created_date) 
                 VALUES (%s, %s, %s, 'Pending', NOW())"""
        cursor.execute(sql, (vehicle_id, mechanic_id, description))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection: connection.close()

def update_service_order(order_id, plate, description, mechanic_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return False
        cursor = connection.cursor()
        
        sqlv="SELECT vehicle_id FROM vehicles WHERE plate_number = %s"
        cursor.execute(sqlv ,(plate,))
        result = cursor.fetchone()
        if not result: return False
        vehicle_id = result[0]

        sql = "UPDATE service_orders SET vehicle_id_fk=%s, mechanic_id_fk=%s, problem_description=%s WHERE order_id=%s"
        cursor.execute(sql, (vehicle_id, mechanic_id, description, order_id))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection: connection.close()

def delete_service_order(order_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return False
        cursor = connection.cursor()
        sql = "DELETE FROM service_orders WHERE order_id=%s"
        cursor.execute(sql, (order_id,))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection: connection.close()

def get_all_orders():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return []
        cursor = connection.cursor()
        sql = """SELECT service_orders.order_id, vehicles.plate_number, users.username, service_orders.problem_description, service_orders.status
            FROM service_orders
            JOIN vehicles ON service_orders.vehicle_id_fk = vehicles.vehicle_id
            JOIN users ON service_orders.mechanic_id_fk = users.user_id
            ORDER BY service_orders.order_id DESC"""
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection: connection.close()


#  UI 
def draw_service_order_screen(app, back_function):
    for widget in app.winfo_children():
        widget.destroy()

    # Header
    ctk.CTkLabel(
        app, text="Create Service Job", 
        font=("Arial", 24, "bold"), anchor="w"
    ).pack(fill="x", padx=40, pady=(20, 10))

    # MAIN CONTAINER 
    main_container = ctk.CTkFrame(app, fg_color="transparent")
    main_container.pack(padx=40, pady=10, fill="x")

    #  LEFT FRAME 
    left_input_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    left_input_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

    # Data
    plates_list = get_all_plates()
    mechanics_map = get_mechanics_dict()
    mechanic_names = list(mechanics_map.keys())

    # Input
    combo_plate = ctk.CTkComboBox(left_input_frame, values=plates_list, height=40)
    combo_plate.set("Select Vehicle Plate")
    combo_plate.pack(fill="x", padx=(0,100),pady=(0, 10))

    combo_mechanic = ctk.CTkComboBox(left_input_frame, values=mechanic_names, height=40)
    combo_mechanic.set("Select Mechanic")
    combo_mechanic.pack(fill="x",padx=(0,100), pady=(0, 10))

    entry_desc = ctk.CTkEntry(left_input_frame, placeholder_text="Problem Description", height=40)
    entry_desc.pack(fill="x", padx=(0,100),pady=(0, 10))

    #STORE SELECTED ORDER ID (safety for update/delete)
    selected_order_id = None

    # RIGHT FRAME
    right_btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    right_btn_frame.pack(side="right", fill="y")

    def clear_form():
        nonlocal selected_order_id
        selected_order_id = None
        entry_desc.delete(0, 'end')
        combo_plate.set("Select Vehicle Plate")
        combo_mechanic.set("Select Mechanic")

    def perform_add():
        plate = combo_plate.get()
        mech_name = combo_mechanic.get()
        if plate == "Select Vehicle Plate" or mech_name == "Select Mechanic":
            messagebox.showwarning("Error", "Please select a Plate and Mechanic")
            return

        if create_service_order(plate, entry_desc.get(), mechanics_map.get(mech_name)):
            messagebox.showinfo("Success", "Job Created!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Failed.")

    def perform_update():
        if not selected_order_id:
            messagebox.showwarning("Selection", "Select a job from the table first.")
            return

        mech_name = combo_mechanic.get()
        if update_service_order(selected_order_id, combo_plate.get(), entry_desc.get(), mechanics_map.get(mech_name)):
            messagebox.showinfo("Success", "Job Updated!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Update Failed.")

    def perform_delete():
        if not selected_order_id:
            messagebox.showwarning("Selection", "Select a job from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this job?"):
            if delete_service_order(selected_order_id):
                messagebox.showinfo("Deleted", "Job deleted.")
                clear_form()
                refresh_table()

    # Buttons
    ctk.CTkButton(right_btn_frame, text="Create Job", fg_color="#1e8e3e", hover_color="#15662b", width=140, height=40, command=perform_add).pack(pady=(0, 10))
    ctk.CTkButton(right_btn_frame, text="Update", fg_color="#1a73e8", hover_color="#135abc", width=140, height=40, command=perform_update).pack(pady=(0, 10))
    ctk.CTkButton(right_btn_frame, text="Delete", fg_color="#d93025", hover_color="#a61d12", width=140, height=40, command=perform_delete).pack(pady=(0, 0))

    # Search 
    search_frame = ctk.CTkFrame(app, fg_color="transparent")
    search_frame.pack(padx=40, pady=10, fill="x")

    entry_search = ctk.CTkEntry(search_frame, placeholder_text="Search...", height=35)
    entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(search_frame, text="Search", width=80, command=lambda: refresh_table(entry_search.get())).pack(side="right")

    # Table
    header = ctk.CTkFrame(app, height=40, fg_color="#1a73e8")
    header.pack(padx=40, pady=(10, 0), fill="x")

    headers = ["ID", "Plate", "Mechanic", "Description", "Status"]
    for h in headers:
        ctk.CTkLabel(header, text=h, text_color="white", font=("Arial", 14, "bold")).pack(side="left", expand=True, fill="x")

    table = ctk.CTkScrollableFrame(app)
    table.pack(padx=40, pady=(0, 20), fill="both", expand=True)

    def fill_form_with_row(data):
        clear_form()
        nonlocal selected_order_id
        
       
        selected_order_id = data[0]

        combo_plate.set(data[1])
        combo_mechanic.set(data[2])
        entry_desc.insert(0, data[3])
       

    def refresh_table(search_query=""):
        for widget in table.winfo_children():
            widget.destroy()

        for row_data in get_all_orders():
            if search_query.lower() in str(row_data).lower():
                row = ctk.CTkFrame(table, fg_color=("gray85", "gray25"), height=35)
                row.pack(fill="x", pady=2)

                # Show ID, Plate, Mechanic, Description, Status
                display_data = [row_data[0], row_data[1], row_data[2], row_data[3], row_data[4]]

                for item in display_data:
                    ctk.CTkLabel(row, text=str(item)).pack(side="left", expand=True, fill="x")

                row.bind("<Button-1>", lambda e, d=row_data: fill_form_with_row(d))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, d=row_data: fill_form_with_row(d))

    refresh_table()

    