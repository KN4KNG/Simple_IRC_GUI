import tkinter as tk
import threading
import socket

class IRCChatClient:
    def __init__(self, host, port, nick, channel):
        self.host = host
        self.port = port
        self.nick = nick
        self.channel = channel
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_history = []
        self.connect()
    
    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.send(f"USER {self.nick} {self.nick} {self.nick} :Python IRC Chat Client\r\n".encode())
            self.sock.send(f"NICK {self.nick}\r\n".encode())
            response = self.sock.recv(1024).decode()
            if "Nickname is already in use" in response:
                self.sock.close()
                raise Exception("Nickname is already in use. Please choose a different nickname.")
            self.sock.send(f"JOIN {self.channel}\r\n".encode())
            self.message_history.append(f"Joined channel {self.channel}")
        except Exception as e:
            self.message_history.append(str(e))
    
    def send_message(self, message):
        self.sock.send(f"PRIVMSG {self.channel} :{message}\r\n".encode())
        self.message_history.append(f"<{self.nick}> {message}")
    
    def receive_messages(self, message_box):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                if message.startswith("PING"):
                    self.sock.send("PONG\r\n".encode())
                elif "PRIVMSG" in message:
                    sender = message.split("!")[0][1:]
                    message_text = message.split("PRIVMSG")[1].split(":")[1].strip()
                    if self.nick in message_text:
                        self.notify_user(sender)
                    self.message_history.append(f"<{sender}> {message_text}")
                    message_box.insert(tk.END, f"<{sender}> {message_text}\n")
                elif "JOIN" in message:
                    user = message.split("!")[0][1:]
                    self.message_history.append(f"{user} joined the channel.")
                    self.update_user_list(message_box)
                elif "QUIT" in message:
                    user = message.split("!")[0][1:]
                    self.message_history.append(f"{user} left the channel.")
                    self.update_user_list(message_box)
                elif "KICK" in message:
                    user = message.split()[3]
                    self.message_history.append(f"{user} was kicked from the channel.")
                    self.update_user_list(message_box)
                elif "MODE" in message:
                    self.message_history.append(message)
                message_box.see(tk.END)
            except Exception as e:
                self.message_history.append(str(e))
    
    def update_user_list(self, message_box):
        users = set()
        message_box.delete(1.0, tk.END)
        for message in self.message_history:
            if "JOIN" in message:
                user = message.split("!")[0][1:]
                users.add(user)
            elif "QUIT" in message or "KICK" in message:
                user = message.split()[0]
                users.discard(user)
        user_list = "\n".join(sorted(users))
        message_box.insert(tk.END, "Users in channel:\n" + user_list + "\n")
    
    def notify_user(self, sender):
        pass # add code to display a notification when a message contains the user's nickname
    
class IRCChatGUI:
    def __init__(self, host, port, nick, channel):
        self.chat_client = IRCChatClient(host, port, nick, channel)
        self.root = tk.Tk()
        self.root.title("IRC Chat Client")
        self.create_gui()
    
    def create_gui(self):
        # Message box
        self.message_box = tk.Text(self.root, height=20, width=80)
        self.message_box.pack(side=tk.TOP, padx=5, pady=5)
        
        # Entry box
        self.message_entry = tk.Entry(self.root, width=80)
        self.message_entry.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        # Send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        # Bind Return key to send message
        self.root.bind("<Return>", self.send_message)
        
        # User list
        self.user_list = tk.Text(self.root, height=20, width=20)
        self.user_list.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Message history button
        self.history_button = tk.Button(self.root, text="History", command=self.show_history)
        self.history_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        # Emojis and formatting
        self.emoji_button = tk.Button(self.root, text="😀", command=lambda: self.insert_text("😀"))
        self.emoji_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        self.bold_button = tk.Button(self.root, text="B", command=lambda: self.insert_text("<b></b>"))
        self.bold_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        self.italic_button = tk.Button(self.root, text="I", command=lambda: self.insert_text("<i></i>"))
        self.italic_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        # Start chat client thread
        threading.Thread(target=self.chat_client.receive_messages, args=(self.message_box,), daemon=True).start()
        
        # Update user list
        self.chat_client.update_user_list(self.user_list)
    
    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            self.chat_client.send_message(message)
            self.message_entry.delete(0, tk.END)
    
    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Message History")
        message_box = tk.Text(history_window, height=20, width=80)
        message_box.pack(side=tk.TOP, padx=5, pady=5)
        for message in self.chat_client.message_history:
            message_box.insert(tk.END, message + "\n")
        message_box.see(tk.END)
    
    def insert_text(self, text):
        self.message_entry.insert(tk.END, text)
        self.message_entry.focus_set()
        self.message_entry.icursor(tk.END)
    
    def start(self):
        self.root.mainloop()

gui = IRCChatGUI("irc.example.com", 6667, "my_nickname", "#my_channel")
gui.start()
