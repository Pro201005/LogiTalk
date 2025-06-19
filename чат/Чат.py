import customtkinter as ctk
import socket
import threading
import time

class LogiTalkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Чат")
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Чат", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Налаштування", command=self.open_settings_window)
        self.settings_button.grid(row=1, column=0, padx=20, pady=10)

        self.main_content_frame = ctk.CTkFrame(self)
        self.message_display_box = ctk.CTkTextbox(self.main_content_frame, width=200, height=200, state="disabled")
        self.message_display_box.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.message_input_entry = ctk.CTkEntry(self.main_content_frame, placeholder_text="Напиши повідомлення")
        self.message_input_entry.grid(row=1, column=0, padx=(20, 20), pady=(10, 0), sticky="ew")
        self.message_input_entry.bind("<Return>", self.send_message_event)

        self.send_button = ctk.CTkButton(self.main_content_frame, text="Відправити", command=self.send_message)
        self.send_button.grid(row=2, column=0, padx=(20, 20), pady=(10, 20), sticky="e")

        
        self.registration_frame = ctk.CTkFrame(self)
        self.registration_frame.grid(row=0, column=0, columnspan=2, rowspan=3, sticky="nsew", padx=20, pady=20)
        self.registration_frame.grid_rowconfigure(0, weight=1)
        self.registration_frame.grid_rowconfigure(4, weight=1)
        self.registration_frame.grid_columnconfigure(0, weight=1)

        self.welcome_label = ctk.CTkLabel(self.registration_frame, text="Ласкаво просимо в Чат", font=ctk.CTkFont(size=24, weight="bold"))
        self.welcome_label.grid(row=1, column=0, pady=(50, 20))

        self.username_label = ctk.CTkLabel(self.registration_frame, text="Будь ласка, введіть ваше ім'я користувача:", font=ctk.CTkFont(size=16))
        self.username_label.grid(row=2, column=0, pady=10)

        self.username_entry = ctk.CTkEntry(self.registration_frame, placeholder_text="Ім'я користувача", width=250)
        self.username_entry.grid(row=3, column=0, pady=5)
        self.username_entry.bind("<Return>", self.register_user_event)

        self.register_button = ctk.CTkButton(self.registration_frame, text="Увійти до чату", command=self.register_user_threaded)
        self.register_button.grid(row=4, column=0, pady=(20, 50))

        
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(0, weight=1)

        self.settings_label = ctk.CTkLabel(self.settings_frame, text="Налаштування додатку", font=ctk.CTkFont(size=20, weight="bold"))
        self.settings_label.grid(row=0, column=0, pady=20, padx=20, sticky="n")

        self.theme_label = ctk.CTkLabel(self.settings_frame, text="Тема:")
        self.theme_label.grid(row=1, column=0, pady=5, padx=20, sticky="w")
        self.theme_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=["System", "Light", "Dark"],
                                                    command=self.change_theme)
        self.theme_optionmenu.grid(row=2, column=0, pady=5, padx=20, sticky="ew")

        self.scale_label = ctk.CTkLabel(self.settings_frame, text="Масштаб інтерфейсу:")
        self.scale_label.grid(row=3, column=0, pady=5, padx=20, sticky="w")
        self.scale_optionmenu = ctk.CTkOptionMenu(self.settings_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                    command=self.change_scaling)
        self.scale_optionmenu.grid(row=4, column=0, pady=5, padx=20, sticky="ew")
        self.theme_optionmenu.set(ctk.get_appearance_mode().capitalize())

        
        self.client_socket = None
        self.username = None
        self.is_connected = False

    def send_message_event(self, event):
        self.send_message()

    def register_user_event(self, event):
        self.register_user_threaded()

    def register_user_threaded(self):
        
        username = self.username_entry.get().strip()
        if username:
            self.username = username
            self.display_message("Спроба підключення до сервера...")
            self.register_button.configure(state="disabled", text="Підключення...") 
            threading.Thread(target=self._attempt_registration, daemon=True).start()
        else:
            self.display_message("Ім'я користувача не може бути порожнім.")

    def _attempt_registration(self):
        
        if self.connect_to_server():
            self.after(0, self._show_chat_interface_on_success)
        else:
            self.after(0, self._reset_registration_button_on_failure)

    def _show_chat_interface_on_success(self):
        print(f"Користувач '{self.username}' зареєструвався успішно.")
        self.registration_frame.grid_forget()
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.main_content_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.register_button.configure(state="normal", text="Увійти до чату") 
        self.display_message(f"Ласкаво просимо, {self.username}! Розпочніть спілкування.")


    def _reset_registration_button_on_failure(self):
        
        self.register_button.configure(state="normal", text="Увійти до чату")
        

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_ip = '0.tcp.eu.ngrok.io'
            server_port = 13578
            
            print(f"Спроба підключення до {server_ip}:{server_port}...")
            self.client_socket.connect((server_ip, server_port))
            self.is_connected = True
            print(f"Підключено до сервера за адресою {server_ip}:{server_port}")
            self.client_socket.sendall(f"{self.username}\n".encode('utf-8'))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            return True
        except ConnectionRefusedError:
            self.display_message("Помилка: Не вдалося підключитися до сервера. Переконайтеся, що сервер запущено.")
            print("Помилка: Сервер відмовив у підключенні.")
            return False
        except Exception as e:
            self.display_message(f"Помилка підключення: {e}")
            print(f"Загальна помилка підключення: {e}")
            return False

    def receive_messages(self):
        buffer = ""
        while self.is_connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                print(f"Отримано сирі дані: '{data}'") 
                if not data:
                    self.display_message("Сервер відключився.")
                    print("Сервер відключився.")
                    self.is_connected = False
                    self.client_socket.close()
                    break

                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    self.display_message(message)
                    print(f"Відображено повідомлення: '{message}'") 

            except OSError:
                print("Сокет закрито, зупинка прийому повідомлень.")
                self.is_connected = False
                break
            except Exception as e:
                self.display_message(f"Помилка при отриманні повідомлення: {e}")
                print(f"Загальна помилка прийому повідомлення: {e}")
                self.is_connected = False
                if self.client_socket:
                    self.client_socket.close()
                break

    def display_message(self, message):
        self.after(0, lambda: self._update_message_display(message))

    def _update_message_display(self, message):
        self.message_display_box.configure(state="normal")
        self.message_display_box.insert("end", f"{message}\n")
        self.message_display_box.see("end")
        self.message_display_box.configure(state="disabled")

    def send_message(self):
        if not self.is_connected:
            self.display_message("Ви не підключені до чату. Будь ласка, увійдіть спочатку.")
            print("Спроба відправити повідомлення, але не підключено.")
            return

        message = self.message_input_entry.get().strip()
        if message:
            try:
               
               
                self.display_message(f"Я: {message}")
                print(f"Повідомлення відправлено та локально відображено: '{message}'")
                self.message_input_entry.delete(0, "end")
            except Exception as e:
                self.display_message(f"Помилка відправки повідомлення: {e}")
                print(f"Помилка відправки повідомлення: {e}")
                self.is_connected = False
                if self.client_socket:
                    self.client_socket.close()

    def open_settings_window(self):
        if self.settings_frame.winfo_ismapped():
            return

        self.main_content_frame.grid_forget()
        self.settings_frame.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=20, pady=20)

        if not hasattr(self, 'back_to_chat_button'):
            self.back_to_chat_button = ctk.CTkButton(self.settings_frame, text="Повернутися до чату", command=self.show_chat_content)
            self.back_to_chat_button.grid(row=5, column=0, pady=20)

    def show_chat_content(self):
        self.settings_frame.grid_forget()
        self.main_content_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def change_theme(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def on_closing(self):
        if self.is_connected and self.client_socket:
            try:
                self.client_socket.sendall(f"leave_chat_signal\n".encode('utf-8'))
                time.sleep(0.1) 
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except OSError as e:
                print(f"Помилка закриття сокета під час виходу: {e}")
        self.destroy()

if __name__ == "__main__":
    app = LogiTalkApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
