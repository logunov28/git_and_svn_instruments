#!/usr/bin/env python

import datetime
import sys
import os.path
import configparser
import threading
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from time import sleep
import tkcalendar
import babel.numbers
import pyperclip
import ctypes
from platform import system
from tendo import singleton
import pygetwindow as gw

#def show_exception_and_exit(exc_type, exc_value, tb):
#    w = showerror(title="Error :(", message="SVN client has crashed...")

#sys.excepthook = show_exception_and_exit

try:
    me = singleton.SingleInstance()
except:
    try:
        window = gw.getWindowsWithTitle('SVN client')[0]
        window.activate()
        window.restore()
    except:
        pass
    sys.exit(0)


limit = 100
script_dir = os.getcwd()
monitoring_flag = 0
rev = ''
get_log_counter = 0
refreshes = 0
current_rev = ''


def get_log_first(path, limit, team, n):
    global log_to_show, current_rev
    try:
        os.chdir(path)
    except:
        return None
    current_rev = os.popen('svn info --show-item last-changed-revision').read()
    url = os.popen('svn info --show-item url').read()

    try:
        if dates_enabled.get() == 1:
            date1 = date_from.get()
            if len(date1) == 0:
                date_from.set_date(datetime.datetime.today())
                date1 = date_from.get()
            date2 = date_to.get()
            if len(date2) == 0:
                date_to.set_date(datetime.datetime.today())
                date2 = date_to.get()
            date1 = datetime.datetime.strptime(date1, '%d/%m/%Y')
            date2 = datetime.datetime.strptime(date2, '%d/%m/%Y')
            date1 = list(reversed((str(date1).split()[0]).split()))[0]
            date2 = list(reversed((str(date2 + datetime.timedelta(days=1)).split()[0]).split()))[0]
            if team != '':
                log = os.popen('svn log --search "' + team + '" -r {' + str(date1) + '}:{' + str(date2) + '} ' + url).read()
            else:
                log = os.popen('svn log' + ' -r {' + str(date1) + '}:{' + str(date2) + '} ' + url).read()
            log = list(reversed(log.split('------------------------------------------------------------------------')))
        elif revisions_enabled.get() == 1:
            revision_from = entry_rev_from.get()
            revision_to = entry_rev_to.get()
            revision_from = ''.join(filter(lambda x: x.isdigit(), revision_from))
            revision_to = ''.join(filter(lambda x: x.isdigit(), revision_to))
            if len(revision_from) == 0:
                revision_from = 'HEAD'
            if len(revision_to) == 0:
                revision_to = 'HEAD'
            if team != '':
                log = os.popen('svn log --search "' + team + '" -r ' + str(revision_from) + ':' + str(revision_to) + ' ' + url).read()
            else:
                log = os.popen('svn log' + ' -r ' + str(revision_from) + ':' + str(revision_to) + ' ' + url).read()
            log = list(reversed(log.split('------------------------------------------------------------------------')))
            last_num = log[-2].split('|')[0]
            last_num = ''.join(filter(lambda x: x.isdigit(), last_num))
            first_num = log[1].split('|')[0]
            first_num = ''.join(filter(lambda x: x.isdigit(), first_num))
            if int(first_num) < int(last_num):
                log = list(reversed(log))
        else:
            if limit != 0:
                if team != '':
                    log = os.popen('svn log --search "' + team + '" -l ' + str(limit) + ' ' + url).read()
                else:
                    log = os.popen('svn log' + ' -l ' + str(limit) + ' ' + url).read()
            else:
                if team != '':
                    log = os.popen('svn log --search "' + team + '" ' + url).read()
                else:
                    log = os.popen('svn log ' + url).read()
            if log == '':
                return None
            log = log.split('------------------------------------------------------------------------')
    except:
        if limit != 0:
            if team != '':
                log = os.popen('svn log --search "' + team + '" -l ' + str(limit) + ' ' + url).read()
            else:
                log = os.popen('svn log' + ' -l ' + str(limit) + ' ' + url).read()
        else:
            if team != '':
                log = os.popen('svn log --search "' + team + '" ' + url).read()
            else:
                log = os.popen('svn log ' + url).read()
        if log == '':
            return None
        log = log.split('------------------------------------------------------------------------')

    list_revs = []
    for i in range(len(log)):
        log_string = log[i]
        log_string = log_string.split('\n')
        if len(log_string) > 2:
            rev = log_string[1].split(' | ')[0][1:]
            if int(rev) == int(current_rev):
                rev = '-> ' + rev
            author = log_string[1].split(' | ')[1]
            date = log_string[1].split(' | ')[2][:19]
            comment = log_string[3]
            to_list_revs = rev + ' | ' + author + ' | ' + date + ' | ' + comment
            list_revs.append(to_list_revs)
    os.chdir(script_dir)
    return list_revs


def get_log(path, team, n):
    global log_to_show, limit, get_log_counter, refreshes
    refreshes += 1
    try:
        gray()
        progressbar.start()
    except:
        pass
    log_to_show = get_log_first(path, limit, team, 0)
    if current_rev != '':
        window.title("SVN client. Current revision: " + current_rev)
    else:
        window.title("SVN client")

    if log_to_show == None:
        limit = 100
        if refreshes > 1:
            w = showerror(title="Error", message="Set a correct path.")


        try:
            ungray()
            progressbar.stop()
        except:
            pass
        return
    listbox.delete(0, 'end')
    to_insert = log_to_show
    to_insert.reverse()

    for i in range(len(to_insert)):
        listbox.insert(0, log_to_show[i])

    try:
        for i in range(len(log_to_show)):
            if log_to_show[i].startswith('-> '):
                listbox.itemconfig(len(log_to_show) - i - 1, {'bg': 'black'})
                listbox.itemconfig(len(log_to_show) - i - 1, {'fg': 'white'})
                listbox.see(len(log_to_show) - i - 1)
    except:
        pass
    try:
        ungray()
        progressbar.stop()
    except:
        pass



def is_locked(path, script_dir):
    try:
        os.rename(path, path)
        return False
    except OSError:
        return True



def monitor(path, team, n):
    global monitoring_flag
    os.chdir(path)
    start_rev = os.popen('svn log --revision HEAD').read().split('\n')[1].split(' ')[0][1:]

    while True:
        for i in range(60):
            sleep(1)
            if monitoring_flag == 0:
                monitor_btn['state'] = 'normal'
                return
        log = os.popen('svn log --revision HEAD').read()
        try:
            info = log.split('\n')[1]
            message = log.split('\n')[3]
            monitor_rev = info.split(' ')[0][1:]
        except IndexError:
            continue
        if team in message and monitor_rev != start_rev:
            w = showinfo(title="New build!", message="Rev: " + monitor_rev)
            start_rev = monitor_rev


def update(path, rev, n):
    gray()
    progressbar.start()

    root = Tk()

    def flash_window():
        hwnd = int(root.wm_frame(), 16)
        ctypes.windll.user32.FlashWindow(hwnd, True)

    root.title('Updating to rev. ' + rev)
    output = ScrolledText(root)
    output.pack(fill='both', expand=True)


    def output_insert():
        update = ''
        if 'Windows' in system():
            command = 'cmd /c svn up "' + path + '" -r ' + rev + ' 2>&1'
        else:
            command = 'svn up "' + path + '" -r ' + rev + ' 2>&1'
        proc = os.popen(command)
        while True:
            text = proc.readline()
            if 'At revision' in text or 'Updated to revision ' in text or 'E155037' in text or 'E155009' in text or 'E720005' in text:
                try:
                    progressbar.stop()
                    root.deiconify()
                    root.focus()
                    root.attributes("-topmost", True)
                    if 'Windows' in system():
                        flash_window()
                    output.insert("end", text)
                    break
                except:
                    pass #Если окно хода обновления закроют раньше времени
            try:
                output.insert("end", text)
                output.see("end")
            except:
                pass #Если окно хода обновления закроют раньше времени

        progressbar.stop()

    output_insert_thread = threading.Thread(target=output_insert, daemon=True)
    output_insert_thread.start()
    root.mainloop()

    ungray()
    progressbar.stop()


def cleanup(path, n):
    global script_dir
    gray()
    progressbar.start()
    os.chdir(path)
    cleanup = os.popen('svn cleanup').read()
    status = os.popen('svn status').read()
    if ' L  ' in status:
        w = showerror(title="Error!", message="Clean up failed...")
    else:
        w = showinfo(title="Success!", message="Clean up finished.")
    os.chdir(script_dir)
    ungray()
    progressbar.stop()


def on_exit():
    global teams, paths
    if combobox_team.get() not in teams:
        team_number = 0
    else:
        team_number = combobox_team.current()
    if combobox_path.get() not in paths:
        path_number = 0
    else:
        path_number = combobox_path.current()

    if (str(type(teams)) == "<class 'list'>") and (str(type(paths)) == "<class 'list'>"):
        
        teams = ';'.join(sorted(teams))
        paths = ';'.join(sorted(paths))

        # Write ini
        os.chdir(script_dir)
        to_ini = f'[vars]\nteam = {teams}\npath = {paths}\nteam_number = {team_number}\npath_number = {path_number}'
        file = open('svn_client_cfg.ini', "w", encoding='utf-8')
        file.write(to_ini)
        file.close()
        sys.exit(0)


####################################################################################################


###########
#         #
#   GUI   #
#         #
###########

# Read INI

cfg = configparser.ConfigParser()

try:
    cfg.read('svn_client_cfg.ini', encoding='utf-8')
    teams = sorted(cfg.get("vars", "team").split(';'))
    paths = sorted(cfg.get("vars", "path").split(';'))
    team_number = cfg.get("vars", "team_number")
    path_number = cfg.get("vars", "path_number")
    team = teams[int(team_number)]
    path = paths[int(path_number)]

except:
    file = open('svn_client_cfg.ini', "w", encoding='utf-8')
    teams = ''
    paths = ''
    team_number = 0
    path_number = 0
    to_ini = f'[vars]\nteam = {teams}\npath = {paths}\nteam_number = {team_number}\npath_number = {path_number}'
    file.write(to_ini)
    file.close()
    cfg.read('svn_client_cfg.ini', encoding='utf-8')
    teams = cfg.get("vars", "team").split(';')
    paths = cfg.get("vars", "path").split(';')
    team_number = cfg.get("vars", "team_number")
    path_number = cfg.get("vars", "path_number")
    team = teams[int(team_number)]
    path = paths[int(path_number)]

try:
    log_to_show = get_log_first(path, limit, team, 0)
except:
    log_to_show = []

# Create a window
window = Tk()
if current_rev == '':
    window.title("SVN client")
else:
    window.title("SVN client. Current revision: " + current_rev)
window.geometry("800x500")
window.minsize(650, 370)
window.resizable(True, True)
try:
    window.iconbitmap(default="svn_client_icon.ico")
except:
    pass
window.protocol("WM_DELETE_WINDOW", on_exit)


# Bind hotkeys in russian layout
def keys(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

    if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
        event.widget.event_generate("<<SelectAll>>")


window.bind("<Control-KeyPress>", keys)


def enter_data():
        team = combobox_team.get()
        team = team.replace('"', '')
        path = combobox_path.get()
        path = path.replace('"', '')
        return team, path


def click_add_team_btn():
    global teams
    if combobox_team.get() not in teams:
        teams.append(combobox_team.get())
    teams = sorted(teams)
    combobox_team['values'] = teams


def click_del_team_btn():
    global teams
    if combobox_team.get() != "" and combobox_team.get() in teams:
        teams.remove(combobox_team.get())
    combobox_team['values'] = teams
    combobox_team.delete(0, END)


def click_add_path_btn():
    global paths
    if combobox_path.get() not in paths:
        paths.append(combobox_path.get())
    paths = sorted(paths)
    combobox_path['values'] = paths


def click_del_path_btn():
    global paths
    if combobox_path.get() != "" and combobox_path.get() in paths:
        paths.remove(combobox_path.get())
    combobox_path['values'] = paths
    combobox_path.delete(0, END)


def gray_dates():
    if dates_enabled.get() == 1:
        date_from['state'] = 'normal'
        date_to['state'] = 'normal'
        entry_rev_from.delete(0, END)
        entry_rev_to.delete(0, END)
        date_from.delete(0, END)
        date_to.delete(0, END)
        date_from.bind("<Button-3>", entry_context_menu)
        date_to.bind("<Button-3>", entry_context_menu)
        revisions_enabled.set(0)
        entry_rev_from['state'] = 'disabled'
        entry_rev_to['state'] = 'disabled'
        entry_rev_from.unbind("<Button-3>")
        entry_rev_to.unbind("<Button-3>")

    else:
        date_from.delete(0, END)
        date_to.delete(0, END)
        date_from['state'] = 'disabled'
        date_to['state'] = 'disabled'
        date_from.unbind("<Button-3>")
        date_to.unbind("<Button-3>")


def gray_revisions():
    if revisions_enabled.get() == 1:
        entry_rev_from['state'] = 'normal'
        entry_rev_to['state'] = 'normal'
        date_from.delete(0, END)
        date_to.delete(0, END)
        entry_rev_from.delete(0, END)
        entry_rev_to.delete(0, END)
        entry_rev_from.bind("<Button-3>", entry_context_menu)
        entry_rev_to.bind("<Button-3>", entry_context_menu)
        dates_enabled.set(0)
        date_from['state'] = 'disabled'
        date_to['state'] = 'disabled'
        date_from.unbind("<Button-3>")
        date_to.unbind("<Button-3>")

    else:
        entry_rev_from.delete(0, END)
        entry_rev_to.delete(0, END)
        entry_rev_from['state'] = 'disabled'
        entry_rev_to['state'] = 'disabled'
        entry_rev_from.unbind("<Button-3>")
        entry_rev_to.unbind("<Button-3>")


def click_update_btn():
    global rev
    if str(update_btn['state']) == 'normal':
        if rev_enabled.get() == 1:
            rev = entry_revision.get()
            rev = ''.join(filter(lambda x: x.isdigit(), rev))
            entry_revision.delete(0, END)
            entry_revision.insert(0, rev)
        if rev == '':
            w = showerror(title="Error!", message="Revision is not chosen!")
            return
        if combobox_path.get() == "":
            w = showerror(title="Error!", message="Path is empty!")
        else:
            team, path = enter_data()
            if is_locked(path, script_dir):
                w = showwarning(title="Error!", message="Files you try to update are locked. Kill processes which lock these files and press ОК")
            update_thread = threading.Thread(target=update, args=(path, rev, 0), daemon=True)
            update_thread.start()
        rev = ''


def click_refresh_btn():
    global log_to_show
    team, path = enter_data()
    refresh_thread = threading.Thread(target=get_log, args=(path, team, 0), daemon=True)
    refresh_thread.start()


def click_next_100_btn():
    global log_to_show, limit
    team, path = enter_data()
    limit += 100
    next_100_thread = threading.Thread(target=get_log, args=(path, team, 0), daemon=True)
    next_100_thread.start()


def click_show_all_btn():
    global log_to_show, limit
    team, path = enter_data()
    limit = 0
    show_all_thread = threading.Thread(target=get_log, args=(path, team, 0), daemon=True)
    show_all_thread.start()


def click_cleanup_btn():
    path = combobox_path.get()
    path = path.replace('"', '')
    cleanup_thread = threading.Thread(target=cleanup, args=(path, 0), daemon=True)
    cleanup_thread.start()


def click_monitor_btn():
    global monitoring_flag
    path = combobox_path.get()
    path = path.replace('"', '')
    monitor_thread = threading.Thread(target=monitor, args=(path, team, 0), daemon=True)
    if monitor_btn['text'] == 'Start monitoring':
        monitor_btn['text'] = 'Stop monitoring'
        monitoring_flag = 1
        monitor_thread.start()
    else:
        monitor_btn['text'] = 'Start monitoring'
        monitor_btn['state'] = 'disabled'
        monitoring_flag = 0


def click_reset_btn():
    global limit
    limit = 100
    click_refresh_btn()

def onselect(event):
    global rev, message
    w = event.widget
    i = int(w.curselection()[0])
    value = w.get(i)
    value = value.split(' |')
    if '>' in value[0]:
        rev = value[0][3:]
    else:
        rev = value[0]
    message = []
    for i in range(len(value)):
        if i > 2:
            message.append(value[i])
    message = ' |'.join(message)
    rev_enabled.set(0)
    entry_revision['state'] = 'disabled'
    entry_revision.unbind("<Button-3>")


def copy_revision():
    pyperclip.copy(rev)


def copy_message():
    pyperclip.copy(message[1:])


def listbox_right_click(event):
    listbox.selection_clear(0, END)
    listbox.selection_set(listbox.nearest(event.y))
    listbox.activate(listbox.nearest(event.y))
    onselect(event)
    listbox_context_menu = Menu(window, tearoff=0)
    listbox_context_menu.add_command(label="Copy revision", command=copy_revision)
    listbox_context_menu.add_command(label="Copy message", command=copy_message)
    listbox_context_menu.add_separator()
    listbox_context_menu.add_command(label="Update to revision", command=click_update_btn)

    def do_popup(event):
        try:
            listbox_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            listbox_context_menu.grab_release()
    do_popup(event)


def listbox_hovering_enter(event):
    listbox['highlightbackground'] = "azure3"


def listbox_hovering_leave(event):
    listbox['highlightbackground'] = "azure2"
    for i in range(listbox.index("end")):
        if listbox.itemcget(i, "background") != 'black':
            listbox.itemconfig(i, {'bg': 'white'})



def listbox_motion(event):
    if listbox.itemcget(listbox.nearest(event.y), "background") != 'black':
        listbox.itemconfig(listbox.nearest(event.y), {'bg': 'azure2'})
    for i in range(listbox.index("end")):
        if i != listbox.nearest(event.y) and listbox.itemcget(i, "background") != 'black':
            listbox.itemconfig(i, {'bg': 'white'})



def gray():
    combobox_team['state'] = 'disabled'
    combobox_team.unbind("<Button-3>")
    combobox_path['state'] = 'disabled'
    combobox_path.unbind("<Button-3>")
    update_btn['state'] = 'disabled'
    update_btn.state(["disabled"])
    refresh_btn['state'] = 'disabled'
    next_100_btn['state'] = 'disabled'
    show_all_btn['state'] = 'disabled'
    cleanup_btn['state'] = 'disabled'


def ungray():
    combobox_team['state'] = 'normal'
    combobox_team.bind("<Button-3>", entry_context_menu)
    combobox_path['state'] = 'normal'
    combobox_path.bind("<Button-3>", entry_context_menu)
    update_btn['state'] = 'normal'
    update_btn.state(["!disabled"])
    refresh_btn['state'] = 'normal'
    next_100_btn['state'] = 'normal'
    show_all_btn['state'] = 'normal'
    cleanup_btn['state'] = 'normal'


def gray_entry_revision():
    if rev_enabled.get() == 1:
        entry_revision['state'] = 'normal'
        listbox.selection_clear(0, END)
        entry_revision.bind("<Button-3>", entry_context_menu)
    else:
        entry_revision['state'] = 'disabled'
        entry_revision.unbind("<Button-3>")


def press_f5(event):
    click_refresh_btn()


def press_ctrl_enter(event):
    click_update_btn()


def ask_path(event):
    folder_selected = filedialog.askdirectory()
    if 'Windows' in system():
        folder_selected.replace('/', '\\')
    if folder_selected != '':
        combobox_path.set(folder_selected)

# FILTER AREA

frame_filter = ttk.Frame()
frame_filter.pack(anchor='n', fill=X, expand=False, pady=6)

frame_filter_left = ttk.Frame(frame_filter)
frame_filter_left.pack(side=LEFT, fill=X, expand=False)
label_team = ttk.Label(frame_filter_left, text="Filter:")
label_team.pack(anchor='nw', padx=6, pady=6)

frame_filter_center = ttk.Frame(frame_filter)
frame_filter_center.pack(side=LEFT, fill=X, expand=True)


teams_var = StringVar(value=teams[int(team_number)])
combobox_team = ttk.Combobox(frame_filter_center, width=60, textvariable=teams_var, values=sorted(teams))
combobox_team.pack(padx=6, pady=6, fill='x')

frame_filter_right = ttk.Frame(frame_filter)
frame_filter_right.pack(side=LEFT, fill=X, expand=False, padx=6)
add_team_btn = ttk.Button(frame_filter_right, text="Add", command=click_add_team_btn, width=5)
add_team_btn.pack(side=LEFT, padx=6)

del_team_btn = ttk.Button(frame_filter_right, text="Del", command=click_del_team_btn, width=5)
del_team_btn.pack(side=LEFT)


# PATH AREA

frame_path = ttk.Frame()
frame_path.pack(anchor='n', fill=X, expand=False, pady=16)

frame_path_left = ttk.Frame(frame_path)
frame_path_left.pack(side=LEFT, fill=X, expand=False)
label_path = Label(frame_path_left, text="Path:", fg="blue", underline=True, cursor="hand2")
label_path.pack(anchor='nw', padx=6, pady=3)
label_path.bind("<Button-1>", ask_path)

frame_path_center = ttk.Frame(frame_path)
frame_path_center.pack(side=LEFT, fill=X, expand=True)
paths_var = StringVar(value=paths[int(path_number)])
combobox_path = ttk.Combobox(frame_path_center, width=60, textvariable=paths_var, values=sorted(paths))
combobox_path.pack(padx=6, pady=6, fill='x')

frame_path_right = ttk.Frame(frame_path)
frame_path_right.pack(side=LEFT, fill=X, expand=False, padx=6)
add_path_btn = ttk.Button(frame_path_right, text="Add", command=click_add_path_btn, width=5)
add_path_btn.pack(side=LEFT, padx=6)

del_path_btn = ttk.Button(frame_path_right, text="Del", command=click_del_path_btn, width=5)
del_path_btn.pack(side=LEFT)

# CALENDAR AREA

frame_dates = ttk.Frame()
frame_dates.pack(anchor='n', fill=X, expand=False, pady=16)

dates_enabled = IntVar(value=0)
dates_checkbox = ttk.Checkbutton(frame_dates, text=' Date range:', variable=dates_enabled, command=gray_dates)
dates_checkbox.pack(side=LEFT, padx=6, pady=3)

date_from = tkcalendar.DateEntry(frame_dates, locale='en_UK')
date_from.pack(side=LEFT, padx=1, pady=3)
date_from.delete(0, END)

label_to1 = ttk.Label(frame_dates, text="-")
label_to1.pack(side=LEFT, padx=1, pady=3)

date_to = tkcalendar.DateEntry(frame_dates, locale='en_UK')
date_to.pack(side=LEFT, padx=1, pady=3)
date_to.delete(0, END)
date_from['state'] = 'disabled'
date_to['state'] = 'disabled'

label_empty1 = ttk.Label(frame_dates, text="     ")
label_empty1.pack(side=LEFT, padx=6, pady=6)

revisions_enabled = IntVar(value=0)
revisions_checkbox = ttk.Checkbutton(frame_dates, text=' Revision range:', variable=revisions_enabled, command=gray_revisions)
revisions_checkbox.pack(side=LEFT, padx=6, pady=3)

entry_rev_from = ttk.Entry(frame_dates, width=10)
entry_rev_from.pack(side=LEFT, padx=1, pady=1)
entry_rev_from['state'] = 'disabled'

label_to2 = ttk.Label(frame_dates, text="-")
label_to2.pack(side=LEFT, padx=1, pady=3)

entry_rev_to = ttk.Entry(frame_dates, width=10)
entry_rev_to.pack(side=LEFT, padx=1, pady=1)
entry_rev_to['state'] = 'disabled'

# LOG AREA

label_log = ttk.Label(text="Log:")
label_log.pack(anchor='nw', padx=6, pady=6)

revs_var = StringVar(value=log_to_show)
listbox = Listbox(listvariable=revs_var)
get_log(path,team,0)
scrollbar_horizontal = ttk.Scrollbar(listbox, orient="horizontal")
scrollbar_vertical = ttk.Scrollbar(listbox, orient="vertical")
listbox.pack(expand=1, fill=BOTH)
listbox['yscrollcommand'] = scrollbar_vertical.set
listbox['xscrollcommand'] = scrollbar_horizontal.set
listbox.bind('<<ListboxSelect>>', onselect)
listbox.bind("<Button-3>", listbox_right_click)
listbox.bind('<Enter>', listbox_hovering_enter)
listbox.bind('<Leave>', listbox_hovering_leave)
listbox.bind('<Motion>', listbox_motion)



scrollbar_horizontal.config(command=listbox.xview)
scrollbar_vertical.config(command=listbox.yview)
scrollbar_horizontal.pack(side="bottom", fill="x")
scrollbar_vertical.pack(side="right", fill="y")


# BUTTON AREA

progressbar = ttk.Progressbar(window, length=2000, orient="horizontal", mode="indeterminate")
progressbar.pack(side=BOTTOM, padx=6, pady=6)

update_btn = ttk.Button(text="Update", command=click_update_btn, width=7)
update_btn.pack(side=LEFT, padx=6, pady=6)

refresh_btn = ttk.Button(text="Refresh", command=click_refresh_btn, width=7)
refresh_btn.pack(side=LEFT, padx=6, pady=6)

next_100_btn = ttk.Button(text="Next 100", command=click_next_100_btn, width=8)
next_100_btn.pack(side=LEFT, padx=6, pady=6)

show_all_btn = ttk.Button(text="Show all", command=click_show_all_btn, width=8)
show_all_btn.pack(side=LEFT, padx=6, pady=6)

cleanup_btn = ttk.Button(text="Clean up", command=click_cleanup_btn, width=8)
cleanup_btn.pack(side=LEFT, padx=6, pady=6)

monitor_btn = ttk.Button(text="Start monitoring", command=click_monitor_btn)
monitor_btn.pack(side=LEFT, padx=6, pady=6)

label_empty2 = ttk.Label(text="  ")
label_empty2.pack(side=LEFT, padx=6, pady=6)

rev_enabled = IntVar(value=0)
rev_checkbox = ttk.Checkbutton(text="Revision:", variable=rev_enabled, command=gray_entry_revision)
rev_checkbox.pack(side=LEFT, padx=1, pady=6)

entry_revision = ttk.Entry(width=10)
entry_revision.pack(side=LEFT, padx=1, pady=1)
entry_revision['state'] = 'disabled'

reset_btn = ttk.Button(text="↑↓", command=click_reset_btn, width=3)
reset_btn.pack(side=RIGHT, padx=6, pady=6)

# HOTKEYS
window.bind("<F5>", press_f5)
window.bind("<Control-Return>", press_ctrl_enter)


# CONTEXT MENU
def entry_context_menu(event):

    def cut_text():
        event.widget.event_generate("<<Cut>>")

    def copy_text():
        event.widget.event_generate("<<Copy>>")

    def paste_text():
        event.widget.event_generate("<<Paste>>")

    entries_context_menu = Menu(window, tearoff=0)
    entries_context_menu.add_command(label="Cut", command=cut_text)
    entries_context_menu.add_command(label="Copy", command=copy_text)
    entries_context_menu.add_command(label="Paste", command=paste_text)

    def do_popup(event):
        try:
            entries_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            entries_context_menu.grab_release()

    do_popup(event)


combobox_team.bind("<Button-3>", entry_context_menu)
combobox_path.bind("<Button-3>", entry_context_menu)
combobox_path['state'] = 'normal'


###################################################################################################

window.mainloop()


# Быстро получить список измененных файлов (чтобы сделать нормальный прогрессбар):
# changes_count = (len(os.popen('svn log -r ' + current_rev + ':' + rev + ' -v').read().split('\n')) - 10)/2
# или так: svn diff --summarize -r 70899:70911 | find /c "       " 