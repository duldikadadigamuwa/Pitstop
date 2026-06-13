import customtkinter as ctk
from PIL import Image, ImageSequence

# MATCH GIF BACKGROUND COLOR
GIF_BG_COLOR = "#000000"

def draw_loading_screen(app, on_finish_callback):                                                 
    for widget in app.winfo_children():
        widget.destroy()

    app.configure(fg_color=GIF_BG_COLOR)

    # CENTER FRAME
    content_frame = ctk.CTkFrame(app, fg_color=GIF_BG_COLOR)
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    # LOAD GIF DIRECTLY
    frames = []
    try:
        #  Open 
        gif_image = Image.open("loading.gif")

        frames = [
            ctk.CTkImage(
                light_image=frame.convert("RGBA"),
                dark_image=frame.convert("RGBA"), # Added dark_image for safety
                size=(300, 330)
            )
            for frame in ImageSequence.Iterator(gif_image)
        ]

        lbl_animation = ctk.CTkLabel(
            content_frame,
            text="",
            fg_color=GIF_BG_COLOR
        )
        lbl_animation.pack(pady=(0, 20))

    except Exception as e:
        print("GIF ERROR:", e)
        ctk.CTkLabel(content_frame, text="[GIF Missing]", text_color="red").pack(pady=20)

    # LOADING TEXT
    lbl_text = ctk.CTkLabel(
        content_frame,
        text="Starting Engine...",
        font=("Arial", 20, "bold"),
        fg_color=GIF_BG_COLOR
    )
    lbl_text.pack()

    # ANIMATION LOOP
    def animate(frame_index=0, load_progress=0):
        # 1. Update the Picture
        if frames:
            lbl_animation.configure(image=frames[frame_index])
            frame_index = (frame_index + 1) % len(frames)

        # 2. Update the Progress
        if load_progress < 100:
            load_progress += 1

            # Simple text updates
            if load_progress == 30: lbl_text.configure(text="Checking Oil...")
            if load_progress == 60: lbl_text.configure(text="Warming Up...")
            if load_progress == 90: lbl_text.configure(text="Ready!")

            # Run again in 30 milliseconds
            app.after(30, lambda: animate(frame_index, load_progress))
        else:
            # 3. Finished! Reset color and go to login
            app.configure(fg_color=("gray90", "gray20"))
            on_finish_callback()

    animate()