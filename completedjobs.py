from database import connect_to_database
import customtkinter as ctk
from tkinter import messagebox
from reportlab.pdfgen import canvas
import os
from tkinter import filedialog

def get_completed_jobs():
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return []
        
        cursor = connection.cursor()
        sql = """
            SELECT service_orders.order_id, vehicles.plate_number, service_orders.created_date, service_orders.status
            FROM service_orders 
            JOIN vehicles ON service_orders.vehicle_id_fk = vehicles.vehicle_id
            WHERE service_orders.status IN ('Completed', 'Billed')
            ORDER BY service_orders.order_id DESC
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        cursor.close()
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

def mark_job_as_billed(order_id):
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        sql = "UPDATE service_orders SET status = 'Billed' WHERE order_id = %s"
        cursor.execute(sql, (order_id,))
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_billing_details(order_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return None
        
        cursor = connection.cursor()
        sql = """
            SELECT customers.name, customers.address, vehicles.plate_number, vehicles.model, service_orders.problem_description
            FROM service_orders
            JOIN vehicles ON service_orders.vehicle_id_fk = vehicles.vehicle_id
            JOIN customers ON vehicles.customer_id_fk = customers.customer_id
            WHERE service_orders.order_id = %s
        """
        cursor.execute(sql, (order_id,))
        result = cursor.fetchone()
        
        cursor.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_job_parts_total(order_id):
    connection = None
    try:
        connection = connect_to_database()
        if connection is None: return 0.0
        
        cursor = connection.cursor()
        sql = """
            SELECT SUM(unit_price * quantity) 
            FROM order_items 
            WHERE order_id_fk = %s
        """
        cursor.execute(sql, (order_id,))
        result = cursor.fetchone()
        cursor.close()
        return float(result[0]) if result[0] is not None else 0.0
        
    except Exception as e:
        print(f"Error calculating parts: {e}")
        return 0.0


# PDF GENERATOR


def create_pdf(filename, customer, car_plate, model, description, labor_cost, parts_cost):
   #sacve bill location
   
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"Invoice_{customer}.pdf", 
        title="Save Invoice Location"
    )

    if not file_path: 
        return
    try:
        c = canvas.Canvas(filename)
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, 800, "PITSTOP SERVICE BILL")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 770, "----------------------------------------------------------------")
        
        c.drawString(50, 750, f"Customer: {customer}")
        c.drawString(50, 730, f"Vehicle: {model} ({car_plate})")
        c.drawString(50, 710, f"Job Description: {description}")
        
        c.drawString(50, 680, "----------------------------------------------------------------")
        
        c.drawString(50, 650, f"Parts Cost:      Rs {parts_cost}")
        c.drawString(50, 630, f"Labor Charges:   Rs {labor_cost}")
        
        total = float(parts_cost) + float(labor_cost)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 590, f"GRAND TOTAL:     Rs {total}")
        
        c.save()
        return True
    except Exception as e:
        print(f"PDF Error: {e}")
        return False


#  UI SCREENS


def draw_billing_details_screen(app, order_id, back_to_home):
    for widget in app.winfo_children():
        widget.destroy()

    details = get_billing_details(order_id)
    parts_cost = get_job_parts_total(order_id) 

    ctk.CTkLabel(app, text="Billing Details", font=("Arial", 24, "bold")).pack(pady=20)

    info_frame = ctk.CTkFrame(app)
    info_frame.pack(padx=40, pady=10, fill="x")

    ctk.CTkLabel(info_frame, text=f"Order ID: {order_id}", font=("Arial", 14, "bold")).pack(pady=5)
    ctk.CTkLabel(info_frame, text=f"Customer: {details[0]}").pack(pady=2)
    ctk.CTkLabel(info_frame, text=f"Vehicle: {details[3]} ({details[2]})").pack(pady=2)
    ctk.CTkLabel(info_frame, text=f"Issue: {details[4]}").pack(pady=2)

    input_frame = ctk.CTkFrame(app, fg_color="transparent")
    input_frame.pack(pady=20)

    ctk.CTkLabel(input_frame, text="Add Labor Fee (Rs):").pack(pady=5)
    entry_labor = ctk.CTkEntry(input_frame, placeholder_text="Enter amount")
    entry_labor.pack(pady=5)

    def print_bill():
        labor = entry_labor.get()
        if not labor:
            messagebox.showerror("Error", "Please enter labor fee")
            return

        filename = f"Bill_{order_id}.pdf"
        
        success = create_pdf(
            filename, details[0], details[2], details[3], details[4], labor, parts_cost
        )

        if success:
            # Update Database Status to Billed
            mark_job_as_billed(order_id)
            
            messagebox.showinfo("Success", f"Bill Saved as {filename}")
            try:
                os.startfile(filename)
            except:
                pass
            
            #  Go back to the list screen 
            draw_completed_jobs_screen(app, back_to_home)
        else:
            messagebox.showerror("Error", "Could not create PDF")

    ctk.CTkButton(app, text="Print Bill", fg_color="green", command=print_bill).pack(pady=10)


def draw_completed_jobs_screen(app, back_function):
    for widget in app.winfo_children():
        widget.destroy()

    ctk.CTkLabel(app, text="Completed Jobs", font=("Arial", 24, "bold")).pack(pady=20)

    # Table Header 
    header = ctk.CTkFrame(app, height=40, fg_color="#1a73e8")
    header.pack(padx=40, pady=(10, 0), fill="x")

    ctk.CTkLabel(header, text="ID", font=("Arial", 14, "bold"), text_color="white").pack(side="left", expand=True, fill="x")
    ctk.CTkLabel(header, text="Plate Number", font=("Arial", 14, "bold"), text_color="white").pack(side="left", expand=True, fill="x")
    ctk.CTkLabel(header, text="Date", font=("Arial", 14, "bold"), text_color="white").pack(side="left", expand=True, fill="x")
    ctk.CTkLabel(header, text="Status", font=("Arial", 14, "bold"), text_color="white").pack(side="left", expand=True, fill="x") # Added Status Header
    ctk.CTkLabel(header, text="Action", font=("Arial", 14, "bold"), text_color="white").pack(side="left", expand=True, fill="x")

    # JOB LIST
    scroll_frame = ctk.CTkScrollableFrame(app)
    scroll_frame.pack(padx=40, pady=(0, 20), fill="both", expand=True)

    completed_jobs = get_completed_jobs()

    if not completed_jobs:
        ctk.CTkLabel(scroll_frame, text="No completed jobs yet.").pack(pady=20)

    for job in completed_jobs:
        row = ctk.CTkFrame(scroll_frame, fg_color=("gray85", "gray25"), height=40)
        row.pack(fill="x", pady=2)

        ctk.CTkLabel(row, text=str(job[0])).pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(row, text=job[1]).pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(row, text=str(job[2])).pack(side="left", expand=True, fill="x")
        
       
        status_text = job[3] # Completed or Billed
        status_color = "green" if status_text == 'Billed' else "orange"
        ctk.CTkLabel(row, text=status_text, text_color=status_color).pack(side="left", expand=True, fill="x")

        
        if status_text == 'Billed':
            # DISABLED BUTTON 
            btn = ctk.CTkButton(row, text="Done", width=100, state="disabled", fg_color="gray")
        else:
            # ACTIVE BUTTON 
            btn = ctk.CTkButton(row, text="Generate Bill", width=100, fg_color="#E0a800", text_color="black",
                                command=lambda oid=job[0]: draw_billing_details_screen(app, oid, back_function))
        
        btn.pack(side="left", expand=True, fill="x", padx=10)

   


   