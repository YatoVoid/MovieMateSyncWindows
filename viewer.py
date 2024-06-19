import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import vlc
import socket
import threading
import settings as st
import json

# Setting the appearance and theme
ctk.set_appearance_mode(st.default_appearance_mode)
ctk.set_default_color_theme(st.default_color_theme)

# Global variables
client_socket = None
server_address = None
server_port = None
current_playing = True
Instance = vlc.Instance()
player = Instance.media_player_new()
file_path = "/"



def connect_to_server(server_ip_entry, server_port_entry):
    global client_socket, server_address, server_port

    # Get server IP and port from input fields
    server_address = server_ip_entry.get()
    server_port = server_port_entry.get()

    # Validate IP address and port
    if not server_address or not server_port:
        print("Please enter both IP address and port.")
        return

    try:
        server_port = int(server_port)  # Convert port to integer

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        print(f"Connected to server {server_address}:{server_port}")


        play_media = threading.Thread(target=select_and_play_media)
        play_media.start()

        # Start a thread to receive data from server
        receive_thread = threading.Thread(target=receive_data_from_server)
        receive_thread.start()

    except ValueError:
        print("Invalid port number. Port must be an integer.")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        client_socket = None


def disconnect_from_server():
    global client_socket
    if client_socket:
        client_socket.close()
        client_socket = None
        print("Disconnected from server")


def receive_data_from_server():
    global client_socket
    global current_playing
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            print(f"Received data from server: {data}")

            # Process received data if needed (for example, seek to a specific time)
            try:
                data_dict = json.loads(data)
                if 'current_time' in data_dict:
                    seek_to_time = int(data_dict['current_time'])
                    player.set_time(seek_to_time)
                    print("TIME:",seek_to_time)

                if 'is_playing' in data_dict:
                    print("PLY:",data_dict['is_playing'])

                    if data_dict['is_playing']==False and current_playing!=False:
                        player.pause()
                        current_playing = False

                    if data_dict['is_playing']==True and current_playing!=True:
                        player.play()
                        current_playing = True

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON data: {e}")

        except Exception as e:
            print(f"Error receiving data: {e}")
            break


def start_movie():
    global file_path

    Media = Instance.media_new(file_path)
    player.set_media(Media)
    player.play()


def select_and_play_media():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        start_movie()


def open_movieM_Viewer():
    global server_address, server_port

    viewer = ctk.CTk()
    viewer.title("MovieMateSyncView")

    viewer.geometry("800x400")
    viewer.minsize(800, 400)

    frame = ctk.CTkFrame(viewer, width=900, height=300)
    frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    server_ip_label = ctk.CTkLabel(frame, text="Server IP:")
    server_ip_label.pack(pady=10)

    server_ip_entry = ctk.CTkEntry(frame, width=100)
    server_ip_entry.pack(pady=5)

    server_port_label = ctk.CTkLabel(frame, text="Server Port:")
    server_port_label.pack(pady=10)

    server_port_entry = ctk.CTkEntry(frame, width=100)
    server_port_entry.pack(pady=5)

    button_connect = ctk.CTkButton(master=frame, text="Connect", corner_radius=30,
                                   command=lambda: connect_to_server(server_ip_entry, server_port_entry),
                                   height=50, width=200, font=(st.default_font_family, st.font_sizes["large"]))
    button_connect.pack(pady=20)

    button_disconnect = ctk.CTkButton(master=frame, text="Disconnect", corner_radius=30,
                                      command=disconnect_from_server,
                                      height=50, width=150, font=(st.default_font_family, st.font_sizes["large"]))
    button_disconnect.pack(pady=20)

    viewer.mainloop()





