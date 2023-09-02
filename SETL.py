import tkinter as ttk
import tkinter as tk
import customtkinter as ctk

root=tk.Tk()
root.geometry("1000x800")
root.configure(bg='#FFF9F1')
root.title("SETL")

#Explore frame
explore_frame = ctk.CTkFrame(master = root, fg_color = "#FBDA8A", corner_radius = 30)
explore_frame.grid(row=0, column=0, sticky="nsew")
explore_frame.configure(width=280)

#prevent the frame resize after add the button option (please do not remove this ^_^)
explore_frame.pack_propagate(False)

#Explore title in Explore frame
explore_title = ctk.CTkLabel(master=explore_frame, text="Explore", fg_color="#FBDA8A", font=("Lato", 30))
explore_title.pack(pady=20)

#Translate in Explore frame button
translate_button = ctk.CTkButton(master=explore_frame, text="Translate", fg_color="#FBDA8A", font=("Lato", 20))
translate_button.pack(pady=10)

#Main frame
main_frame = tk.Frame(root, bg = "#FFF9F1")
main_frame.grid(row=0, column=1, sticky="nsew")


#split the frame in two parts
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

root.mainloop()
