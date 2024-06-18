import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import vlc
import socket
import threading
import settings as st
import time
import json
import sys
import os
import keyboard
from pynput import mouse


def thread_create(function):
    threading.Thread(target=function).start()
    threading.Thread(target=function).join()


def on_move(x, y):
    show_controls()


def on_click(x, y, button, pressed):
    show_controls()


def on_scroll(x, y, dx, dy):
    show_controls()


def start_mouse_listen():
    with mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll) as listener:
        listener.join()


os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')

# Setting the appearance and theme
ctk.set_appearance_mode(st.default_appearance_mode)
ctk.set_default_color_theme(st.default_color_theme)

Instance = vlc.Instance("--no-video-title-show")
player = Instance.media_player_new()

file_path = "/"
hide_control_ui = False
hide_control_timer = None
vlc_window_open = False  # Variable to track if VLC window is open

client_socket = None
server_address = '0.0.0.0'  # Default to bind to all interfaces
server_port = 12345  # Default server port

server_running = True  # Flag to control server thread


def get_player_info():
    global player
    is_playing = False
    current_time = 0

    if player.is_playing():
        print(f"Playback status: Playing")
        is_playing = True
    else:
        print(f"Playback status: Paused")
        is_playing = False

    current_time = player.get_time()
    print(f"Current time (ms): {current_time}")
    return is_playing, current_time


def send_player_info():
    global client_socket
    global player

    try:
        is_playing, current_time = get_player_info()
        player_info = {
            "is_playing": is_playing,
            "current_time": current_time
        }
        json_data = json.dumps(player_info).encode('utf-8')
        if client_socket:
            client_socket.sendall(json_data)
        time.sleep(3)  # Send info every 3 seconds
    except Exception as e:
        print(f"Error sending player info: {e}")


def start_server():
    global client_socket
    global server_address
    global server_port

    if server_address is None or server_port is None:
        print("Server address or port is not properly initialized.")
        return

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_address, server_port))
        server_socket.listen(5)

        print(f"Server listening on {server_address}:{server_port}")

        client_socket, addr = server_socket.accept()
        print(f"Client connected from {addr}")

        while True:
            send_player_info()

    except Exception as e:
        print(f"Error starting server: {e}")
    finally:
        server_socket.close()


def start_movie(display, file_path):
    global player
    Media = Instance.media_new(file_path)

    # Set media to player
    player.set_media(Media)

    # Set the window handle to embed VLC
    player.set_hwnd(display.winfo_id())

    # Play the media
    player.play()


def select_movie():
    global file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        # Update label with selected file path
        selected_file_label.configure(text=file_path)
        vlc_player()


def toggle_fullscreen(vlc_window):
    if vlc_window.attributes('-fullscreen'):
        vlc_window.attributes('-fullscreen', False)
    else:
        vlc_window.attributes('-fullscreen', True)


def skip_forward():
    # Skip forward 5 seconds
    thread_create(lambda: player.set_time(player.get_time() + 5000))

    send_thread = threading.Thread(target=send_player_info)
    send_thread.start()
    send_thread.join()


def skip_backward():
    # Rewind 5 seconds
    thread_create(lambda: player.set_time(player.get_time() - 5000))

    send_thread = threading.Thread(target=send_player_info)
    send_thread.start()
    send_thread.join()


def toggle_pause(event=None):
    # Pause or unpause the video
    thread_create(player.pause)
    send_thread = threading.Thread(target=send_player_info)
    send_thread.start()
    send_thread.join()


def close_window(event=None):
    global vlc_window_open
    global mouse_listener
    player.stop()
    vlc_window.destroy()
    vlc_window_open = False  # Update the status when VLC window is closed
    if mouse_listener:
        mouse_listener.stop()  # Stop the mouse listener


def show_controls(event=None):
    global hide_control_ui
    global hide_control_timer
    hide_control_ui = False
    control_frame.place(relx=0.5, rely=1.0, anchor=tk.S)
    reset_hide_controls()


def reset_hide_controls():
    global hide_control_timer
    if hide_control_timer is not None:
        vlc_window.after_cancel(hide_control_timer)
    hide_control_timer = vlc_window.after(3000, hide_controls)


def hide_controls():
    global hide_control_ui
    control_frame.place_forget()
    hide_control_ui = True


def vlc_player():
    global file_path
    global vlc_window
    global control_frame
    global vlc_window_open
    global mouse_listener

    if vlc_window_open:
        print("VLC player is already running.")
        return

    vlc_window_open = True

    vlc_window = ctk.CTk()
    vlc_window.geometry("1920x1080")

    # Make the window fullscreen
    vlc_window.attributes('-fullscreen', True)

    # Frame for video display
    frame = tk.Frame(vlc_window, background="black")
    frame.pack(fill=tk.BOTH, expand=True)

    display = tk.Frame(frame, bd=5)
    display.pack(fill=tk.BOTH, expand=True)

    # Start the movie in the display frame
    start_movie(display, file_path)

    # Bind keys for controlling the player
    vlc_window.bind("<f>", lambda event: toggle_fullscreen(vlc_window))
    vlc_window.bind("<space>", toggle_pause)
    vlc_window.bind("<Left>", lambda event: skip_backward())
    vlc_window.bind("<Right>", lambda event: skip_forward())
    vlc_window.bind("<Escape>", close_window)
    keyboard.on_press(show_controls)

    # Create control buttons
    control_frame = tk.Frame(vlc_window, bg='gray')

    button_skip_backward = tk.Button(control_frame, text="<< 5s", command=skip_backward)
    button_skip_backward.pack(side=tk.LEFT, padx=10)

    button_skip_forward = tk.Button(control_frame, text="5s >>", command=skip_forward)
    button_skip_forward.pack(side=tk.LEFT, padx=10)

    button_toggle_fullscreen = tk.Button(control_frame, text="Toggle Fullscreen (F)",
                                         command=lambda: toggle_fullscreen(vlc_window))
    button_toggle_fullscreen.pack(side=tk.LEFT, padx=10)

    button_pause = tk.Button(control_frame, text="Pause/Play (Space)", command=toggle_pause)
    button_pause.pack(side=tk.LEFT, padx=10)

    button_close = tk.Button(control_frame, text="Close (Esc)", command=close_window)
    button_close.pack(side=tk.LEFT, padx=10)

    control_frame.place(relx=0.5, rely=1.0, anchor=tk.S)
    reset_hide_controls()

    # Start mouse listener
    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )
    mouse_listener.start()

    vlc_window.mainloop()


def get_local_ip():
    try:
        # Connect to an external server to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 1))  # Connect to Google's public DNS server
        local_ip = s.getsockname()[0]
    except Exception as e:
        print(f"Could not get local IP: {e}")
        local_ip = '127.0.0.1'  # Default to localhost if unable to get IP
    finally:
        s.close()
    return local_ip


def on_closing():
    print("Closing application...")
    if client_socket:
        client_socket.close()
    sys.exit(0)


def open_movieM_Host():
    global server_address
    global server_port

    start_server_thread = threading.Thread(target=start_server)
    start_server_thread.start()

    host = ctk.CTk()

    host.geometry("980x610")
    host.minsize(980, 610)

    # Handle closing the application
    host.protocol("WM_DELETE_WINDOW", on_closing)

    # Host frame
    frame = ctk.CTkFrame(host)
    frame.pack(pady=40, padx=60, fill="both", expand=True)

    # Server frame
    server_frame = ctk.CTkFrame(frame)
    server_frame.pack(pady=10, padx=10, fill="both", expand=True)

    host.title("Movie Mate")

    heading_label = ctk.CTkLabel(server_frame, text="Movie Mate Host", font=ctk.CTkFont(size=24, weight="bold"))
    heading_label.pack(pady=(10, 5), padx=10)

    # Get the local IP address and update the server frame
    local_ip = get_local_ip()

    ip_label = ctk.CTkLabel(server_frame, text=f"Server IP: {local_ip}", font=ctk.CTkFont(size=18))
    ip_label.pack(pady=(10, 5), padx=10)

    port_label = ctk.CTkLabel(server_frame, text=f"Server Port: {server_port}", font=ctk.CTkFont(size=18))
    port_label.pack(pady=(5, 10), padx=10)

    select_file_button = ctk.CTkButton(host, text="Select Movie", command=select_movie)
    select_file_button.pack(pady=(10, 20))

    global selected_file_label
    selected_file_label = ctk.CTkLabel(host, text="", font=ctk.CTkFont(size=16))
    selected_file_label.pack(pady=(10, 20))

    host.mainloop()


if __name__ == "__main__":
    open_movieM_Host()
