# Import module
import customtkinter as ctk
from tkinter import *
import pyautogui
from pynput import keyboard, mouse
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
from PIL import Image, ImageTk, ImageGrab, ImageDraw
import time
from datetime import datetime
import os
import threading
import tkinter as tk
import keyboard

# Create App class
class App(ctk.CTk):
    # Layout of the GUI will be written in the init itself
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.script_running = False 
        self.stop_event = threading.Event()      
        # Sets the title of our window to "App"
        self.title("YouTube skipper")
        self.setup_window_properties()
        # Dimensions of the window will be 350x225
        window_width = 350
        window_height = 225
        # Získanie rozlíšenia obrazovky
        self.screen_width, self.screen_height = pyautogui.size()
        x = (self.screen_width - window_width) // 2
        y = self.screen_height // 2 - window_height
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # Inicializujte premennú pre sledovanie stavu
        self.button_clicked = False                
        # Create a label with text (vrátane info o ESC)
        label = ctk.CTkLabel(self, text="Author: robopol.sk\nThe script automatically skips YouTube ads.\nPress 'ESC' to stop script at any time.")
        label.pack(pady=10)  # Adjust pady as needed
        
        # Create a frame to contain the buttons
        button_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        button_frame.pack()
        # Create "Start" button
        start_button = ctk.CTkButton(button_frame, text="Start", command=self.start_action,corner_radius=6)
        start_button.grid(row=0, column=0, pady=(10, 0), padx=10)
        # Create "Stop" button
        stop_button = ctk.CTkButton(button_frame, text="Stop", command=self.stop_action,corner_radius=6)
        stop_button.grid(row=0, column=1, pady=(10, 0), padx=10)
        # Create CTkTextbox below the buttons
        self.textbox = ctk.CTkTextbox(self, width=300, height=60, border_color="gray", border_width=1, corner_radius=3, fg_color="transparent")
        self.textbox.pack(pady=10)       
        
        # Create "Configure" button
        button_frame_1 = ctk.CTkFrame(master=self, fg_color="transparent")
        button_frame_1.pack()
        configure_button = ctk.CTkButton(button_frame_1, text="Configure", command=self.button_click_handler, corner_radius=6)
        configure_button.grid(row=0, column=0)
        # Vytvorenie inštancie ovládača myši a klavesnice
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Pripojte klávesnicu na metódu on_key_press pre stlačenie klávesy F8 a ESC
        self.bind_keys()
        self.setup_ui()
        self.canvas_1=None
        self.Image_on=0

    def bind_keys(self):
        keyboard.on_press_key("F8", self.on_key_press)
        keyboard.on_press_key("esc", self.on_esc_press)  # ESC key to stop

    def on_esc_press(self, event):
        # Stop the script if running
        if self.script_running:
            self.script_running = False
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", "Script was stopped by pressing ESC.\n")

    def button_click_handler(self):
        # Ak tlačidlo ešte nebolo stlačené
        if self.button_clicked == False:            
            # Ak skript beží a užívateľ stlačí configure, zastav skript
            if self.script_running:
                self.script_running = False
                self.textbox.delete("0.0","end")
                self.textbox.insert("0.0", "Script stopped because user pressed Configure.\n")
            # Vykonajte configure_action
            self.configure_action()
            self.textbox.insert("0.0", f"Your resolution is: {self.screen_width} x {self.screen_height} px.\n")
            self.textbox.insert("0.0", "Initial white threshold level is set to R, G, B = 200.\n")
            self.textbox.insert("0.0", "Time should be entered in the format hh:mm, for example, 07:45.\n")                        
            self.button_clicked = True
        else:            
            # Inicializujte základné okno
            self.initialize_base_window()
            self.button_clicked = False
            self.script_running=False

    def on_key_press(self, key):
        # Získání hodnot z Entry polí x_entry a y_entry
        if self.canvas_1 is not None:
            self.x_value = self.x_entry.get()
            self.y_value = self.y_entry.get()            
            # Kontrola, či sú platné integer hodnoty
            if not (self.x_value and self.y_value and self.x_value.isdigit() and self.y_value.isdigit()):
                self.textbox.delete("0.0", "end")
                self.textbox.insert("0.0", "Enter integer values for x and y coordinates.\n")
                return
            # Prevod na integer
            self.x_coordinate = int(self.x_value)
            self.y_coordinate = int(self.y_value)                               
            # Zachytte malý screenshot
            self.screenshot = ImageGrab.grab(bbox=(self.x_coordinate - self.area_width // 2, self.y_coordinate - self.area_height // 2, self.x_coordinate + self.area_width // 2, self.y_coordinate + self.area_height // 2))
            self.tk_image_1 = ImageTk.PhotoImage(self.screenshot)
            self.screenshot.save("your_screen.png")
            
            # Aktualizácia malého obrázka
            width, height = self.screenshot.size
            if hasattr(self, "canvas_1_image"):
                self.canvas_1.delete(self.canvas_1_image)            
            self.canvas_1_image = self.canvas_1.create_image(0, 0, anchor="nw", image=self.tk_image_1)
            self.canvas_1.config(width=width, height=height)
            self.canvas_1.itemconfig(self.canvas_1_image, image=self.tk_image_1)

            # Spravíme veľký screenshot celej obrazovky
            big_screenshot = ImageGrab.grab()
            draw = ImageDraw.Draw(big_screenshot)
            # Nakreslíme malý červený štvorček v mieste malého screenshotu
            rect_x1 = self.x_coordinate - self.area_width // 2
            rect_y1 = self.y_coordinate - self.area_height // 2
            rect_x2 = self.x_coordinate + self.area_width // 2
            rect_y2 = self.y_coordinate + self.area_height // 2
            draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], outline="red", width=3)

            big_screenshot.save("big_screenshot.png")
            # Otvoríme big_screenshot v prehliadači
            big_screenshot.show()

            self.Image_on=1

    def save_function(self):
        self.textbox.delete("0.0", "end")
        # Získání hodnot z Entry polí x_entry a y_entry
        self.x_value = self.x_entry.get()
        self.y_value = self.y_entry.get()
        self.center_x=int(self.x_value)
        self.center_y=int(self.y_value)
        # Kontrola, zda jsou vstupy celočíselné hodnoty
        if not (self.x_value and self.y_value and self.x_value.isdigit() and self.y_value.isdigit()):
            self.textbox.insert("0.0", "Enter integer values for x and y coordinates.\n")
            return
        # Získanie thresholdu
        self.threshold_value = self.threshold_entry.get()
        if not (self.threshold_value and self.threshold_value.isdigit()):
            self.textbox.insert("0.0", "White threshold must be an integer.\n")
            return
        self.threshold_value = int(self.threshold_value)
        # Získanie shutdown time
        shutdown_time_str = self.shutdown_entry.get()
        try:
            if shutdown_time_str:
                shutdown_datetime = datetime.strptime(shutdown_time_str, "%H:%M")
                shutdown_time = shutdown_datetime.time()
            else:
                shutdown_time = None
        except ValueError:
            self.textbox.insert("0.0", "Time must be in the format HH:MM.\n")
            return
        self.shutdown_time = shutdown_time

        # Namiesto použitia self.screenshot načítame 'your_screen.png' znova
        try:
            saved_image = Image.open("your_screen.png")
        except FileNotFoundError:
            self.textbox.insert("0.0", "your_screen.png not found, press F8 first.\n")
            return

        # výpočet self.saved_binary_values pre your_screen
        pixel_colors = list(self.screenshot.getdata())            
        self.saved_binary_values = [1 if self.is_color_close_to_white(color) else 0 for color in pixel_colors]

        # uloženie údajov do setting.txt
        with open("setting.txt", "w") as file:
            file.write(f"{self.x_value}\n")
            file.write(f"{self.y_value}\n")
            file.write(f"{', '.join(map(str, self.saved_binary_values))}\n")
            file.write(f"{self.threshold_value}\n")
            if self.shutdown_time is not None:
                file.write(f"{self.shutdown_time.strftime('%H:%M')}\n")
            else:
                file.write("\n")

        # Teraz porovnáme correct_screen s your_screen
        if os.path.exists("correct_screen.png"):
            correct_img = Image.open("correct_screen.png")
            correct_pixels = list(correct_img.getdata())
            correct_binary = [1 if self.is_color_close_to_white(color) else 0 for color in correct_pixels]

            if len(correct_binary) == len(self.saved_binary_values):
                match_count = sum(1 for a,b in zip(correct_binary, self.saved_binary_values) if a == b)
                match_ratio = match_count / len(correct_binary)
                match_percent = match_ratio * 100
                if match_ratio < 0.9:
                    self.textbox.insert("0.0", f"The patterns match only {match_percent:.2f}%.\n")
                else:
                    self.textbox.insert("0.0", f"The patterns match {match_percent:.2f}%.\n")
            else:
                self.textbox.insert("0.0", "Cannot compare screens: dimensions differ.\n")
        else:
            self.textbox.insert("0.0", "correct_screen.png not found for comparison.\n")

        self.textbox.insert("0.0", "Data saved to setting.txt.\n")

    def initialize_base_window(self):
        # Vymažte predchádzajúci obsah okna
        for widget in self.winfo_children():
            widget.pack_forget()
        # Sets the title of our window to "App"
        self.title("YouTube skipper")
        self.setup_window_properties()
        # Dimensions of the window will be 350x225
        window_width = 350
        window_height = 225
        # Nastavime rozmery okna
        self.geometry(f"{window_width}x{window_height}")                       

        label = ctk.CTkLabel(self, text="Author: robopol.sk\nThe script automatically skips YouTube ads.\nPress 'ESC' to stop script at any time.")
        label.pack(pady=10)
        button_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        button_frame.pack()
        start_button = ctk.CTkButton(button_frame, text="Start", command=self.start_action,corner_radius=6)
        start_button.grid(row=0, column=0, pady=(10, 0), padx=10)
        stop_button = ctk.CTkButton(button_frame, text="Stop", command=self.stop_action,corner_radius=6)
        stop_button.grid(row=0, column=1, pady=(10, 0), padx=10)
        self.textbox = ctk.CTkTextbox(self, width=300, height=60, border_color="gray", border_width=1, corner_radius=3, fg_color="transparent")
        self.textbox.pack(pady=10)
        
        button_frame_1 = ctk.CTkFrame(master=self, fg_color="transparent")
        button_frame_1.pack()
        configure_button = ctk.CTkButton(button_frame_1, text="Configure", command=self.button_click_handler, corner_radius=6)
        configure_button.grid(row=0, column=0)
        self.Image_on=0        

    def setup_window_properties(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def configure_action(self):
        # Zväčšiť hlavné okno a zobraziť postup nastavenia
        self.geometry("520x660")       
        # Postup nastavenia
        configure_label = ctk.CTkLabel(self, text="Procedure:")
        configure_label.pack(anchor="w",padx=10)
        procedure_text = (
            "1) Set the coordinates x, y for the screenshot skip button.\n"
            "2) Launch a YouTube fullscreen video with an ongoing ad where \n"
            "   the skip button is visible.\n"
            "3) Press 'F8' to capture a screenshot (32x28 px) of the skip button.\n"
            "4) A large screenshot is also captured with a red box indicating the captured\n"
            "   area and opened in viewer.\n"
            "5) Adjust x, y coordinates until you achieve a good match with the correct screen.\n"
            "6) Once correct, press 'Save'.\n"
            "Press 'ESC' at any time to stop the script.\n"
        )
        configure_label_1 = ctk.CTkLabel(self, text=procedure_text, justify="left")
        configure_label_1.pack(pady=5)       
        # Frame for x, y coordinates
        xy_frame = ctk.CTkFrame(self,border_color="gray", border_width=1, corner_radius=3)
        xy_frame.pack(pady=10)
        x_label = ctk.CTkLabel(xy_frame, text="Coordinate - x:")
        x_label.grid(row=0, column=0, padx=5, pady=5)
        self.x_entry = ctk.CTkEntry(xy_frame, width=80)
        self.x_entry.grid(row=0, column=1, padx=0, pady=5)
        self.x_entry.insert(0,str(self.center_x))
        x_label = ctk.CTkLabel(xy_frame, text="px ,    ",)
        x_label.grid(row=0, column=2, padx=5, pady=0)
        y_label = ctk.CTkLabel(xy_frame, text="Coordinate - y:")
        y_label.grid(row=0, column=3, padx=5, pady=5)
        self.y_entry = ctk.CTkEntry(xy_frame, width=80)
        self.y_entry.grid(row=0, column=4, padx=0, pady=5)
        self.y_entry.insert(0,str(self.center_y))
        x_label = ctk.CTkLabel(xy_frame, text="px")
        x_label.grid(row=0, column=5, padx=5, pady=0)

        screen_frame = ctk.CTkFrame(self, fg_color="transparent",border_color="gray", border_width=1, corner_radius=3)
        screen_frame.pack()
        correct_screen_label = ctk.CTkLabel(screen_frame, text="Correct screenshot:")
        correct_screen_label.grid(row=0, column=0, padx=25, pady=5, sticky="e")
        image_path_1 = "correct_screen.png"
        try:
            self.pil_image = Image.open(image_path_1)
            self.pil_image_width, self.pil_image_height = self.pil_image.size                       
        except Exception as e:
            self.textbox.insert("0.0", f"Error loading image: {image_path_1}\n{e}\n")
            self.pil_image = None
        if self.pil_image:
            self.tk_image = ImageTk.PhotoImage(self.pil_image)                        
            canvas = ctk.CTkCanvas(screen_frame, width=self.pil_image_width, height=self.pil_image_height)
            canvas.grid(row=0, column=1, padx=25, pady=5)                        
            canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        your_screen_label=ctk.CTkLabel(screen_frame, text="Your screenshot - press 'F8':")
        your_screen_label.grid(row=1, column=0, padx=25, pady=5,sticky="e")
        image_path_2 = "your_screen.png"
        try:
            self.pil_image_1 = Image.open(image_path_2)
            self.pil_image_width_1, self.pil_image_height_1 = self.pil_image_1.size                       
        except Exception as e:
            self.textbox.insert("0.0", f"Error loading image: {image_path_2}\n{e}\n")
            self.pil_image_1 = None
        if self.pil_image_1:
            self.tk_image_1 = ImageTk.PhotoImage(self.pil_image_1)                        
            self.canvas_1 = ctk.CTkCanvas(screen_frame, width=self.pil_image_width_1, height=self.pil_image_height_1)
            self.canvas_1.grid(row=1, column=1, padx=25, pady=5)
            self.canvas_1.create_image(0, 0, anchor="nw", image=self.tk_image_1)

        end_frame = ctk.CTkFrame(self,border_color="gray", border_width=1, corner_radius=3)
        end_frame.pack(pady=10)
        threshold_label = ctk.CTkLabel(end_frame, text="White threshold:",anchor="w")
        threshold_label.grid(row=0, column=0, padx=5, pady=5)
        self.threshold_entry = ctk.CTkEntry(end_frame, width=80)
        self.threshold_entry.grid(row=0, column=1, padx=5, pady=5)
        self.threshold_entry.insert(0,str(self.threshold_value))
        shutdown_label = ctk.CTkLabel(end_frame, text="Shutdown PC:",anchor="w")
        shutdown_label.grid(row=0, column=2, padx=5, pady=5)
        self.shutdown_entry = ctk.CTkEntry(end_frame, width=80)
        self.shutdown_entry.grid(row=0, column=3, padx=5, pady=5)
        if self.shutdown_time is not None:
            self.shutdown_entry.insert(0,str(self.shutdown_time.strftime('%H:%M')))
        configure_button = ctk.CTkButton(self, text="Save", command=self.save_function, corner_radius=6)
        configure_button.pack(pady=10)

    def setup_ui(self):        
        self.area_width = int(32)
        self.area_height = int(28)
        try:
            with open("setting.txt", "r") as file:
                lines = file.readlines()
                if len(lines) < 4:
                    raise ValueError("Not enough lines in the file.")
                self.x_value = int(lines[0].strip())
                self.y_value = int(lines[1].strip())
                self.center_x=self.x_value
                self.center_y=self.y_value
                self.saved_binary_values = list(map(int, lines[2].strip().split(',')))
                self.threshold_value = int(lines[3].strip())
                if len(lines) >= 5 and lines[4].strip():
                    try:
                        shutdown_datetime = datetime.strptime(lines[4].strip(), "%H:%M")
                        self.shutdown_time = shutdown_datetime.time()                        
                    except ValueError:
                        raise ValueError("Invalid time format in the file.")
                else:
                    self.shutdown_time = None                
        except ValueError as e:
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", f"Corrupted data in the file. Error: {str(e)}\n")        
        except FileNotFoundError:
            self.shutdown_time = None
            self.threshold_value=200           
            self.center_x = int(self.screen_width) - int(51/3840*self.screen_width)
            self.center_y = int(self.screen_height) - int(171/2160*self.screen_height)                      

    def is_color_close_to_white(self,color):        
        return all(value >= self.threshold_value for value in color)

    def compare_arrays(self,array1, array2, threshold=0.91):
        matching_count = sum(1 for a, b in zip(array1, array2) if a == b)
        match_ratio = matching_count / len(array1)        
        return match_ratio >= threshold

    def start_action(self):
        if not os.path.exists("setting.txt"):
            self.button_click_handler()
            return
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0","Script has been started.\n")
        self.script_running = True
        self.stop_event.clear()
        self.running_thread = threading.Thread(target=self.start_action_thread)
        self.running_thread.start()

    def start_action_thread(self):
        while self.script_running==True:            
            time.sleep(0.6)                    
            screenshot = ImageGrab.grab(bbox=(self.center_x - self.area_width // 2, self.center_y - self.area_height // 2, self.center_x + self.area_width // 2, self.center_y + self.area_height // 2))    
            pixel_colors = list(screenshot.getdata())            
            self.binary_values = [1 if self.is_color_close_to_white(color) else 0 for color in pixel_colors]
            if self.compare_arrays(self.binary_values, self.saved_binary_values):
                pyautogui.moveTo(self.center_x, self.center_y)                
                self.mouse_controller.press(Button.left)
                time.sleep(0.3)
                self.mouse_controller.release(Button.left)
            current_time = time.localtime()    
            if self.shutdown_time and current_time.tm_hour == self.shutdown_time.hour and current_time.tm_min == self.shutdown_time.minute:        
                self.script_running = False
                pyautogui.moveTo(int(self.screen_width)-30, int(self.screen_height)-30)
                time.sleep(1.0)
                self.mouse_controller.press(Button.left)
                time.sleep(0.5)
                self.mouse_controller.release(Button.left)
                pyautogui.moveTo(int(self.screen_width)-30, 30)
                time.sleep(1.0)
                self.mouse_controller.press(Button.left)
                time.sleep(0.5)
                self.mouse_controller.release(Button.left)
                os.system('shutdown /s /t 60')        
                self.stop_action()
                time.sleep(1.0)                                                  
                break
            if not self.script_running:
                break                     

    def stop_action(self):
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0","Script has been completed.\n")
        self.script_running=False                     

if __name__ == "__main__":
    app = App()
    app.iconbitmap("icon/YouTube_skipper.ico")  # Nastavenie ikony pre okno       
    app.mainloop()
