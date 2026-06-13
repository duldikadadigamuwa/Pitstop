from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox


def add_new_vehicle(nic, plate_number, model):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return False, "Database Error"

        cursor = connection.cursor()
        
        # Find Customer 
        check_sql = "SELECT customer_id FROM customers WHERE nic = %s"
        cursor.execute(check_sql, (nic,))
        result = cursor.fetchone()

        if result is None:
            return False, "Customer NIC not found"

        customer_id = result[0]
        
        # Insert Vehicle
        sql = "INSERT INTO vehicles (customer_id_fk, plate_number, model) VALUES (%s, %s, %s)"
        cursor.execute(sql, (customer_id, plate_number, model))

        connection.commit()
        cursor.close()
        return True, "Vehicle Added"
    except Exception as e:
        print(f"Error: {e}")
        return False, str(e)

def update_vehicle(vehicle_id, nic, plate_number, model):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return False

        cursor = connection.cursor()
        
        # Check Owner NIC
        cursor.execute("SELECT customer_id FROM customers WHERE nic = %s", (nic,))
        result = cursor.fetchone()
        if not result:
            return False
        
        customer_id = result[0]

        # Update Vehicle
        sql = "UPDATE vehicles SET customer_id_fk=%s, plate_number=%s, model=%s WHERE vehicle_id=%s"
        cursor.execute(sql, (customer_id, plate_number, model, vehicle_id))

        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def delete_vehicle(vehicle_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        sql = "DELETE FROM vehicles WHERE vehicle_id = %s"
        cursor.execute(sql, (vehicle_id,))

        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_all_vehicles():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        sql = """
            SELECT vehicles.vehicle_id, customers.nic, vehicles.plate_number, vehicles.model 
            FROM vehicles
            JOIN customers ON vehicles.customer_id_fk = customers.customer_id
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        cursor.close()
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

#get all plates
def get_all_plates():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        sql = "SELECT plate_number FROM vehicles"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return [row[0] for row in results]
    
    except Exception as e:
        print(f"Error: {e}")
        return []


# UI FUNCTION

def draw_crud_vehicle_screen(app, back_function):
    for widget in app.winfo_children():
        widget.destroy()

    # Header
    ctk.CTkLabel(
        app, text="Manage Vehicles", 
        font=("Arial", 24, "bold"), 
        anchor="w"
    ).pack(fill="x", padx=40, pady=(20, 10))

    # MAIN CONTAINER
    main_container = ctk.CTkFrame(app, fg_color="transparent")
    main_container.pack(padx=40, pady=10, fill="x")

    # LEFT FRAME 
    left_input_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    left_input_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

    # Inputs
    entry_nic = ctk.CTkEntry(left_input_frame, placeholder_text="Owner NIC", height=40)
    entry_nic.pack(fill="x", pady=(0, 10))

    entry_plate = ctk.CTkEntry(left_input_frame, placeholder_text="Plate Number", height=40)
    entry_plate.pack(fill="x", pady=(0, 10))

    entry_model = ctk.CTkEntry(left_input_frame, placeholder_text="Vehicle Model", height=40)
    entry_model.pack(fill="x", pady=(0, 10))
    
  
    selected_vehicle_id = None

    # RIGHT FRAME
    right_btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    right_btn_frame.pack(side="right", fill="y")

    def clear_form():
        nonlocal selected_vehicle_id
        selected_vehicle_id = None
        entry_nic.delete(0, 'end')
        entry_plate.delete(0, 'end')
        entry_model.delete(0, 'end')

    def perform_add():
        success, message = add_new_vehicle(
            entry_nic.get(),
            entry_plate.get(),
            entry_model.get()
        )
        if success:
            messagebox.showinfo("Success", message)
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", message)

    def perform_update():
        if not selected_vehicle_id:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle from the table first.")
            return

        if update_vehicle(selected_vehicle_id, entry_nic.get(), entry_plate.get(), entry_model.get()):
            messagebox.showinfo("Success", "Vehicle Updated!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Update Failed. Check if Owner NIC exists.")

    def perform_delete():
        if not selected_vehicle_id:
            messagebox.showwarning("Select Vehicle", "Please select a vehicle from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this vehicle?"):
            if delete_vehicle(selected_vehicle_id):
                messagebox.showinfo("Deleted", "Vehicle deleted.")
                clear_form()
                refresh_table()
            else:
                messagebox.showerror("Error", "Could not delete vehicle.")

    # Vertical Buttons
    ctk.CTkButton(right_btn_frame, text="Add Vehicle", fg_color="#1e8e3e", hover_color="#15662b", width=140, height=40, command=perform_add).pack(pady=(0, 10))
    ctk.CTkButton(right_btn_frame, text="Update", fg_color="#1a73e8", hover_color="#135abc", width=140, height=40, command=perform_update).pack(pady=(0, 10))
    ctk.CTkButton(right_btn_frame, text="Delete", fg_color="#d93025", hover_color="#a61d12", width=140, height=40, command=perform_delete).pack(pady=(0, 0))

    #Search Section
    search_frame = ctk.CTkFrame(app, fg_color="transparent")
    search_frame.pack(padx=40, pady=10, fill="x")

    entry_search = ctk.CTkEntry(
        search_frame, 
        placeholder_text="Search by Plate / NIC...", 
        height=35
    )
    entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(
        search_frame, text="Search", width=80, 
        command=lambda: refresh_table(entry_search.get())
    ).pack(side="right")

    # Table Section
    header = ctk.CTkFrame(app, height=40, fg_color="#1a73e8")
    header.pack(padx=40, pady=(10, 0), fill="x")

    headers = ["ID", "Owner NIC", "Plate Number", "Model"]
    for h in headers:
        ctk.CTkLabel(
            header, text=h, 
            text_color="white", 
            font=("Arial", 14, "bold")
        ).pack(side="left", expand=True, fill="x")

    table = ctk.CTkScrollableFrame(app)
    table.pack(padx=40, pady=(0, 20), fill="both", expand=True)

    def fill_form_with_row(data):
        clear_form()
        nonlocal selected_vehicle_id
        
        # Save ID to variable
        selected_vehicle_id = data[0]

        # Fill inputs
        entry_nic.insert(0, data[1])
        entry_plate.insert(0, data[2])
        entry_model.insert(0, data[3])

    def refresh_table(search_query=""):
        for widget in table.winfo_children():
            widget.destroy()

        for v in get_all_vehicles():
            # v = (id, nic, plate, model)
            
            if search_query.lower() in str(v).lower():
                row = ctk.CTkFrame(table, fg_color=("gray85", "gray25"), height=35)
                row.pack(fill="x", pady=2)

                # Map data to headers: ID, NIC, Plate, Model
                display_data = [v[0], v[1], v[2], v[3]]

                for item in display_data:
                    ctk.CTkLabel(row, text=str(item)).pack(side="left", expand=True, fill="x")

                row.bind("<Button-1>", lambda e, d=v: fill_form_with_row(d))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, d=v: fill_form_with_row(d))

    refresh_table()

   