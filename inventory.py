from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox


def add_part(name, price, stock):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        sql = "INSERT INTO parts (part_name, price, stock_quantity) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, price, stock))
        
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_part(part_id, name, price, stock):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        sql = "UPDATE parts SET part_name=%s, price=%s, stock_quantity=%s WHERE part_id=%s"
        cursor.execute(sql, (name, price, stock, part_id))
        
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def delete_part(part_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return False
        
        cursor = connection.cursor()
        sql = "DELETE FROM parts WHERE part_id=%s"
        cursor.execute(sql, (part_id,))
        
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_all_parts():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None:
            return []
        
        cursor = connection.cursor()
        sql = "SELECT part_id, part_name, price, stock_quantity FROM parts"
        cursor.execute(sql)
        results = cursor.fetchall()
        
        cursor.close()
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []
    

# UI 
def draw_crud_inventory_screen(app, back_function):
    for widget in app.winfo_children():
        widget.destroy()

    # Header 
    ctk.CTkLabel(
        app, text="Manage Inventory", 
        font=("Arial", 24, "bold"), 
        anchor="w"
    ).pack(fill="x", padx=40, pady=(20, 10))

    # Form Section
    form_frame = ctk.CTkFrame(app, fg_color="transparent")
    form_frame.pack(padx=40, pady=10, fill="x")

    # Input Fields 
    entry_name = ctk.CTkEntry(form_frame, placeholder_text="Part Name", height=40)
    entry_price = ctk.CTkEntry(form_frame, placeholder_text="Price", height=40)
    entry_stock = ctk.CTkEntry(form_frame, placeholder_text="Stock Quantity", height=40)
    
    
    entry_name.grid(row=0, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
    entry_price.grid(row=1, column=0, padx=10, pady=8, sticky="ew")
    entry_stock.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

    form_frame.columnconfigure(0, weight=1)
    form_frame.columnconfigure(1, weight=1)

    # Buttons Section 
    button_frame = ctk.CTkFrame(app, fg_color="transparent")
    button_frame.pack(padx=40, pady=10, fill="x")

    #store invisible id
    selected_part_id = None 

    def clear_form():
        nonlocal selected_part_id
        selected_part_id = None
        
        entry_name.delete(0, 'end')
        entry_price.delete(0, 'end')
        entry_stock.delete(0, 'end')

    def perform_add():
        if add_part(entry_name.get(), entry_price.get(), entry_stock.get()):
            messagebox.showinfo("Success", "Part Added!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Failed to add part.")

    def perform_update():
        if not selected_part_id:
            messagebox.showwarning("Select Part", "Please select a part from the table first.")
            return

        if update_part(selected_part_id, entry_name.get(), entry_price.get(), entry_stock.get()):
            messagebox.showinfo("Success", "Part Updated!")
            clear_form()
            refresh_table()
        else:
            messagebox.showerror("Error", "Update Failed.")

    def perform_delete():
        if not selected_part_id:
            messagebox.showwarning("Select Part", "Please select a part from the table first.")
            return

        if messagebox.askyesno("Confirm", "Delete this part?"):
            if delete_part(selected_part_id):
                messagebox.showinfo("Deleted", "Part deleted.")
                clear_form()
                refresh_table()
            else:
                messagebox.showerror("Error", "Could not delete part.")

    # Buttons 
    ctk.CTkButton(
        button_frame, text="Add Part", 
        fg_color="#1e8e3e", hover_color="#15662b", 
        width=100, height=40, command=perform_add
    ).pack(side="left", expand=True, fill='x', padx=5)
    
    ctk.CTkButton(
        button_frame, text="Update", 
        fg_color="#1a73e8", hover_color="#135abc", 
        width=100, height=40, command=perform_update
    ).pack(side="left", expand=True, fill='x', padx=5)

    ctk.CTkButton(
        button_frame, text="Delete", 
        fg_color="#d93025", hover_color="#a61d12", 
        width=100, height=40, command=perform_delete
    ).pack(side="left", expand=True, fill='x', padx=5)


    # Search 
    search_frame = ctk.CTkFrame(app, fg_color="transparent")
    search_frame.pack(padx=40, pady=10, fill="x")

    entry_search = ctk.CTkEntry(
        search_frame, 
        placeholder_text="Search by Part Name...", 
        height=35
    )
    entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(
        search_frame, text="Search", width=80, 
        command=lambda: refresh_table(entry_search.get())
    ).pack(side="right")

    # Table 
    header = ctk.CTkFrame(app, height=40, fg_color="#1a73e8")
    header.pack(padx=40, pady=(10, 0), fill="x")

    headers = ["ID", "Part Name", "Price", "Stock"]
    
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
        nonlocal selected_part_id
        
        # Data: (0:id, 1:name, 2:price, 3:stock)
        selected_part_id = data[0] 

        entry_name.insert(0, data[1])
        entry_price.insert(0, str(data[2]))
        entry_stock.insert(0, str(data[3]))

    def refresh_table(search_query=""):
        for widget in table.winfo_children():
            widget.destroy()

        for p in get_all_parts():
            # p = (id, name, price, stock)
            
            if search_query.lower() in str(p).lower():
                row = ctk.CTkFrame(table, fg_color=("gray85", "gray25"), height=35)
                row.pack(fill="x", pady=2)

                # Map data to headers: ID, Name, Price, Stock
                display_data = [p[0], p[1], p[2], p[3]]

                for item in display_data:
                    ctk.CTkLabel(row, text=str(item)).pack(side="left", expand=True, fill="x")

                row.bind("<Button-1>", lambda e, d=p: fill_form_with_row(d))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, d=p: fill_form_with_row(d))

    refresh_table()