import threading
from socket import *

from customtkinter import *
from tkinter import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('400x500')
        self.minsize(300, 400)

        self.update_idletasks()
        self.menu = CTkFrame(self, fg_color='light blue', width=0, height=self.winfo_height())
        self.menu.pack_propagate(False)
        self.menu.place(x=0, y=0)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.menu, text='Your name')
        self.label.pack(pady=30)

        self.entry = CTkEntry(self.menu)
        self.entry.pack()

        self.label_theme = CTkOptionMenu(self.menu, values=['Light', 'Dark'], command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=self.winfo_height() * 0.95)

        self.btn = CTkButton(self, text='▶️', width=30, command=self.toggle_show_menu)
        self.btn.place(x=0, y=0)

        self.update_idletasks()
        self.chat = CTkFrame(self, width=1, height=1)
        self.chat.place(relx=0.09, y=0, relwidth= 0.9, relheight=1)


        self.chat_field = CTkScrollableFrame(self.chat)
        self.chat_field.place(relx=0, rely=0, relwidth=1, relheight=0.9)

        self.bottom_frame = CTkFrame(self.chat, fg_color='transparent')
        self.bottom_frame.place(relx=0, rely=0.9, relwidth=1, relheight=0.1)

        self.entry_msg = CTkEntry(self.bottom_frame, placeholder_text="Введіть повідомлення")
        self.entry_msg.pack(side='left', fill='both', expand=True)

        self.btn_send = CTkButton(self.bottom_frame, text='Send', width=50, command=self.send_message)
        self.btn_send.pack(side='right', fill='both')

        self.username = self.entry.get()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('5.tcp.eu.ngrok.io', 10001))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")


        self.after(100, self.adaptive_ui)


    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()

    def show_menu(self):
        self.update_idletasks()
        if self.frame_width <= self.winfo_width() * 0.8:
            self.frame_width += 5
            self.menu.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀️')
        if self.is_show_menu:
            self.after(10, self.show_menu)

    def close_menu(self):
        self.update_idletasks()
        if self.frame_width >= 0:
            self.frame_width -= 5
            self.menu.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='▶️')
        if not self.is_show_menu:
            self.after(10, self.close_menu)

    def change_theme(self, value):
        if value == 'Light':
            set_appearance_mode('light')
            self.menu.configure(fg_color='light blue')
        else:
            set_appearance_mode('dark')
            self.menu.configure(fg_color='dodger blue')

    def adaptive_ui(self):
        self.update_idletasks()
        self.username = self.entry.get()

        self.menu.configure(height=self.winfo_height())

        menu_width = self.menu.winfo_width()
        window_width = self.winfo_width()

        n = window_width - menu_width


        self.chat.configure(width=n, height=self.winfo_height())
        self.chat.place(x=menu_width, y=0)
        # if menu_width > 150:
        #     self.chat.place(x=menu_width-100, y=0)
        # else:
        #self.chat.place(x=menu_width, y=0)


        self.bottom_frame.place(x=0, rely=0.85, relwidth=1, relheight=0.15)

        self.chat_field.place(x=0, y=0, relwidth=1, relheight=0.85)


        self.after(50, self.adaptive_ui)

    # def send_message(self):
    #     text = self.entry_msg.get()
    #     if text.strip():
    #         label = CTkLabel(self.chat_field, text=text, anchor='w', justify='left')
    #         label.pack(anchor='w', padx=10, pady=5)
    #         self.entry_msg.delete(0, 'end')
    #         self.chat_field.update_idletasks()
    #         self.chat_field._parent_canvas.yview_moveto(1.0)  # Прокрутка до низу

    def add_message(self, text):
        label = CTkLabel(self.chat_field, text=text, anchor='w', justify='left', wraplength=300)
        label.pack(anchor='w', padx=10, pady=5)
        self.chat_field.update_idletasks()
        self.chat_field._parent_canvas.yview_moveto(1.0)  # Автопрокрутка вниз

    def send_message(self):
        message = self.entry_msg.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.entry_msg.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]

                self.add_message(f"{author} надіслав(ла) зображення: {filename}")

        else:
            self.add_message(line)


win = MainWindow()
win.mainloop()
