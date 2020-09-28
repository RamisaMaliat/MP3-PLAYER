from tkinter import *
import pygame
import sqlite3
import time
from tkinter import filedialog, messagebox, ttk
from mutagen.mp3 import MP3
import re

pygame.mixer.init()
global paused
paused = False
global top, playlist_label, playlist_listbox, create_playlist, create_playlist_listbox, names_entry, playlist_frame, scroll, selected_song_listbox_playlist
global forward_image1, backward_image1, pause_image1, stop_image1, play_image1, volume_frame1, volume_slider1, song_slider1, song_slider_frame1, after_id1, after_id2
playlists = "playlists.sqlite"
chack_play = False
window_stack = []
global after_id
after_id = ""
after_id1 = ""
after_id2 = ""

main_window = Tk()
main_window.title("MP3 PLAYER")
main_window.config(bg="black")
main_window.iconbitmap(r"mp3.ico")
main_window.geometry("1100x645+100+100")

def on_closing():
    pygame.mixer.music.stop()
    w = window_stack[len(window_stack)-1]
    window_stack.pop()
    w.destroy()
    window_stack[len(window_stack) - 1].deiconify()

def volume(var):
    pygame.mixer.music.set_volume(volume_slider.get())

def nothing():
    pass

def add_a_song():
    selected_song = filedialog.askopenfilename(title="Select a song", filetypes=(("mp3 files", "*.mp3"),))
    if selected_song:
        selected_song_listbox.insert(END, selected_song)


def add_multiple_songs():
    selected_songs = filedialog.askopenfilenames(title="Select songs", filetypes=(("mp3 files", "*.mp3"),))
    if selected_songs:
        for song in selected_songs:
            selected_song_listbox.insert(END, song)


def remove_the_selected_song():
    stop()
    selected_song_listbox.delete(ANCHOR)


def remove_all_songs():
    stop()
    selected_song_listbox.delete(0, END)

def update_song_slider(var):
    play(song_slider.get())


def stop():
    global after_id
    if after_id != "":
        song_slider_frame.after_cancel(after_id)
    pygame.mixer.music.stop()
    selected_song_listbox.selection_clear(ACTIVE)
    song_slider_frame.config(text=f"00:00:00  of  00:00:00")
    song_slider.config(value=0)
    after_id = ""

def play_time(song, current_pos):
    global after_id
    converted_current_pos = time.strftime('%H:%M:%S', time.gmtime(current_pos))
    song_mut = MP3(song)
    song_length = song_mut.info.length
    converted_song_length = time.strftime('%H:%M:%S', time.gmtime(song_length))
    if current_pos <= song_length:
        song_slider_frame.config(text=f"Playing : {song} - {converted_current_pos}  of  {converted_song_length}")
        song_slider.config(value=current_pos)
        after_id = song_slider_frame.after(1000, lambda: play_time(song, song_slider.get()+1))
    else:
        song_slider_frame.config(text=f"Playing : {song} - {converted_song_length}  of  {converted_song_length}")
        song_slider.config(value=song_length)

def play(val):
    global after_id
    if after_id != "":
        song_slider_frame.after_cancel(after_id)
    song_tuple = selected_song_listbox.curselection()
    if song_tuple:
        song = selected_song_listbox.get(ACTIVE)
        if song:
            try:
                pygame.mixer.music.load(song)
                pygame.mixer.music.play(loops=0, start=val)
                song_mut = MP3(song)
                song_length = song_mut.info.length
                song_slider.config(to=song_length, value=val)
                global paused
                paused = False
                play_time(song, val)
            except:
                stop()
                messagebox.showerror("Song not found!", "Song could not be found.")


def pause():
    global paused, after_id
    try:
        if paused:
            pygame.mixer.music.unpause()
            paused = False
            play(song_slider.get())
        else:
            pygame.mixer.music.pause()
            song_slider_frame.after_cancel(after_id)
            paused = True
    except:
        pass

def forward():
    song_tuple = selected_song_listbox.curselection()
    if song_tuple:
        next_song = song_tuple[0] + 1
        if next_song == selected_song_listbox.size():
            next_song = 0
        selected_song_listbox.selection_clear(ACTIVE)
        selected_song_listbox.activate(next_song)
        selected_song_listbox.selection_set(next_song)
        play(0)


def backward():
    song_tuple = selected_song_listbox.curselection()
    if song_tuple:
        prev_song = song_tuple[0] - 1
        if prev_song == -1:
            prev_song = selected_song_listbox.size() - 1
        selected_song_listbox.selection_clear(ACTIVE)
        selected_song_listbox.activate(prev_song)
        selected_song_listbox.selection_set(prev_song)
        play(0)

def volume1(var):
    pygame.mixer.music.set_volume(volume_slider1.get())


def add_to_new_playlist():
    selected_songs = filedialog.askopenfilenames(title="Select songs", filetypes=(("mp3 files", "*.mp3"),))
    if selected_songs:
        for song in selected_songs:
            create_playlist_listbox.insert(END, song)


def remove_from_new_playlist():
    songs = create_playlist_listbox.curselection()
    if songs:
        remaining = []
        pos = 0
        target_index = songs[pos]
        for index in range(create_playlist_listbox.size()):
            if index != target_index:
                remaining.append(create_playlist_listbox.get(index))
            else:
                pos = pos + 1
                if pos < len(songs):
                    target_index = songs[pos]
        create_playlist_listbox.delete(0, END)
        for song in remaining:
            create_playlist_listbox.insert(END, song)


def get_title(song):
    songlist = re.findall("3pm\..*?/", song[::-1])
    title = songlist[0][::-1][1:]
    return title

def get_song_location(song):
    location = re.findall("File Location -> (.*)", song)[0]
    return location

def create_new_playlist():
    global create_playlist_listbox, names_entry

    playlist_name = names_entry.get().strip().lower()

    if len(playlist_name) == 0:
        messagebox.showerror("Invalid Name!", "Playlist name should at least have one character.")
        return

    if playlist_name[0] >= '0' and playlist_name[0] <= '9':
        messagebox.showerror("Invalid Name!", "Playlist name should not start with numbers(0-9).")
        return

    if create_playlist_listbox.size() == 0:
        messagebox.showerror("Add songs!", "Add songs to create a playlist.")
        return

    playlist_name = playlist_name.replace(" ", "_")

    conn = sqlite3.connect(playlists)
    cur = conn.cursor()

    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (playlist_name, ))
    # if the count is 1, then table exists
    if cur.fetchone()[0] == 1:
        messagebox.showerror("Invalid Name!", "Playlist with this name already exists.Try another name.")
    else:
        sql = f"CREATE TABLE {playlist_name} (title TEXT, song TEXT, CONSTRAINT pk PRIMARY KEY(title,song) )"
        cur.execute(sql)
        for index in range(create_playlist_listbox.size()):
            song = create_playlist_listbox.get(index)
            title = get_title(song)
            sql = f'''INSERT OR REPLACE INTO {playlist_name} VALUES("{title}","{song}")'''
            cur.execute(sql)
        messagebox.showinfo("New playlist created!", f"You created a new playlist : {playlist_name}.")

    conn.commit()
    conn.close()
    w = window_stack[len(window_stack) - 1]
    window_stack.pop()
    w.destroy()
    w = window_stack[len(window_stack) - 1]
    window_stack.pop()
    w.destroy()
    open_my_playlists()

def create_new_playlist_window():
    stop()
    window_stack[len(window_stack) - 1].wm_withdraw()
    global create_playlist_listbox, names_entry
    temp_top = Toplevel(bg="#C0C0C0")
    temp_top.title("MP3 PLAYER-Create a new playlist")
    temp_top.geometry("1000x520")
    temp_top.iconbitmap(r"mp3.ico")
    create_playlist_label = Label(temp_top, text="--- CREATE A NEW PLAYLIST ---", width=50, height=1, bg="black",
                                  fg="white",
                                  font=("helvetica", 10))
    create_playlist_label.pack(pady=25)
    create_playlist_frame = Frame(temp_top)
    create_playlist_frame.pack()
    create_playlist_listbox = Listbox(create_playlist_frame, bg="black", fg="white", width=157, height=19, selectmode=EXTENDED)
    create_playlist_listbox.grid(row=0, column=0)
    scroll1 = Scrollbar(create_playlist_frame, orient='vertical', command=create_playlist_listbox.yview)
    create_playlist_listbox.config(yscrollcommand=scroll1.set)
    scroll1.grid(row=0, column=1, sticky=N + S + E)
    scroll2 = Scrollbar(create_playlist_frame, orient='horizontal', command=create_playlist_listbox.xview)
    create_playlist_listbox.config(xscrollcommand=scroll2.set)
    scroll2.grid(row=1, column=0, columnspan=2, sticky=W + E + S)
    name_frame = Frame(temp_top, pady=2)
    name_frame.pack()
    name_label = Label(name_frame, text="Name Your Playlist : ", font=("helvetica", 12), width=16)
    name_label.grid(row=0, column=0)
    names_entry = Entry(name_frame, font=("helvetica", 12), width=73)
    names_entry.grid(row=0, column=1)
    add_songs_button = Button(name_frame, text="Add Songs To Playlist", font=("helvetica", 10), width=18, fg="white",
                              bg="#03509E",
                              activebackground="#377BFF", bd=1, command=add_to_new_playlist)
    add_songs_button.grid(row=0, column=2, pady=2)
    remove_song_button = Button(name_frame, text="Remove Selected Song(s) From Playlist", font=("helvetica", 10),
                                width=30, fg="white", bg="gray",
                                activebackground="silver", activeforeground="black", bd=1,
                                command=remove_from_new_playlist)
    remove_song_button.grid(row=1, columnspan=2, sticky=E, column=1)
    create_playlist = Button(temp_top, text="CREATE", font=("helvetica", 10), fg="white", bg="#03509E",
                             activebackground="#377BFF",
                             bd=2, height=2, width=20, command=create_new_playlist)
    create_playlist.pack(pady=20)
    window_stack.append(temp_top)
    window_stack[len(window_stack) - 1].protocol("WM_DELETE_WINDOW", on_closing)

def show_playlists():
    conn = sqlite3.connect(playlists)
    cur = conn.cursor()
    results = cur.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ')
    for row in results:
        title = row[0]
        sql = f"SELECT COUNT(*) FROM {row[0]}"
        tmp = conn.cursor()
        tmp.execute(sql)
        number = tmp.fetchone()[0]
        vstr = "Title : "+title
        playlist_listbox.insert(END, vstr)
        vstr = "Number of Songs : "+str(number)
        playlist_listbox.insert(END, vstr)
        playlist_listbox.insert(END, "_"*134)

def play_time1(song, current_pos, index):
    global after_id1, after_id2
    converted_current_pos = time.strftime('%H:%M:%S', time.gmtime(current_pos))
    song_mut = MP3(song)
    song_length = song_mut.info.length
    converted_song_length = time.strftime('%H:%M:%S', time.gmtime(song_length))
    if current_pos <= song_length:
        song_slider_frame1.config(text=f"Playing : {song} - {converted_current_pos}  of  {converted_song_length}")
        song_slider1.config(value=current_pos)
        after_id1 = song_slider_frame1.after(1000, lambda: play_time1(song, song_slider1.get()+1, index))
    else:
        if (index+1)!=selected_song_listbox_playlist.size():
            index += 1
        else:
            index = 0
        song_slider_frame1.config(text=f"Playing : {song} - {converted_song_length}  of  {converted_song_length}")
        song_slider1.config(value=song_length)
        after_id2 = selected_song_listbox_playlist.after(3000, lambda: update_next(index))

def update_song_slider1(var):
    play_current(song_slider1.get())

def playlist_options():
    conn = sqlite3.connect(playlists)
    cur = conn.cursor()
    results = cur.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ')
    options = []
    for row in results:
        title = row[0]
        options.append(title)
    return options

def update_next(index):
    global after_id1, after_id2
    selected_song_listbox_playlist.selection_clear(ACTIVE)
    if after_id1 != "":
        song_slider_frame1.after_cancel(after_id1)
    play_all(index, 0)

def play_all(index, val):
        global after_id2
        song_length = 0
        selected_song_listbox_playlist.activate(index)
        selected_song_listbox_playlist.selection_set(index)
        song = get_song_location(selected_song_listbox_playlist.get(ACTIVE))
        try:
            pygame.mixer.music.load(song)
            pygame.mixer.music.play(loops=0, start=val)
            song_mut = MP3(song)
            song_length = song_mut.info.length
            song_slider1.config(to=song_length, value=val)
            global paused
            paused = False
            play_time1(song, val, index)
        except:
            messagebox.showerror("Song not found!", "Invalid song.")
            forward_current()

def play_current(val):
    global after_id1, after_id2
    if after_id1 != "":
        song_slider_frame1.after_cancel(after_id1)
    if after_id2 != "":
        selected_song_listbox_playlist.after_cancel(after_id2)
    line = selected_song_listbox_playlist.curselection()
    if line:
        index = line[0]
        play_all(index, val)

def stop_current():
    global after_id1, after_id2
    if after_id1 != "":
        song_slider_frame1.after_cancel(after_id1)
    if after_id2 != "":
        selected_song_listbox_playlist.after_cancel(after_id2)
    pygame.mixer.music.stop()
    selected_song_listbox_playlist.selection_clear(ACTIVE)
    song_slider_frame1.config(text=f"00:00:00  of  00:00:00")
    song_slider1.config(value=0)
    after_id1 = ""
    after_id2 = ""

def forward_current():
    if after_id1 != "":
        song_slider_frame1.after_cancel(after_id1)
    if after_id2 != "":
        selected_song_listbox_playlist.after_cancel(after_id2)
    song_tuple = selected_song_listbox_playlist.curselection()
    if song_tuple:
        next_song = song_tuple[0] + 1
        if next_song == selected_song_listbox_playlist.size():
            next_song = 0
        selected_song_listbox_playlist.selection_clear(ACTIVE)
        selected_song_listbox_playlist.activate(next_song)
        selected_song_listbox_playlist.selection_set(next_song)
        try:
            song = get_song_location(selected_song_listbox_playlist.get(ACTIVE))
            pygame.mixer.music.load(song)
            play_all(next_song, 0)
        except:
            messagebox.showerror("Song not found!", "Invalid song.")
            forward_current()

def backward_current():
    if after_id1 != "":
        song_slider_frame1.after_cancel(after_id1)
    if after_id2 != "":
        selected_song_listbox_playlist.after_cancel(after_id2)
    song_tuple = selected_song_listbox_playlist.curselection()
    if song_tuple:
        prev_song = song_tuple[0] - 1
        if prev_song == -1:
            prev_song = selected_song_listbox_playlist.size() - 1
        selected_song_listbox_playlist.selection_clear(ACTIVE)
        selected_song_listbox_playlist.activate(prev_song)
        selected_song_listbox_playlist.selection_set(prev_song)
        try:
            song = get_song_location(selected_song_listbox_playlist.get(ACTIVE))
            pygame.mixer.music.load(song)
            play_all(prev_song, 0)
        except:
            messagebox.showerror("Song not found!", "Invalid song.")
            backward_current()

def pause_current():
    global paused, after_id1, after_id2, song_slider1, song_slider_frame1
    try:
        if paused:
            pygame.mixer.music.unpause()
            paused = False
            play_current(song_slider1.get())
        else:
            pygame.mixer.music.pause()
            if after_id1 != "":
                song_slider_frame1.after_cancel(after_id1)
            if after_id2 != "":
                selected_song_listbox_playlist.after_cancel(after_id2)
            paused = True
    except:
        pass

def play_playlist():
    global volume_frame1, volume_slider1, song_slider_frame1, song_slider1
    options = playlist_options()
    text = names_dropdown.get().strip()
    if (text in options):
        global forward_image1, backward_image1, pause_image1, stop_image1, play_image1, paused, selected_song_listbox_playlist
        paused = False
        stop()
        window_stack[len(window_stack) - 1].wm_withdraw()
        window = Toplevel(bg="black")
        window.title("MP3 PLAYER")
        window.geometry("1100x660+100+100")
        window.iconbitmap(r"mp3.ico")
        label_text = f"--- Playlist Name : {text} ---"
        selected_song_label = Label(window, text=label_text, width=50, height=2, bg="white",
                                    font=("helvetica", 12))
        selected_song_label.pack(pady=20)
        selected_song_label2 = Label(window, width=50, height=1, bg="white",
                                    font=("helvetica", 10))
        selected_song_label2.pack()
        playlist_frame = Frame(window, bg="#C0C0C0", width=175, height=20)
        playlist_frame.pack(pady=3)
        selected_song_listbox_playlist = Listbox(playlist_frame, bg="#C0C0C0", width=175, height=23)
        selected_song_listbox_playlist.grid(row=0, column=0)
        scroll1 = Scrollbar(playlist_frame, orient='vertical', command=selected_song_listbox_playlist.yview)
        selected_song_listbox_playlist.config(yscrollcommand=scroll1.set)
        scroll1.grid(row=0, column=1, sticky=N + S + E)
        scroll2 = Scrollbar(playlist_frame, orient='horizontal', command=selected_song_listbox_playlist.xview)
        selected_song_listbox_playlist.config(xscrollcommand=scroll2.set)
        scroll2.grid(row=1, column=0, columnspan=2, sticky=W + E + S)
        song_slider_frame1 = LabelFrame(window, text="00:00:00  of  00:00:00", bg="black", fg="white",
                                       labelanchor='n')
        song_slider_frame1.pack()
        song_slider1 = ttk.Scale(song_slider_frame1, from_=0, to=100, value=0, length=1070, command= update_song_slider1)
        song_slider1.pack()
        button_frame = Frame(window, bg="black")
        button_frame.pack(pady=4)
        forward_image1 = PhotoImage(file=r"forward.png")
        backward_image1 = PhotoImage(file=r"backward.png")
        pause_image1 = PhotoImage(file=r"pause.png")
        stop_image1 = PhotoImage(file=r"stop.png")
        play_image1 = PhotoImage(file=r"play.png")
        forward_button = Button(button_frame, image=forward_image1, bd=3, command=forward_current)
        forward_button.grid(row=0, column=5, padx=12)
        backward_button = Button(button_frame, image=backward_image1, bd=3, command=backward_current)
        backward_button.grid(row=0, column=1, padx=12)
        pause_button = Button(button_frame, image=pause_image1, bd=3, command=pause_current)
        pause_button.grid(row=0, column=3, padx=12)
        play_button = Button(button_frame, image=play_image1, bd=3, command=lambda: play_current(0))
        play_button.grid(row=0, column=4, padx=12)
        stop_button = Button(button_frame, image=stop_image1, bd=3, command=stop_current)
        stop_button.grid(row=0, column=2, padx=12)
        window_stack.append(window)
        window_stack[len(window_stack) - 1].protocol("WM_DELETE_WINDOW", on_closing)
        conn = sqlite3.connect(playlists)
        cur = conn.cursor()
        sql = f"SELECT * FROM {text}"
        results = cur.execute(sql)
        total = 0
        found = 0
        for row in results:
            title = row[0]
            location = row[1]
            total+=1
            try:
                pygame.mixer.music.load(location)
                found += 1
                vstr = f"{found}.  Song Title -> " + title + "  ----------  File Location -> " + location
                selected_song_listbox_playlist.insert(END, vstr)
            except:
                continue
        selected_song_label2.config(text=f"Total songs in playlist : {total} || Songs found in location: {found}")
        volume_frame1 = LabelFrame(window, text="Volume", bg="black", fg="white")
        volume_frame1.pack()
        volume_slider1 = ttk.Scale(volume_frame1, from_=0, to=1, value=1, length=150, command=volume1)
        volume_slider1.pack()
        status_bar = Label(window_stack[len(window_stack) - 1], text="*Close the window to go back to previous window",
                           anchor="e", relief=RIDGE)
        status_bar.pack(fill=X, side=BOTTOM)
    else:
        messagebox.showerror("Playlist not found!", "Enter a valid playlist name.")

def add_more_songs(playlist_name):
    selected_songs = filedialog.askopenfilenames(title="Select songs to add", filetypes=(("mp3 files", "*.mp3"),))
    if selected_songs:
        ok = messagebox.askokcancel("Add songs to playlist", "Are you sure you want to add the song(s) in playlist?")
        if ok:
            conn = sqlite3.connect(playlists)
            cur = conn.cursor()
            for song in selected_songs:
                title = get_title(song)
                sql = f'''INSERT OR REPLACE INTO {playlist_name} VALUES("{title}","{song}")'''
                cur.execute(sql)
            w = window_stack[len(window_stack) - 1]
            window_stack.pop()
            w.destroy()
            w = window_stack[len(window_stack) - 1]
            window_stack.pop()
            w.destroy()
            conn.commit()
            conn.close()
            open_my_playlists()
            edit_playlist(1, playlist_name)

def remove_songs_from_playlist(box, lines, playlist_name):
    if lines:
        res = messagebox.askyesno("Remove songs from playlist", "Are you sure you want to remove the song(s) from playlist?")
        if res:
            conn = sqlite3.connect(playlists)
            cur = conn.cursor()
            for line in lines:
                line = box.get(line)
                song = get_song_location(line)
                title = get_title(song)
                sql = f'''DELETE FROM {playlist_name} WHERE title="{title}" AND song="{song}" '''
                cur.execute(sql)
            w = window_stack[len(window_stack) - 1]
            window_stack.pop()
            w.destroy()
            w = window_stack[len(window_stack) - 1]
            window_stack.pop()
            w.destroy()
            conn.commit()
            conn.close()
            open_my_playlists()
            edit_playlist(1, playlist_name)


def delete_playlist(playlist_name):
    res = messagebox.askyesno("Delete playlist",
                                "Are you sure you want to delete the playlist?")
    if res:
        sql = f"DROP TABLE {playlist_name}"
        conn = sqlite3.connect(playlists)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()
        w = window_stack[len(window_stack) - 1]
        window_stack.pop()
        w.destroy()
        w = window_stack[len(window_stack) - 1]
        window_stack.pop()
        w.destroy()
        messagebox.showinfo("Playlist deleted!",
                            "You deleted a playlist.")
        open_my_playlists()

def edit_playlist(edited,text):
    stop()
    options = playlist_options()
    if edited==0:
        text = names_dropdown.get().strip()
    if (text in options):
        global paused
        paused = False
        stop()
        window_stack[len(window_stack) - 1].wm_withdraw()
        window = Toplevel(bg="black")
        window.title("MP3 PLAYER")
        window.geometry("1100x615")
        window.iconbitmap(r"mp3.ico")
        label_text = f"--- Playlist Name : {text} ---"
        selected_song_label = Label(window, text=label_text, width=50, height=2, bg="white",
                                    font=("helvetica", 12))
        selected_song_label.pack(pady=25)
        selected_song_label2 = Label(window, width=50, height=1, bg="white",
                                     font=("helvetica", 10))
        selected_song_label2.pack()
        playlist_frame = Frame(window, bg="#C0C0C0", width=175, height=20)
        playlist_frame.pack(pady=8)
        edit_listbox = Listbox(playlist_frame, bg="#C0C0C0", width=175, height=21, selectmode="multiple")
        edit_listbox.grid(row=0, column=0)
        scroll1 = Scrollbar(playlist_frame, orient='vertical', command=edit_listbox.yview)
        edit_listbox.config(yscrollcommand=scroll1.set)
        scroll1.grid(row=0, column=1, sticky=N + S + E)
        scroll2 = Scrollbar(playlist_frame, orient='horizontal', command=edit_listbox.xview)
        edit_listbox.config(xscrollcommand=scroll2.set)
        scroll2.grid(row=1, column=0, columnspan=2, sticky=W + E + S)
        window_stack.append(window)
        window_stack[len(window_stack) - 1].protocol("WM_DELETE_WINDOW", on_closing)
        conn = sqlite3.connect(playlists)
        cur = conn.cursor()
        sql = f"SELECT * FROM {text}"
        results = cur.execute(sql)
        total = 0
        found = 0
        for row in results:
            title = row[0]
            location = row[1]
            total += 1
            try:
                pygame.mixer.music.load(location)
                found += 1
                vstr = f"{found}.  Song Title -> " + title + "  ----------  File Location -> " + location
                edit_listbox.insert(END, vstr)
            except:
                continue
        selected_song_label2.config(text=f"Total songs in playlist : {total} || Songs found in location: {found}")
        add_button = Button(window, text="ADD NEW SONG", font=("helvetica", 10), fg="white", bg="#03509E",
                             activebackground="#377BFF",
                             bd=2, height=1, width=30, command=lambda:add_more_songs(text))
        add_button.pack(pady=5)
        remove_button = Button(window, text="REMOVE SELECTED SONG(S)", font=("helvetica", 10), fg="white", bg="#03509E",
                             activebackground="#377BFF",
                             bd=2, height=1, width=30, command=lambda: remove_songs_from_playlist(edit_listbox, edit_listbox.curselection(), text))
        remove_button.pack(pady=5)
        delete_button = Button(window, text="DELETE PLAYLIST", font=("helvetica", 10), fg="white", bg="#03509E",
                             activebackground="#377BFF",
                             bd=2, height=1, width=30, command=lambda: delete_playlist(text))
        delete_button.pack(pady=5)
        status_bar = Label(window_stack[len(window_stack) - 1], text="*Close the window to go back to previous window",
                           anchor="e", relief=RIDGE)
        status_bar.pack(fill=X, side=BOTTOM)
    else:
        messagebox.showerror("Playlist not found!", "Enter a valid playlist name.")

def open_my_playlists():
    stop()
    window_stack[len(window_stack) - 1].wm_withdraw()
    global top, playlist_label, playlist_listbox, create_playlist, playlist_frame, scroll, names_dropdown
    top = Toplevel(bg="#C0C0C0")
    top.title("MP3 PLAYER-My Playlists")
    top.geometry("1000x558")
    top.iconbitmap(r"mp3.ico")
    playlist_label = Label(top, text="--- MY PLAYLISTS ---", width=50, height=2, bg="black", fg="white", font=("helvetica", 10))
    playlist_label.pack(pady=20)
    playlist_frame = Frame(top, bg="black", height=20)
    conn = sqlite3.connect(playlists)
    cur = conn.cursor()
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' ''')

    if cur.fetchone()[0] == 0:  # if the count is 1, table exists
        playlist_frame.pack(expand=1, fill=BOTH)
        empty_label = Label(playlist_frame, text="NO PLAYLIST FOUND!", width=40, bg="#EBECF0", fg="gray",
                               font=("helvetica", 15))
        empty_label.pack(pady=30)
    else:
        playlist_frame.pack()
        playlist_frame.config(bg="white")
        playlist_names_label = Label(playlist_frame, text="My Playlists", width=118, height=2, font=("helvetica", 10), anchor='w',
                                     relief="groove", bd=2, highlightthickness=0)
        playlist_names_label.grid(row=0, column=0, columnspan=2)
        playlist_listbox = Listbox(playlist_frame, bg="black", fg="white", width=134, height=18, borderwidth=3, highlightthickness=1,
                                   activestyle="none", selectbackground="black", font=("helvetica", 10))
        playlist_listbox.grid(row=1, column=0, columnspan=2)
        show_playlists()
        scroll = Scrollbar(playlist_frame, orient='vertical', command=playlist_listbox.yview)
        playlist_listbox.config(yscrollcommand=scroll.set)
        scroll.grid(row=1, column=1, sticky=N+S+E)

        search_label = Label(playlist_frame, width=113, height=2, font=("helvetica", 10),
                                     anchor='w',
                                     relief="groove", bd=1, highlightthickness=0)
        search_label.grid(row=2, column=0, columnspan=3)
        search_name_label = Label(search_label, text="Enter a playlist name to play or edit : ",  anchor="w", height=2, width=27, font=("helvetica", 10))
        search_name_label.grid(row=0, column=0)
        options = playlist_options()
        selected = StringVar()
        selected.set(options[0])
        names_dropdown = ttk.Combobox(search_label, textvariable=selected, values=options)
        names_dropdown.config(width=80, height=2)
        names_dropdown.grid(row=0, column=1, padx=5)
        play_button = Button(search_label, text="Play", font=("helvetica", 10), fg="white", bg="#03509E",
                                 activebackground="#377BFF",
                                 bd=2, height=1, width=12, command=play_playlist)
        play_button.grid(row=0, column=2)
        edit_button = Button(search_label, text="Edit", font=("helvetica", 10), fg="white", bg="#03509E",
                                 activebackground="#377BFF",
                                 bd=2, height=1, width=12, command=lambda: edit_playlist(0," "))
        edit_button.grid(row=0, column=3)
    create_playlist = Button(top, text="CREATE A NEW PLAYLIST", font=("helvetica", 10), fg="white", bg="#03509E",
                             activebackground="#377BFF",
                             bd=2, height=2, width=30, command=create_new_playlist_window)
    create_playlist.pack(pady=14)
    window_stack.append(top)
    window_stack[len(window_stack) - 1].protocol("WM_DELETE_WINDOW", on_closing)
    status_bar = Label(window_stack[len(window_stack) - 1], text="*Close the window to go back to previous window", anchor="e", relief=RIDGE)
    status_bar.pack(fill=X, side=BOTTOM)

window_menu = Menu(main_window)
main_window.config(menu=window_menu)
add_song_menu = Menu(window_menu)
remove_song_menu = Menu(window_menu)
window_menu.add_cascade(label="  Add song to list   ", menu=add_song_menu)
window_menu.add_cascade(label="Remove song from list", menu=remove_song_menu)
window_menu.add_command(label="     My Playlists    ", command=open_my_playlists)
add_song_menu.add_command(label="Add a song", command=add_a_song)
add_song_menu.add_command(label="Add multiple songs", command=add_multiple_songs)
remove_song_menu.add_command(label="Remove the selected song", command=remove_the_selected_song)
remove_song_menu.add_command(label="Remove all songs", command=remove_all_songs)

selected_song_label = Label(main_window, text="--- ADD SONGS TO LISTEN ---", width=50, height=2, bg="#C0C0C0",
                            font=("helvetica", 10))
selected_song_label.pack(pady=25)
playlist_frame = Frame(main_window, bg="#C0C0C0", width=175, height=22)
playlist_frame.pack(pady=3)
selected_song_listbox = Listbox(playlist_frame, bg="#C0C0C0", width=175, height=22)
selected_song_listbox.grid(row=0, column=0, sticky=W+E)
song_slider_frame = LabelFrame(main_window, text="00:00:00  of  00:00:00", bg="black", fg="white", labelanchor='n')
song_slider_frame.pack()
song_slider = ttk.Scale(song_slider_frame, from_=0, to=100, value=0, length=1070, command=update_song_slider)
song_slider.pack()
button_frame = Frame(main_window, bg="black")
button_frame.pack(pady=8)
forward_image = PhotoImage(file=r"forward.png")
backward_image = PhotoImage(file=r"backward.png")
pause_image = PhotoImage(file=r"pause.png")
stop_image = PhotoImage(file=r"stop.png")
play_image = PhotoImage(file=r"play.png")
forward_button = Button(button_frame, image=forward_image, bd=3, command=forward)
forward_button.grid(row=0, column=5, padx=12)
backward_button = Button(button_frame, image=backward_image, bd=3, command=backward)
backward_button.grid(row=0, column=1, padx=12)
pause_button = Button(button_frame, image=pause_image, bd=3, command=pause)
pause_button.grid(row=0, column=3, padx=12)
play_button = Button(button_frame, image=play_image, bd=3, command=lambda: play(0))
play_button.grid(row=0, column=4, padx=12)
stop_button = Button(button_frame, image=stop_image, bd=3, command=stop)
stop_button.grid(row=0, column=2, padx=12)
volume_frame = LabelFrame(main_window, text="Volume", bg="black", fg="white")
volume_frame.pack()
volume_slider = ttk.Scale(volume_frame, from_=0, to=1, value=1, length=150, command=volume)
volume_slider.pack()
scroll1 = Scrollbar(playlist_frame, orient='vertical', command=selected_song_listbox.yview)
selected_song_listbox.config(yscrollcommand=scroll1.set)
scroll1.grid(row=0, column=1, sticky=N + S + E)
scroll2 = Scrollbar(playlist_frame, orient='horizontal', command=selected_song_listbox.xview)
selected_song_listbox.config(xscrollcommand=scroll2.set)
scroll2.grid(row=1, column=0, columnspan=2, sticky=W + E + S)
window_stack.append(main_window)

main_window.mainloop()