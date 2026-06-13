from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox

#  DATABASE FUNCTIONS
def add_new_user(username, password, role, full_name, nic, phone, address):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False

        cursor = connection.cursor()
        sql = """
            INSERT INTO users (username, password, role, full_name, nic, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (username, password, role, full_name, nic, phone, address))
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False


def get_user_by_nic(nic):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False

        cursor = connection.cursor()
        sql = """
            SELECT username, role, full_name, nic, password, phone, address
            FROM users WHERE nic=%s
        """
        cursor.execute(sql, (nic,))
        result = cursor.fetchone()
        cursor.close()
        return result
    except Exception as e:
        print(f"error : {e}")
        return False


def update_user_info(o_nic, username, password, role, full_name, phone, address, n_nic):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False

        cursor = connection.cursor()
        sql = """
            UPDATE users
            SET username=%s, password=%s, role=%s, full_name=%s,
                phone=%s, address=%s, nic=%s
            WHERE nic=%s
        """
        cursor.execute(
            sql,
            (username, password, role, full_name, phone, address, n_nic, o_nic)
        )
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False


def delete_user(nic):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            print("error : could not connect to database")
            return False

        cursor = connection.cursor()
        sql = "DELETE FROM users WHERE nic=%s"
        cursor.execute(sql, (nic,))
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"error : {e}")
        return False


def get_all_users():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return []

        cursor = connection.cursor()
        sql = """
            SELECT user_id, username, role, full_name, nic, password, phone, address
            FROM users
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        print(f"error : {e}")
        return []



# UI 

def draw_crud_users_screen(app, back_function):
    for widget in app.winfo_children():
        widget.destroy()

    # Header
    ctk.CTkLabel(
        app, text="Manage Users",
        font=("Arial", 24, "bold"),
        anchor="w"
    ).pack(fill="x", padx=40, pady=(20, 10))

    # MAIN CONTAINER 
    form_container = ctk.CTkFrame(app, fg_color="transparent")
    form_container.pack(padx=40, pady=10, fill="x")

    # LEFT AND RIGHT FRAMES
    left_frame = ctk.CTkFrame(form_container, fg_color="transparent")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

    right_frame = ctk.CTkFrame(form_container, fg_color="transparent")
    right_frame.pack(side="right", fill="both", expand=True)

    # LEFT SIDE INPUTS
    entry_fullname = ctk.CTkEntry(left_frame, placeholder_text="Full Name", height=40)
    entry_fullname.pack(fill="x", pady=(0, 10))

    entry_nic = ctk.CTkEntry(left_frame, placeholder_text="NIC", height=40)
    entry_nic.pack(fill="x", pady=(0, 10))

    entry_phone = ctk.CTkEntry(left_frame, placeholder_text="Phone Number", height=40)
    entry_phone.pack(fill="x", pady=(0, 10))

    entry_address = ctk.CTkEntry(left_frame, placeholder_text="Address", height=40)
    entry_address.pack(fill="x", pady=(0, 10))

    #  RIGHT SIDE INPUTS
    entry_username = ctk.CTkEntry(right_frame, placeholder_text="Username", height=40)
    entry_username.pack(fill="x", pady=(0, 10))

    entry_password = ctk.CTkEntry(right_frame, placeholder_text="Password", height=40)
    entry_password.pack(fill="x", pady=(0, 10))

    entry_role = ctk.CTkComboBox(right_frame, values=["admin", "mechanic"], height=40)
    entry_role.set("Select Role")
    entry_role.pack(fill="x", pady=(0, 10))
    
    # BUTTONS GRID
    btn_grid = ctk.CTkFrame(right_frame, fg_color="transparent")
    btn_grid.pack(fill="x", pady=(0, 0)) 

    # store the selected users NIC 
    selected_user_nic = None


    def clear_form():
        nonlocal selected_user_nic
        selected_user_nic = None
        
        for e in [entry_fullname, entry_nic, entry_phone, entry_address, entry_username, entry_password]:
            e.delete(0, "end")
        entry_role.set("Select Role")

    def perform_add():
        if add_new_user(
            entry_username.get(),
            entry_password.get(),
            entry_role.get(),
            entry_fullname.get(),
            entry_nic.get(),
            entry_phone.get(),
            entry_address.get()
        ):
            messagebox.showinfo("Success", "User added successfully")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Could not add user")

    def perform_update():
        if not selected_user_nic:
            messagebox.showwarning("Select User", "Please select a user from the table first.")
            return

        if update_user_info(
            selected_user_nic,          # Old NIC to find the row
            entry_username.get(),
            entry_password.get(),
            entry_role.get(),
            entry_fullname.get(),
            entry_phone.get(),
            entry_address.get(),
            entry_nic.get()             # New NIC to update
        ):
            messagebox.showinfo("Success", "User Updated!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Update Failed.")

    def perform_delete():
        if not selected_user_nic:
            messagebox.showwarning("Select User", "Please select a user from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this user?"):
            if delete_user(selected_user_nic):
                messagebox.showinfo("Deleted", "User deleted.")
                clear_form()
                refresh_table()
            else:
                messagebox.showerror("Error", "Could not delete user.")

    #  BUTTONS
    ctk.CTkButton(btn_grid, text="Add", fg_color="#1e8e3e", hover_color="#15662b", 
                  width=80, height=40, command=perform_add).pack(side="left", padx=(0, 5), expand=True, fill="x")
    
    ctk.CTkButton(btn_grid, text="Update", fg_color="#1a73e8", hover_color="#135abc", 
                  width=80, height=40, command=perform_update).pack(side="left", padx=(0, 5), expand=True, fill="x")

    ctk.CTkButton(btn_grid, text="Delete", fg_color="#d93025", hover_color="#a61d12", 
                  width=80, height=40, command=perform_delete).pack(side="left", padx=(0, 0), expand=True, fill="x")


    # SEARCH 
    search_frame = ctk.CTkFrame(app, fg_color="transparent")
    search_frame.pack(padx=40, pady=10, fill="x")

    entry_search = ctk.CTkEntry(
        search_frame,
        placeholder_text="Search by Name / Username / NIC",
        height=35
    )
    entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(
        search_frame, text="Search", width=80,
        command=lambda: refresh_table(entry_search.get())
    ).pack(side="right")


    # TABLE 
    header = ctk.CTkFrame(app, height=40, fg_color="#1a73e8")
    header.pack(padx=40, pady=(10, 0), fill="x")

    headers = ["Username", "Role", "Full Name", "NIC", "Phone"]
    
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
        nonlocal selected_user_nic
        # data = (id, user, role, name, nic, pass, phone, addr)
        
        selected_user_nic = data[4]  

        entry_username.insert(0, data[1])
        entry_role.set(data[2])
        entry_fullname.insert(0, data[3])
        entry_nic.insert(0, data[4])
        entry_password.insert(0, data[5])
        entry_phone.insert(0, data[6])
        entry_address.insert(0, data[7])

    def refresh_table(search_query=""):
        for widget in table.winfo_children():
            widget.destroy()

        for u in get_all_users():
            # u = (id, user, role, name, nic, pass, phone, addr)
            
            if search_query.lower() in str(u).lower():
                row = ctk.CTkFrame(table, fg_color=("gray85", "gray25"), height=35)
                row.pack(fill="x", pady=2)
                
                # display Username, Role, FullName, NIC, Phone
                display_data = [u[1], u[2], u[3], u[4], u[6]]

                for item in display_data:
                    ctk.CTkLabel(row, text=str(item)).pack(side="left", expand=True, fill="x")

                row.bind("<Button-1>", lambda e, d=u: fill_form_with_row(d))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, d=u: fill_form_with_row(d))

    refresh_table()

   