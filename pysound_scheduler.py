#!/usr/bin/env python
import tkinter as tk
from tkinter import messagebox, ttk
import os, subprocess, time
from crontab import CronTab
from libs.crontask import Task
from libs.db_handler import Dbhandler
from libs.logger import logger

dbh = None

logger = logger('main.window')

largefont = "Helvetica 32"
mediumfont = "Helvetica 22"
smallfont = "Helvetica 16"

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
days_it = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]

fullscreen = os.getenv('PYSS_FULLSCREEN', 'True')

class mainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("320x480")
        self.title("Sound Scheduler")

        # disable title/widget bar
        self.wm_attributes('-fullscreen', fullscreen)

        # init container box
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}

        for f in (mainFrame, iPlayer, ScheduleList, ScheduleEdit):
            frame = f(container, self)
            self.frames[f] = frame

            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame(mainFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_frame(self, f):
        return self.frames[f]

# defining main frame with date/time
class mainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight = 2)
        self.grid_rowconfigure(1, weight = 2)
        self.grid_rowconfigure(2, weight = 1)
        self.grid_rowconfigure(3, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)

        self.date_label = tk.Label(self, text = "Data", font=largefont)
        self.date_label.grid(row=0, column=0, columnspan=2)
        self.date_tick()

        self.clock_label = tk.Label(self, text = "Ora", font = largefont)
        self.clock_label.grid(row=1, column=0, columnspan=2)
        self.clock_tick()

        scheduler_button = tk.Button(self, text="Programma", font=mediumfont, command=lambda:controller.show_frame(ScheduleList))
        scheduler_button.grid(row=2, column=0, sticky="nsew")

        player_button = tk.Button(self, text="Riproduci", font=mediumfont, command=lambda:controller.show_frame(iPlayer))
        player_button.grid(row=2, column=1, sticky="nsew")

        reboot_button = tk.Button(self, text="Riavvia", font=mediumfont, command=self.reboot)
        reboot_button.grid(row=3, column=0, sticky="nsew")

        poweroff_button = tk.Button(self, text="Spegni", font=mediumfont, command=self.poweroff)
        poweroff_button.grid(row=3, column=1, sticky="nsew")

    def date_tick(self):
        date_string = time.strftime("%d / %m / %Y")
        self.date_label.config(text=date_string)
        self.date_label.after(5000, self.date_tick)

    def clock_tick(self):
        time_string = time.strftime("%H:%M:%S")
        self.clock_label.config(text=time_string)
        self.clock_label.after(200, self.clock_tick)

    def reboot(self):
        if messagebox.askokcancel(title="Riavvio", message="Vuoi davvero riavviare?"):
            subprocess.Popen(
                ["reboot"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

    def poweroff(self):
        if messagebox.askokcancel(title="Spegnimento", message="Vuoi davvero spegnere?"):
            subprocess.Popen(
                ["poweroff"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )

# defining manual player frame
class iPlayer(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 2)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)

        self.player = None
        self.sfile_index = None
        
        self.file_list = tk.Listbox(self, font=mediumfont)
        self.file_list.grid(row=0, column=0, columnspan=3, sticky="nsew")
        
        self.scrollbary = tk.Scrollbar(self, width=32)
        self.scrollbary.grid(row=0, column=1, columnspan=3, sticky="nse")

        self.file_list.config(yscrollcommand=self.scrollbary.set)
        self.scrollbary.config(command=self.file_list.yview)

        self.list_sounds()
        
        play_button = tk.Button(self, text="Play", command=self.play_sound, font=mediumfont)
        play_button.grid(row=1, column=0, sticky="nsew")

        stop_button = tk.Button(self, text="Stop", command=self.stop_sound, font=mediumfont)
        stop_button.grid(row=1, column=1, sticky="nsew")

        exit_button = tk.Button(self, text="Esci", command=self.exit_player, font=mediumfont)
        exit_button.grid(row=1, column=2, sticky="nsew")

    def list_sounds(self):
        self.file_list.delete(0, 'end')
        files = sorted(os.listdir(os.path.relpath('sounds')))
        for f in files:
            if not f.startswith('.'):
                self.file_list.insert('end', f)

        if self.sfile_index:
            self.file_list.select_clear(0, "end")
            self.file_list.selection_set(self.sfile_index)
            self.file_list.see(self.sfile_index)
            self.file_list.activate(self.sfile_index)
            self.file_list.selection_anchor(self.sfile_index)
        logger.msg(level='debug', text='Sounds list reloaded')

    def play_sound(self):
        exe_app = "mpg123"
        if (os.name == "nt"):
            exe_app = 'tools\\' + exe_app + '.exe'
        elif (os.name == "macos"):
            exe_app = 'tools/' + exe_app

        self.sfile_index = self.file_list.curselection()
        sfile = self.file_list.get(self.sfile_index)
        sound = os.path.abspath(os.path.join('sounds', sfile))
        
        if self.player != None:
            self.stop_sound()
        
        self.player = subprocess.Popen([exe_app, sound])
        logger.msg(level='info', text="Playing file: {}".format(sfile))
        logger.msg(level='debug', text="Absolute file path: {}".format(sound))

    def stop_sound(self):
        if self.player != None:
            self.player.terminate()
            self.player = None

        shell_out = subprocess.Popen(
            ["killall", "-9", "mpg123"],
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
        stdout,stderr = shell_out.communicate()
        if(stderr):
            print(stderr)
        logger.msg(level='info', text='Player terminated')

    def exit_player(self):
        self.list_sounds()
        self.controller.show_frame(mainFrame)

class ScheduleList(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_rowconfigure(2, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)

        self.tasks_list = tk.Listbox(self, font=mediumfont)
        self.tasks_list.grid(row=0, column=0, columnspan=3, sticky="nsew")
        
        self.scrollbary = tk.Scrollbar(self, width=32)
        self.scrollbary.grid(row=0, column=1, columnspan=3, sticky="nse")

        self.tasks_list.config(yscrollcommand=self.scrollbary.set)
        self.scrollbary.config(command=self.tasks_list.yview)

        self.list_tasks()

        add_button = tk.Button(self, text="Nuova", command=self.add_schedule, font=mediumfont)
        add_button.grid(row=1, column=0, sticky="nsew")

        edit_button = tk.Button(self, text="Modifica", command=self.edit_schedule, font=mediumfont)
        edit_button.grid(row=1, column=1, sticky="nsew")

        del_button = tk.Button(self, text="Elimina", command=self.delete_schedule, font=mediumfont)
        del_button.grid(row=2, column=0, sticky="nsew")

        exit_button = tk.Button(self, text="Esci", command=self.exit_schedule, font=mediumfont)
        exit_button.grid(row=2, column=1, sticky="nsew")

    def list_tasks(self):
        dbh.list_tasks()

        self.tasks_list.delete(0, 'end')
        for t in dbh.tasks_list:
            self.tasks_list.insert('end', t.getName())

    def reload_tasks(self):
        dbh.tasks_list.clear()
        self.list_tasks()
        logger.msg(level='debug', text='Tasks list reloaded')

    def reload_crontab(self):
        cron = CronTab(user=True)
        cron.remove_all()
        cron.write()
        for t in dbh.tasks_list:
            xdg_runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
            job = cron.new(
                command="XDG_RUNTIME_DIR={} {} >/dev/null 2>&1".format(
                    xdg_runtime_dir,
                    t.getCommand()
            ))
            job.setall("{} {} {} {} {}".format(
                t.getMinute(),
                t.getHour(),
                t.getDom(),
                t.getMon(),
                t.getDow()
            ))
            cron.write()

    def add_schedule(self):
        self.controller.show_frame(ScheduleEdit)
        schedule_edit = self.controller.get_frame(ScheduleEdit)
        schedule_edit.load_task()

    def edit_schedule(self):
        lid = self.tasks_list.curselection()
        
        if lid:
            t = dbh.tasks_list[lid[0]]
            logger.msg(level='info', text='Editing task')
            logger.msg(level='debug', text="Task to edit: {}".format(t))
            self.controller.show_frame(ScheduleEdit)
            schedule_edit = self.controller.get_frame(ScheduleEdit)
            schedule_edit.load_task(t)
        else:
            messagebox.showinfo(message="Selezionare un programma")

    def delete_schedule(self):
        lid = self.tasks_list.curselection()
        logger.msg(level='debug', text='User want to delete a task')
        if lid:
            t = dbh.tasks_list[lid[0]]
            logger.msg(level='debug', text="Select task: {}, id: {}".format(t.getName(),t.getTid()))
            if messagebox.askokcancel(message="Vuoi cancellare {}?".format(t.getName()), default=messagebox.CANCEL):
                dbh.delete_task(t.getTid())
                self.reload_tasks()
                self.reload_crontab()
                logger.msg(level='info', text="Deleted task: {}".format(t.getName()))
        else:
            messagebox.showinfo(message="Selezionare un programma")

    def exit_schedule(self):
        self.reload_tasks()
        self.controller.show_frame(mainFrame)

class ScheduleEdit(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight = 2)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_rowconfigure(2, weight = 1)
        self.grid_rowconfigure(3, weight = 2)
        self.grid_rowconfigure(4, weight = 1)
        self.grid_rowconfigure(5, weight = 0)
        self.grid_rowconfigure(6, weight = 3)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)
        self.grid_columnconfigure(3, weight = 1)

        self.task = None
        self.sfile = None

        self.dow_label = tk.Label(self, font=mediumfont, text="Giorni della settimana")
        self.dow_label.grid(row=0, column=0, columnspan=4, sticky="nsew")

        self.day_cb = []
        for d in range(0,7):
            self.day_cb.append(tk.StringVar(value="0"))

        self.day_0 = tk.Checkbutton(self, text=days_it[0], font=smallfont, variable=self.day_cb[0])
        self.day_0.grid(row=1, column=0, sticky="nsew")
        self.day_1 = tk.Checkbutton(self, text=days_it[1], font=smallfont, variable=self.day_cb[1])
        self.day_1.grid(row=1, column=1, sticky="nsew")
        self.day_2 = tk.Checkbutton(self, text=days_it[2], font=smallfont, variable=self.day_cb[2])
        self.day_2.grid(row=1, column=2, sticky="nsew")
        self.day_3 = tk.Checkbutton(self, text=days_it[3], font=smallfont, variable=self.day_cb[3])
        self.day_3.grid(row=1, column=3, sticky="nsew")
        self.day_4 = tk.Checkbutton(self, text=days_it[4], font=smallfont, variable=self.day_cb[4])
        self.day_4.grid(row=2, column=0, sticky="nsew")
        self.day_5 = tk.Checkbutton(self, text=days_it[5], font=smallfont, variable=self.day_cb[5])
        self.day_5.grid(row=2, column=1, sticky="nsew")
        self.day_6 = tk.Checkbutton(self, text=days_it[6], font=smallfont, variable=self.day_cb[6])
        self.day_6.grid(row=2, column=2, sticky="nsew")

        # Time frame definition
        self.hour_label = tk.Label(self, font=mediumfont, text="Ora", padx=3, pady=3)
        self.hour_label.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.selected_hour = tk.StringVar()
        self.hour_cb = ttk.Combobox(self, textvariable=self.selected_hour, font=smallfont)
        self.hour_cb['values'] = [h for h in range(0, 24)]
        self.hour_cb['state'] = 'readonly'
        self.hour_cb.grid(row=4, column=0, columnspan=2, sticky="new")

        self.minute_label = tk.Label(self, font=mediumfont, text="Minuti", padx=3, pady=3)
        self.minute_label.grid(row=3, column=2, columnspan=2, sticky="ew")
        self.selected_minute = tk.StringVar()
        self.minute_cb = ttk.Combobox(self, textvariable=self.selected_minute, font=smallfont)
        self.minute_cb['values'] = [h for h in range(0, 60, 5)]
        self.minute_cb['state'] = 'readonly'
        self.minute_cb.grid(row=4, column=2, columnspan=2, sticky="new")

        self.file_list = tk.Listbox(self, font=mediumfont, height=5)
        self.file_list.grid(row=5, column=0, columnspan=4)
        
        self.scrollbary = tk.Scrollbar(self, width=32)
        self.scrollbary.grid(row=5, column=3, sticky="nse")

        self.file_list.config(yscrollcommand=self.scrollbary.set)
        self.scrollbary.config(command=self.file_list.yview)

        abort_button = tk.Button(self, text="Annulla", command=self.abort, font=mediumfont)
        abort_button.grid(row=6, column=0, columnspan=2, sticky="nsew")

        confirm_button = tk.Button(self, text="Conferma", command=self.confirm, font=mediumfont)
        confirm_button.grid(row=6, column=2, columnspan=2, sticky="nsew")

        def cbls(event):
            self.list_sounds()
            
        self.hour_cb.bind('<<ComboboxSelected>>', cbls)
        self.minute_cb.bind('<<ComboboxSelected>>', cbls)

    def list_sounds(self):
        self.file_list.delete(0, 'end')
        files = sorted(os.listdir(os.path.relpath('sounds')))

        for f in files:
            if not f.startswith('.'):
                self.file_list.insert('end', f)

        if self.sfile:
            sfile_index = self.file_list.get(0, 'end').index(self.sfile)
            self.file_list.selection_set(sfile_index)
            self.file_list.see(sfile_index)
            self.file_list.activate(sfile_index)
            self.file_list.selection_anchor(sfile_index)
        logger.msg(level='debug', text='Schedule sounds list reloaded')
    
    def abort(self):
        self.reset()
        self.controller.show_frame(ScheduleList)

    def reset(self):
        self.task = None
        self.sfile = None
        self.hour_cb.current(newindex=0)
        self.minute_cb.current(newindex=0)

        for d in range(0,7):
            self.day_cb[d].set("0")

        self.file_list.select_clear(0, "end")

    def confirm(self):
        rowid = None
        dow = ""
        name = ""
        hour = self.selected_hour.get()
        minute = self.selected_minute.get()
        for d in range(0, 7):
            if self.day_cb[d].get() == "1":
                if dow != "":
                    dow += ","
                if name != "":
                    name += "-"
                dow += str(d+1)
                name += days_it[d]

        if dow == "" or name == "":
            messagebox.showwarning(message="Selezionare almeno un giorno della settimana")
            logger.msg(level='debug', text='no DoW selected')
            return None

        if not self.file_list.curselection():
            messagebox.showwarning(message="Selezionare il brano da riprodurre")
            logger.msg(level='debug', text='no sound selected')
            return None

        name = "{:02d}:{:02d} {}".format(int(hour), int(minute), name)
        sound = os.path.abspath(os.path.join(
            'sounds',
            self.file_list.get(self.file_list.curselection())
        ))
        command = 'mpg123 "{}"'.format(sound)

        if not self.task:
            self.sfile = self.file_list.get(self.file_list.curselection())
            task=(name, minute, hour, "*", "*", dow, command)
            dbh.search_task(task)
            if not dbh.curr_task:
                rowid = dbh.insert_task(task)
            else:
                logger.msg(level='warning', text='There is another schedulation at same time!')
                messagebox.showwarning(title="Attenzione", message="Esiste un'altra schedulazione alla stessa ora")
        else:
            self.task.setName(name)
            self.task.setHour(hour)
            self.task.setMinute(minute)
            self.task.setDow(dow)
            self.task.setCommand(command)
            task=(self.task.getName(), self.task.getMinute(), self.task.getHour(), self.task.getDom(), self.task.getMon(), self.task.getDow(), self.task.getCommand())
            dbh.search_task(task)
            if not dbh.curr_task or dbh.curr_task.getTid() == self.task.getTid():
                rowid = dbh.update_task(self.task)
            else:
                logger.msg(level='warning', text='There is another schedulation at same time!')
                messagebox.showwarning(title="Attenzione", message="Esiste un'altra schedulazione alla stessa ora")
        
        logger.msg(level='debug', text="rowid: {} ".format(rowid))
        
        if not rowid == None:
            self.task = None
            schedule_list = self.controller.get_frame(ScheduleList)
            schedule_list.reload_tasks()
            schedule_list.reload_crontab()
            self.controller.show_frame(ScheduleList)

    def get_sound_from_command(self, command):
        sfile = command.replace("mpg123", "").lstrip().strip('"')
        return os.path.basename(sfile)

    def load_task(self, task=None):
        self.reset()

        if task:
            self.task = task
            dow = self.task.getDow().split(",")
            for d in dow:
                self.day_cb[int(d)-1].set("1")
            self.hour_cb.current(newindex=int(self.task.getHour()))
            self.minute_cb.current(newindex=(int(int(self.task.getMinute())/5)))

            self.sfile = self.get_sound_from_command(self.task.getCommand())
        
        self.list_sounds()

def init_app():
    global dbh
    
    dbh = Dbhandler()
    app = mainApp()
    app.mainloop()

def exit_app():
    global dbh

    dbh.close()
    logger.msg(level='info', text='Exiting application')

# starting application
if __name__ == "__main__":
    init_app()
    exit_app()
