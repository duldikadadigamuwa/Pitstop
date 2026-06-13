from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox

def add_new_customer(name, email, phone, address, nic):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False

        cursor = connection.cursor()
        sql = "INSERT INTO customers (name, email, phone, address, nic) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (name, email, phone, address, nic))

        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False

def update_customer_info(customer_id, name, email, phone, address, nic):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False

        cursor = connection.cursor()
        sql = """
            UPDATE customers 
            SET name=%s, email=%s, phone=%s, address=%s, nic=%s 
            WHERE customer_id=%s
        """
        cursor.execute(sql, (name, email, phone, address, nic, customer_id))

        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False

def delete_customer(customer_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False
        
        cursor = connection.cursor()
        sql = "DELETE FROM customers WHERE customer_id=%s"
        cursor.execute(sql, (customer_id,))

        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False

def get_all_customers():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        sql = "SELECT customer_id, name, email, phone, address, nic FROM customers ORDER BY customer_id DESC"
        cursor.execute(sql)
        result = cursor.fetchall()
        
        cursor.close()
        return result
    except Exception as e:
        print(f"error : {e}")
        return []


# UI 


def draw_crud_customer_screen(app, back_function):
    for widget in app.winfo_children():
        widget.destroy()

    # Header
    ctk.CTkLabel(
        app, text="Manage Customers", 
        font=("Arial", 24, "bold"), 
        anchor="w"
    ).pack(fill="x", padx=40, pady=(20, 10))

    # MAIN FORM CONTAINER
    form_container = ctk.CTkFrame(app, fg_color="transparent")
    form_container.pack(padx=40, pady=10, fill="x")

    #  CREATE COLUMNS
    left_frame = ctk.CTkFrame(form_container, fg_color="transparent")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

    right_frame = ctk.CTkFrame(form_container, fg_color="transparent")
    right_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

    # LEFT SIDE INPUTS (Name, Email, Phone)
    entry_name = ctk.CTkEntry(left_frame, placeholder_text="Full Name", height=40)
    entry_name.pack(fill="x", pady=(0, 10))

    entry_email = ctk.CTkEntry(left_frame, placeholder_text="Email", height=40)
    entry_email.pack(fill="x", pady=(0, 10))

    entry_phone = ctk.CTkEntry(left_frame, placeholder_text="Phone Number", height=40)
    entry_phone.pack(fill="x", pady=(0, 10))

    # RIGHT SIDE INPUTS (Address, NIC) 
    entry_address = ctk.CTkEntry(right_frame, placeholder_text="Address", height=40)
    entry_address.pack(fill="x", pady=(0, 10))
    
    entry_nic = ctk.CTkEntry(right_frame, placeholder_text="NIC", height=40)
    entry_nic.pack(fill="x", pady=(0, 10))
    

    # BUTTONS SECTION 
    btn_grid = ctk.CTkFrame(right_frame, fg_color="transparent")
    btn_grid.pack(fill="x", pady=(1, 0))

    #  store selected ID invisibly
    selected_customer_id = None

    # LOGIC FUNCTIONS
    def clear_form():
        nonlocal selected_customer_id
        selected_customer_id = None # Reset ID
        for e in [entry_name, entry_email, entry_phone, entry_address, entry_nic]:
            e.delete(0, "end")

    def perform_add():
        if add_new_customer(
            entry_name.get(),
            entry_email.get(),
            entry_phone.get(),
            entry_address.get(),
            entry_nic.get()
        ):
            messagebox.showinfo("Success", "Customer added successfully")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Could not add customer")

    def perform_update():
        if not selected_customer_id:
            messagebox.showwarning("Select Customer", "Please select a customer from the table first.")
            return

        if update_customer_info(
            selected_customer_id, 
            entry_name.get(),
            entry_email.get(),
            entry_phone.get(),
            entry_address.get(),
            entry_nic.get()
        ):
            messagebox.showinfo("Success", "Customer Updated!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Update Failed.")

    def perform_delete():
        if not selected_customer_id:
            messagebox.showwarning("Select Customer", "Please select a customer from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this customer?"):
            if delete_customer(selected_customer_id): # Use variable
                messagebox.showinfo("Deleted", "Customer deleted.")
                clear_form()
                refresh_table()
            else:
                messagebox.showerror("Error", "Could not delete customer.")

   
    
    # Add Button 
    ctk.CTkButton(btn_grid, text="Add", fg_color="#1e8e3e", hover_color="#15662b", 
                  width=100,height=40, command=perform_add).pack(side="left", expand='True' ,fill='x', padx=5)
    
    # Update Button 
    ctk.CTkButton(btn_grid, text="Update", fg_color="#1a73e8", hover_color="#135abc", 
                  width=100,height=40, command=perform_update).pack(side="left",  expand='True' ,fill='x', padx=5)

    #  Delete Button 
    ctk.CTkButton(btn_grid, text="Delete", fg_color="#d93025", hover_color="#a61d12", 
                  width=100,height=40, command=perform_delete).pack(side="left", expand='True' ,fill='x',  padx=5)


    # SEARCH 
    search_frame = ctk.CTkFrame(app, fg_color="transparent")
    search_frame.pack(padx=40, pady=10, fill="x")

    entry_search = ctk.CTkEntry(search_frame, placeholder_text="Search by Name / Email / NIC", height=35)
    entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(search_frame, text="Search", width=80, 
                  command=lambda: refresh_table(entry_search.get())).pack(side="right")

    # TABLE 
    header = ctk.CTkFrame(app, height=40, fg_color="#1a73e8")
    header.pack(padx=40, pady=(10, 0), fill="x")

    headers = ["ID", "Name", "Email", "Phone", "NIC"]
    for h in headers:
        ctk.CTkLabel(header, text=h, text_color="white", font=("Arial", 14, "bold")).pack(side="left", expand=True, fill="x")

    table = ctk.CTkScrollableFrame(app)
    table.pack(padx=40, pady=(0, 20), fill="both", expand=True)

    def fill_form_with_row(data):
        clear_form()
        nonlocal selected_customer_id
        selected_customer_id = data[0] # Store ID 
        
        entry_name.insert(0, data[1])
        entry_email.insert(0, data[2])
        entry_phone.insert(0, data[3])
        entry_address.insert(0, data[4])
        entry_nic.insert(0, data[5])

    def refresh_table(search_query=""):
        for widget in table.winfo_children():
            widget.destroy()

        for c in get_all_customers():
            # c = (id, name, email, phone, addr, nic)
            if search_query.lower() in str(c).lower():
                row = ctk.CTkFrame(table, fg_color=("gray85", "gray25"), height=35)
                row.pack(fill="x", pady=2)

                # Show ID, Name, Email, Phone, NIC
                display_data = [c[0], c[1], c[2], c[3], c[5]]

                for item in display_data:
                    ctk.CTkLabel(row, text=str(item)).pack(side="left", expand=True, fill="x")

                row.bind("<Button-1>", lambda e, d=c: fill_form_with_row(d))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, d=c: fill_form_with_row(d))

    refresh_table()