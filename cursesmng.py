#!/usr/bin/env python2

"""
The MIT License (MIT)
Copyright (c) 2015 Santiago Caamanho

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
from os import system
import curses
import curses.textpad
import commands
import subprocess
import logging

__author__ = 'Santiago Caamanho'

"""
*************************************************************************************************
******************************    CONFIGURACION PROCESOS    *************************************
*************************************************************************************************
"""
# PROCESOS ID
PROCESS_AXIS_ID = "axis2-1.6.2"
PROCESS_RVD_ID = "rvd64"
PROCESS_RABBIT_ID = "rabbitmq-server"
PROCESS_MONGODB_ID = "mongod"
PROCESS_CACHE_ID = "AppCache.jar"
PROCESS_CORE_ID = "AppCoreSA.jar"
PROCESS_JBOSS_ID = "org.jboss.byteman"
PROCESS_NODE_ID = "server.js"

# PATHS CONFIGURABLES
# TMP_PATH = "/tmp/"
TMP_PATH = ""
SRV_PATH = "/sbin/"
AXIS_PATH = "/opt/axis2-1.6.2/bin/"
MONGO_PATH = "/opt/mongodb/bin/"
CACHE_PATH = "/opt/cache-srv/"
CORE_PATH = "/opt/appcore/bin/"
JBOSS_PATH = "/opt/jboss-eap-6.2/bin/"
NODE_PATH = "/opt/nodeservers/updatesrv/"
LOG_PATH = "/home/inplan/logs/"
MONGO_SCRIPTS = "/usr/local/bin/"

CACHE_DEPLOY_PATH = CACHE_PATH
CORE_DEPLOY_PATH = CORE_PATH
JBOSS_DEPLOY_PATH = "/opt/jboss-eap-6.2/standalone/deployments/"

# PROCESOS COMMANDOS
PROCESS_AXIS_CMD = "./start & "
PROCESS_RVD_CMD = "rvd64 > /dev/null &"
PROCESS_RABBIT_CMD_START = SRV_PATH + "service rabbitmq-server start"
PROCESS_RABBIT_CMD_STOP = SRV_PATH + "service rabbitmq-server stop"
PROCESS_RABBIT_CMD_STATUS = SRV_PATH + "service rabbitmq-server status"
# PROCESS_MONGODB_CMD_START = "numactl --interleave=all mongod --dbpath /home/inplan/mongodata  " \
#                            "> /home/inplan/logs/mongo.log  2>&1 &"
PROCESS_MONGODB_CMD_START = "mongod --dbpath /home/app/mongodata > /home/app/logs/mongo.log  2>&1 &"
PROCESS_MONGODB_CMD_STOP = "mongod --shutdown --dbpath /home/app/mongodata &"
PROCESS_CACHE_CMD = "./start &"
PROCESS_CORE_CMD = "./run &"
PROCESS_CLEAR_DUMMY_CMD = "rm -f /opt/dummies/ftp/*.pmi"
PROCESS_JBOSS_CLEAR_CMD = "./clean"
PROCESS_JBOSS_START_CMD = "./start &"
PROCESS_NODE_CMD = "./start &"

# OPERACIONES MONGO
MONGO_DROP_INPLAN_CMD = "mongo app --eval 'db.dropDatabase()'"
MONGO_DROP_HISTORIC_CMD = "mongo historic --eval 'db.dropDatabase()'"
MONGO_EXPORT_CMD = "mongodump --host 127.0.0.1 --port 27017 --out "
MONGO_RESTORE_CMD = "mongorestore --host 127.0.0.1 --port 27017  "

# FICHEROS DE LOG
PROCESS_CORE_LOG = "inplancore.log"
PROCESS_ATV_LOG = "app.log"
PROCESS_INDEX_LOG = "app_indicator.log"
PROCESS_ALERT_LOG = "app_alert.log"
PROCESS_PRES_LOG = "app_presentation.log"
PROCESS_JMX_LOG = ""  # todo
PROCESS_JBOSS_LOG = "server.log"
PROCESS_MONGO_LOG = "mongo.log"
PROCESS_CACHE_LOG = "app_cache.log"
PROCESS_NODE_LOG = "node_updateserver.log"
PROCESS_AXIS_LOG = "axis2.log"
PROCESS_AINS_LOG = "app_ains.log"
PROCESS_ANSP_LOG = "app_ansp.log"
PROCESS_APT_LOG = "app_apt.log"
PROCESS_RABBIT_LOG = "/var/log/rabbitmq/rabbit@ugnome.log"  # todo

"""
*************************************************************************************************
**********************************      APLICACION      *****************************************
*************************************************************************************************
"""
# CODIGO TECLA ESC
ESC_KEY = 27
ESC_MSG = "Esc - Back Main Screen"

# ESTADOS PROCESOS
STARTED = "STARTED"
STOPED = "STOPED "

# PANTALLAS
MAIN_SCREEN = 0
START_SCREEN = 1
STOP_SCREEN = 2
STATUS_SCREEN = 3
DDBB_SCREEN = 4
LOG_SCREEN = 5

# OPCIONES MENU PANTALLA PRINCIPAL
MAIN_OPT_QUIT = "q"


class SystemCmd():
    def __init__(self):
        pass

    def check_process_status(self, process_id):
        status = STOPED
        output = self.ps_command(process_id)
        if output and output.find(process_id):
            status = STARTED
        return status

    def inplan_ps_report(self):
        curses.endwin()
        system("clear")
        print ("")
        print (self.ps_command(PROCESS_AXIS_ID))
        print (self.ps_command(PROCESS_RVD_ID))
        print (self.ps_command(PROCESS_RABBIT_ID))
        print (self.ps_command(PROCESS_MONGODB_ID))
        print (self.ps_command(PROCESS_CACHE_ID))
        print (self.ps_command(PROCESS_CORE_ID))
        print (self.ps_command(PROCESS_JBOSS_ID))
        print (self.ps_command(PROCESS_NODE_ID))
        print ("")
        raw_input("Press enter")
        print ("")
        return

    def test_file(self, fileName):
        val = False
        output = commands.getoutput('[ -f ' + fileName + ' ] && echo "True" || echo "False"')
        if output == "True":
            val = True
        return val

    def ps_command(self, process_id):
        output = commands.getoutput("ps -ef | grep " + process_id + " | grep -v grep")
        return output

    def tail_cmd(self, log_file):
        try:
            self.execute_cmd(TMP_PATH, "tail -f -n 50 " + LOG_PATH + log_file)
        except KeyboardInterrupt, e:
            logging.warning('Interrupted:'+e.message)

    def print_report(self, message):
        curses.endwin()
        system("clear")
        print(message)
        raw_input("Press enter")

    def check_and_launch(self, id_process, path, command):
        if self.check_process_status(id_process) == STARTED:
            self.print_report("process already launched")
        else:
            self.execute_cmd(path, command)
        return

    def kill_process(self, process_id, kill_signal=""):
        output = self.ps_command(process_id)
        if not output:
            self.print_report("Process:" + process_id + " not found.")
        else:
            parts = output.split()
            self.execute_cmd(TMP_PATH, "kill " + kill_signal + " " + parts[1])

    def execute_cmd(self, path, cmd_string):
        if path != TMP_PATH:
            os.chdir(path)
        else:
            os.chdir("/tmp/")
        curses.endwin()
        system("clear")
        print("Working dir:" + commands.getoutput("pwd"))
        print ("Executing:" + cmd_string)
        # a = self.execute(cmd_string)
        a = self.execute_bg(cmd_string, path)
        if a == 0:
            print ("Command executed correctly.")
        else:
            print ("Command terminated with error.")
        raw_input("Press enter")

    def execute_bg(self, cmd, path):
        # print ("Executing:" + path + cmd)
        return subprocess.call(path + cmd, shell=True)
        # return subprocess.Popen(path + cmd, shell=True)

    def execute(self, cmd):
        return system(cmd)


class WindowMaker():
    def __init__(self, x=2, y=1, row=11, col=39):
        self.win = curses.newwin(row, col, y, x)

    def create_color_win(self, title, color):
        self.win.border(0)
        self.win.attron(color)
        self.win.box(0, 0)
        self.win.addstr(0, 2, title)
        self.win.attroff(color)
        return self.win

    def addstr(self, y, x, text, style=curses.A_NORMAL):
        self.win.addstr(y, x, text, style)

    def add_status_str(self, y, x, text, status=STARTED):
        color_pair = 2
        if status == STARTED:
            color_pair = 3
        self.win.addstr(y, x, text, curses.color_pair(color_pair) + curses.A_BOLD)
        self.win.addstr(y, x + 18, "-", curses.color_pair(color_pair))
        self.win.addstr(y, x + 20, status, curses.color_pair(color_pair) + curses.A_REVERSE + curses.A_BOLD)

    def get_win(self):
        return self.win

    def refresh(self):
        self.win.refresh()


class GenericWindow():
    def __init__(self, screen, screen_display=0):
        self.screen = screen
        self.screen_display = screen_display
        self.OPT_AXIS_LOG = "a"
        self.OPT_MONGO_LOG = "b"
        self.OPT_CACHE_LOG = "c"
        self.OPT_CORE_LOG = "d"
        self.OPT_JBOSS_LOG = "e"
        self.OPT_NODE_LOG = "f"

    def input_dialog(self, prompt_string, _help="", default_option=""):
        x = 2
        y = 6
        rows = 9
        cols = 76

        win = WindowMaker(x, y, rows, cols)
        win.refresh()
        x += 2
        y += 2
        rows -= 4
        cols -= 4
        win = WindowMaker(x, y, rows, cols)
        win.create_color_win(prompt_string,curses.color_pair(0))
        win.refresh()
        x += 1
        y += 1
        rows -= 2
        cols -= 2
        win = WindowMaker(x, y, rows, cols)
        win.create_color_win(_help, curses.color_pair(4))
        win.addstr(1, 1, default_option)
        win.refresh()
        x += 1
        y += 1
        rows -= 2
        user_input = self.screen.getstr(y, x, cols)

        """
        win = curses.newwin(5, 60, 5, 10)
        tb = curses.textpad.Textbox(win)
        text = tb.edit()
        # message=tb.gather()
        """
        return user_input.strip()

    def error_dialog(self, error_msg, error_msg1="", error_msg2="", error_msg3="",):
        win = WindowMaker(19, 4, 12, 42)
        win.refresh()
        win = WindowMaker(20, 5, 10, 40)
        win.create_color_win("Error", curses.color_pair(2))
        x = 4
        y = 2
        win.addstr(y, x, error_msg)
        y += 1
        win.addstr(y, x, error_msg1)
        y += 1
        win.addstr(y, x, error_msg2)
        y += 1
        win.addstr(y, x, error_msg3)
        y += 3
        x = 8
        win.addstr(y, x, "Press Enter to return")
        win.refresh()
        self.screen.getstr(13, 50, 1)

    def tail_dialog(self, log_file):
        filter =self.input_dialog("egrep filter")
        if filter.strip() != "":
            log_file += " | egrep " + filter
        syscmd = SystemCmd()
        syscmd.tail_cmd(log_file)

    def paint_report(self, x=40, y=1):
        win = WindowMaker(x, y)
        win.create_color_win(" Status Report ", curses.color_pair(4))
        syscmd = SystemCmd()
        x = 4
        y = 2
        win.add_status_str(y, x, "Axis", syscmd.check_process_status(PROCESS_AXIS_ID))
        y += 1
        win.add_status_str(y, x, "RVD", syscmd.check_process_status(PROCESS_RVD_ID))
        y += 1
        win.add_status_str(y, x, "RabbitMQ", syscmd.check_process_status(PROCESS_RABBIT_ID))
        y += 1
        win.add_status_str(y, x, "MongoDB", syscmd.check_process_status(PROCESS_MONGODB_ID))
        y += 1
        win.add_status_str(y, x, "INplan Cache", syscmd.check_process_status(PROCESS_CACHE_ID))
        y += 1
        win.add_status_str(y, x, "INplan Core", syscmd.check_process_status(PROCESS_CORE_ID))
        y += 1
        win.add_status_str(y, x, "INplan JBoss", syscmd.check_process_status(PROCESS_JBOSS_ID))
        y += 1
        win.add_status_str(y, x, "Node Server", syscmd.check_process_status(PROCESS_NODE_ID))
        win.refresh()

    def paint_log(self, rows=11, cols=78, x=1, y=12):
        win = WindowMaker(x, y, rows, cols)
        win.create_color_win(" [Quick Log] ", curses.color_pair(5))
        x = 2
        y = 1
        win.addstr(y, x, self.OPT_AXIS_LOG + " - Axis")
        y += 1
        win.addstr(y, x, self.OPT_MONGO_LOG + " - MongoDB")
        y += 1
        win.addstr(y, x, self.OPT_CACHE_LOG + " - INplan Cache")
        y += 1
        win.addstr(y, x, self.OPT_CORE_LOG + " - INplan Core")
        y += 1
        win.addstr(y, x, self.OPT_JBOSS_LOG + " - INplan JBoss")
        y += 1
        win.addstr(y, x, self.OPT_NODE_LOG + " - Node Server")
        y += 2
        if self.screen_display == MAIN_SCREEN:
            win.addstr(y, x, MAIN_OPT_QUIT + " - Exit", curses.A_BOLD)
        else:
            win.addstr(y, x, ESC_MSG, curses.A_BOLD)
        win.refresh()

    def get_menu_screen(self, x=1, y=1):
        win = WindowMaker(x, y)
        win.create_color_win(" Status Report ", curses.color_pair(4))
        return

    def getch(self):
        return self.screen.getch()

    def finish(self):
        curses.endwin()

    def manage_log_menu(self, option):
        if option == ord(self.OPT_AXIS_LOG):
            self.tail_dialog(PROCESS_AXIS_LOG)
        elif option == ord(self.OPT_MONGO_LOG):
            self.tail_dialog(PROCESS_MONGO_LOG)
        elif option == ord(self.OPT_CACHE_LOG):
            self.tail_dialog(PROCESS_CACHE_LOG)
        elif option == ord(self.OPT_CORE_LOG):
            self.tail_dialog(PROCESS_CORE_LOG)
        elif option == ord(self.OPT_JBOSS_LOG):
            self.tail_dialog(PROCESS_JBOSS_LOG)
        elif option == ord(self.OPT_NODE_LOG):
            self.tail_dialog(PROCESS_NODE_LOG)


class MongoManager(GenericWindow):
    def __init__(self, screen):
        GenericWindow.__init__(self, screen)

    def export_ddbb(self):
        syscmd = SystemCmd()
        if(syscmd.check_process_status(PROCESS_MONGODB_ID) == STOPED):
            self.error_dialog("MongoDB must be running")
            return
        export_path = self.input_dialog("Path to export dabase [Path must finish in /dump]")
        if export_path.strip() == "":
            self.error_dialog(" export path can't be empty")
            return
        if not export_path.endswith("/dump"):
            export_path += "/dump"
        curses.endwin()
        print ("Creating directory:" + export_path)
        a = system("mkdir -p " + export_path)
        if a != 0:
            print ("Error creating directory:" + export_path)
            raw_input("Press enter")
            return
        syscmd.execute_cmd(TMP_PATH, MONGO_EXPORT_CMD + export_path)
        return

    def import_ddbb(self):
        syscmd = SystemCmd()
        if(syscmd.check_process_status(PROCESS_MONGODB_ID) == STOPED):
            self.error_dialog("MongoDB must be running")
            return
        import_path = self.input_dialog("Import path [Path where dump directory is]")
        if import_path.strip() == "":
            self.error_dialog("import path can't be empty")
            return
        """
        if not import_path.endswith("/"):
            import_path += "/"
        if not syscmd.test_file(import_path + "dump"):
            self.paint_error("dump directory not found", "in path:", import_path)
            return
        """
        syscmd.execute_cmd(TMP_PATH, MONGO_RESTORE_CMD + import_path)
        return

    def ddbb_stats(self):
        syscmd = SystemCmd()
        if(syscmd.check_process_status(PROCESS_MONGODB_ID) == STOPED):
            self.error_dialog("MongoDB must be running")
            return
        export_path = self.input_dialog("Path to generate CSV files")
        if export_path.strip() == "":
            self.error_dialog("export cvs path can't be empty")
            return
        if not export_path.endswith("/"):
            export_path += "/"
        curses.endwin()
        a = system("mkdir -p " + export_path)
        if a != 0:
            print ("Error creating directory:" + export_path)
            raw_input("Press enter")
            return
        syscmd.execute_cmd(TMP_PATH, "mongo 127.0.0.1:27017/inplan " + MONGO_SCRIPTS + "mongostats.js > " + export_path
            + "inplan.csv")
        syscmd.execute_cmd(TMP_PATH, "mongo 127.0.0.1:27017/historic " + MONGO_SCRIPTS + "mongostats.js > " + export_path
            + "historic.csv")

    def drop_ddbb(self):
        syscmd = SystemCmd()
        if(syscmd.check_process_status(PROCESS_MONGODB_ID) == STOPED):
            self.error_dialog("MongoDB must be running")
            return
        export_path = self.input_dialog("Drop inplan and historic databases. Are you sure ?", "(y/N)", "N")
        export_path = export_path.strip().lower()
        if export_path == "" or export_path.startswith("n"):
            return
        export_path = self.input_dialog("Drop inplan and historic databases. Are you really sure ?", "(y/N)", "N")
        export_path = export_path.strip().lower()
        if export_path == "" or export_path.startswith("n"):
            return
        curses.endwin()
        a = syscmd.execute(MONGO_DROP_INPLAN_CMD)
        if a == 0:
            print ("inplan database droped")
        else:
            print ("drop inplan database failed")
        a = syscmd.execute(MONGO_DROP_HISTORIC_CMD)
        if a == 0:
            print ("historic database droped")
        else:
            print ("drop historic database failed")
        raw_input("Press enter")
        print ("")
        return


class StatusManager(GenericWindow):
    def __init__(self, screen):
        GenericWindow.__init__(self, screen)

    def deploy_inplan(self):
        syscmd = SystemCmd()
        base_dir = self.input_dialog("Directory where deploy directory is", "")
        if base_dir == "" or not syscmd.test_file(base_dir):
            self.error_dialog("path can't be empty")
            return
        syscmd.execute_cmd(base_dir, "cp -rf deploy/core/* " + CORE_DEPLOY_PATH)
        syscmd.execute_cmd(base_dir, "cp -rf deploy/cache/* " + CACHE_DEPLOY_PATH)
        syscmd.execute_cmd(base_dir, "cp -rf deploy/jboss/* " + JBOSS_DEPLOY_PATH)
        return

    def stop_all(self):
        syscmd = SystemCmd()
        option = self.input_dialog("Force stop all?", "(Y/n)", "Y")
        # cualquier cosa que no sea n o N es Y
        option = option.upper()
        if option == "N":
            ps_signal = ""
        else:
            ps_signal = "-9"
        # FORZAMOS KILL <ps_signal> TODOS PROCESOS
        syscmd.kill_process(PROCESS_AXIS_ID, ps_signal)
        syscmd.kill_process(PROCESS_RVD_ID, ps_signal)
        # syscmd.execute_cmd(TMP_PATH, PROCESS_RABBIT_CMD_STOP)
        syscmd.kill_process(PROCESS_CACHE_ID, ps_signal)
        syscmd.kill_process(PROCESS_CORE_ID, ps_signal)
        syscmd.kill_process(PROCESS_JBOSS_ID, ps_signal)
        syscmd.kill_process(PROCESS_NODE_ID, ps_signal)
        status = syscmd.check_process_status(PROCESS_MONGODB_ID)
        if status == STARTED:
            syscmd.execute_cmd(TMP_PATH, PROCESS_MONGODB_CMD_STOP)
        return

    def start_all(self):
        syscmd = SystemCmd()
        option = self.input_dialog("Start All Inplan ? [Running Process will not be checked]", "(y/N)", "N")
        # cualquier cosa que no sea y o Y es N
        option = option.upper()
        if option  != "Y":
            return
        # EJECUTAMOS inplan -a
        curses.endwin()
        syscmd.execute_cmd(TMP_PATH, "inplan -a")
        return


class MainWindow(GenericWindow):
    def __init__(self, screen, screen_display=MAIN_SCREEN):
        self.screen_display = screen_display
        self.name = "INplan Console Manager"
        self.menu_win_name = " [Choose an option] "
        self.OPT_START = "1"
        self.OPT_STOP = "2"
        self.OPT_STATUS = "3"
        self.OPT_DDBB = "4"
        self.OPT_LOG = "5"
        GenericWindow.__init__(self, screen, screen_display)

    def paint_win(self, y=1, x=1):
        win = WindowMaker(x, y)
        win.create_color_win(self.menu_win_name, curses.color_pair(4))
        y = 2
        x = 2
        win.addstr(y, x, self.OPT_START + " - Start Processes")
        y += 1
        win.addstr(y, x, self.OPT_STOP + " - Stop Processes")
        y += 1
        win.addstr(y, x, self.OPT_STATUS + " - Status / Deploy")
        y += 1
        win.addstr(y, x, self.OPT_DDBB + " - Database Management")
        y += 1
        win.addstr(y, x, self.OPT_LOG + " - Application Logs")
        win.refresh()

    def paint(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 6, self.name)
        self.screen.refresh()
        self.paint_win()
        self.paint_report()
        self.paint_log()

    def get_display(self, option):
        if option == ord(self.OPT_START):
            self.screen_display = START_SCREEN
        elif option == ord(self.OPT_STOP):
            self.screen_display = STOP_SCREEN
        elif option == ord(self.OPT_STATUS):
            self.screen_display = STATUS_SCREEN
        elif option == ord(self.OPT_DDBB):
            self.screen_display = DDBB_SCREEN
        elif option == ord(self.OPT_LOG):
            self.screen_display = LOG_SCREEN
        else:
            self.manage_log_menu(option)
        return self.screen_display


class StartWindow(GenericWindow):
    def __init__(self, screen, screen_display=START_SCREEN):
        self.screen_display = screen_display
        self.name = "INplan Console Manager - [Start Processes]"
        self.menu_win_name = " [Select process to start] "
        self.OPT_AXIS = "1"
        self.OPT_RVD = "2"
        self.OPT_RABBIT = "3"
        self.OPT_MONGO = "4"
        self.OPT_CACHE = "5"
        self.OPT_CORE = "6"
        self.OPT_JBOSS = "7"
        self.OPT_NODE = "8"
        GenericWindow.__init__(self, screen, screen_display)

    def paint_win(self, y=1, x=1):
        win = WindowMaker(x, y)
        win.create_color_win(self.menu_win_name, curses.color_pair(4))
        x = 2
        y = 2
        win.addstr(y, x, self.OPT_AXIS + " - Axis")
        y += 1
        win.addstr(y, x, self.OPT_RVD + " - RVD")
        y += 1
        win.addstr(y, x, self.OPT_RABBIT + " - RabbitMQ")
        y += 1
        win.addstr(y, x, self.OPT_MONGO + " - MongoDB")
        y += 1
        win.addstr(y, x, self.OPT_CACHE + " - INplan Cache")
        y += 1
        win.addstr(y, x, self.OPT_CORE + " - INplan Core")
        y += 1
        win.addstr(y, x, self.OPT_JBOSS + " - INplan JBoss")
        y += 1
        win.addstr(y, x, self.OPT_NODE + " - Node Server")
        win.refresh()

    def paint(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 6, self.name)
        self.screen.refresh()
        self.paint_win()
        self.paint_report()
        self.paint_log()

    def execute(self, process_id, path, cmd):
        syscmd = SystemCmd()
        if syscmd.check_process_status(process_id) == STARTED:
            self.error_dialog("Process arready launched", "Id:" + process_id)
            return
        syscmd.execute_cmd(path, cmd)
        return

    def executejb(self, process_id, path, cmd):
        syscmd = SystemCmd()
        if syscmd.check_process_status(process_id) == STARTED:
            self.error_dialog("Process arready launched", "Id:" + process_id)
            return
        syscmd.execute_cmd(TMP_PATH, PROCESS_CLEAR_DUMMY_CMD)
        syscmd.execute_cmd(JBOSS_PATH, PROCESS_JBOSS_CLEAR_CMD)
        syscmd.execute_cmd(JBOSS_PATH, PROCESS_JBOSS_START_CMD)
        return

    def get_display(self, option):
        syscmd = SystemCmd()
        if option == ESC_KEY:
            self.screen_display = MAIN_SCREEN
        elif option == ord(self.OPT_AXIS):
            self.execute(PROCESS_AXIS_ID, AXIS_PATH, PROCESS_AXIS_CMD)
        elif option == ord(self.OPT_RVD):
            self.execute(PROCESS_RVD_ID, TMP_PATH, PROCESS_RVD_CMD)
        elif option == ord(self.OPT_RABBIT):
            syscmd.execute_cmd(TMP_PATH, PROCESS_RABBIT_CMD_START)
        elif option == ord(self.OPT_MONGO):
            self.execute(PROCESS_MONGODB_ID, MONGO_PATH, PROCESS_MONGODB_CMD_START)
        elif option == ord(self.OPT_CACHE):
            self.execute(PROCESS_CACHE_ID, CACHE_PATH, PROCESS_CACHE_CMD)
        elif option == ord(self.OPT_CORE):
            self.execute(PROCESS_CORE_ID, CORE_PATH, PROCESS_CORE_CMD)
        elif option == ord(self.OPT_JBOSS):
            self.executejb(PROCESS_JBOSS_ID, JBOSS_PATH, PROCESS_JBOSS_START_CMD)
        elif option == ord(self.OPT_NODE):
            self.execute(PROCESS_NODE_ID, NODE_PATH, PROCESS_NODE_CMD)
        else:
            self.manage_log_menu(option)
        return self.screen_display


class StopWindow(GenericWindow):
    def __init__(self, screen, screen_display=STOP_SCREEN):
        self.screen_display = screen_display
        self.name = "INplan Console Manager - [Stop Processes]"
        self.menu_win_name = " [Select process to stop] "
        self.OPT_AXIS = "1"
        self.OPT_RVD = "2"
        self.OPT_RABBIT = "3"
        self.OPT_MONGO = "4"
        self.OPT_CACHE = "5"
        self.OPT_CORE = "6"
        self.OPT_JBOSS = "7"
        self.OPT_NODE = "8"
        GenericWindow.__init__(self, screen, screen_display)

    def paint_win(self, y=1, x=1):
        win = WindowMaker(x, y)
        win.create_color_win(self.menu_win_name, curses.color_pair(4))
        x = 2
        y = 2
        win.addstr(y, x, self.OPT_AXIS + " - Axis")
        y += 1
        win.addstr(y, x, self.OPT_RVD + " - RVD")
        y += 1
        win.addstr(y, x, self.OPT_RABBIT + " - RabbitMQ")
        y += 1
        win.addstr(y, x, self.OPT_MONGO + " - MongoDB")
        y += 1
        win.addstr(y, x, self.OPT_CACHE + " - INplan Cache")
        y += 1
        win.addstr(y, x, self.OPT_CORE + " - INplan Core")
        y += 1
        win.addstr(y, x, self.OPT_JBOSS + " - INplan JBoss")
        y += 1
        win.addstr(y, x, self.OPT_NODE + " - Node Server")
        win.refresh()

    def paint(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 6, self.name)
        self.screen.refresh()
        self.paint_win()
        self.paint_report()
        self.paint_log()

    def get_display(self, option):
        syscmd = SystemCmd()
        if option == ESC_KEY:
            self.screen_display = MAIN_SCREEN
        elif option == ord(self.OPT_AXIS):
            self.kill_process(syscmd, PROCESS_AXIS_ID)
        elif option == ord(self.OPT_RVD):
            self.kill_process(syscmd, PROCESS_RVD_ID)
        elif option == ord(self.OPT_RABBIT):
            syscmd.execute_cmd(TMP_PATH, PROCESS_RABBIT_CMD_STOP)
        elif option == ord(self.OPT_MONGO):
            syscmd.execute_cmd(TMP_PATH, PROCESS_MONGODB_CMD_STOP)
        elif option == ord(self.OPT_CACHE):
            self.kill_process(syscmd, PROCESS_CACHE_ID)
        elif option == ord(self.OPT_CORE):
            self.kill_process(syscmd, PROCESS_CORE_ID)
        elif option == ord(self.OPT_JBOSS):
            self.kill_process(syscmd, PROCESS_JBOSS_ID)
        elif option == ord(self.OPT_NODE):
            self.kill_process(syscmd, PROCESS_NODE_ID)
        else:
            self.manage_log_menu(option)
        return self.screen_display

    def kill_dialog(self, process_id):
        """
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(2, 2, "Kill " + process_id + " ?")
        self.screen.addstr(9, 2, "Kill signal [0-9]")
        # enable keypad mode
        self.screen.keypad(1)
        self.screen.refresh()
        """


        x = 15
        y = 3
        rows = 13
        cols = 40

        win = WindowMaker(x, y, rows, cols)
        win.create_color_win("Kill Dialog", curses.color_pair(0))

        win.refresh()
        x += 2
        y += 2
        rows = 5
        cols -= 4
        win = WindowMaker(x, y, rows, cols)
        win.create_color_win("Kill " + process_id + " ?", curses.color_pair(0))
        win.refresh()
        x += 1
        y += 1
        rows -= 2
        cols -= 2
        win = WindowMaker(x, y, rows, cols)
        win.create_color_win("[Y/n]", curses.color_pair(4))
        win.addstr(1, 1, "Y")
        win.refresh()
        x += 1
        y += 1

        y2 = y + 3
        x2 = x - 2
        rows = 5
        cols = 36
        win = WindowMaker(x2, y2, rows, cols)
        win.create_color_win("Kill signal [0-9]", curses.color_pair(0))
        win.refresh()
        x2 += 1
        y2 += 1
        rows -= 2
        cols -= 2
        win = WindowMaker(x2, y2, rows, cols)
        win.create_color_win("[Default None]", curses.color_pair(4))
        win.addstr(1, 1, "")
        win.refresh()
        x2 += 1
        y2 += 1

        # recogemos entradas
        user_input = self.screen.getstr(y, x, cols)
        if user_input.lower() == "n":
            return "--"
        user_input = self.screen.getstr(y2, x2, cols)
        if user_input != "" and not user_input.startswith("-"):
            user_input = "-" + user_input
        return user_input.strip()

    def kill_process(self, syscmd, process_id):
        if syscmd.check_process_status(process_id) == STOPED:
            self.error_dialog("Process " + process_id + " not found")
            return
        kill_signal = self.kill_dialog(process_id)
        if kill_signal == "--":
            return
        syscmd.kill_process(process_id, kill_signal)


class StatusWindow(GenericWindow):
    def __init__(self, screen, screen_display=STATUS_SCREEN):
        self.screen_display = screen_display
        self.name = "INplan Console Manager - [Status / Deploy]"
        self.menu_win_name = " [Choose an option] "
        self.OPT_DISK = "1"
        self.OPT_PS = "2"
        self.OPT_RBIT = "3"
        self.OPT_START = "4"
        self.OPT_STOP = "5"
        self.OPT_DEPLOY = "6"
        GenericWindow.__init__(self, screen, screen_display)

    def paint_win(self, y=1, x=1):
        win = WindowMaker(x, y)
        win.create_color_win(self.menu_win_name, curses.color_pair(4))
        x = 2
        y = 2
        win.addstr(y, x, self.OPT_DISK + " - Disk Status")
        y += 1
        win.addstr(y, x, self.OPT_PS + " - INplan ps Report")
        y += 1
        win.addstr(y, x, self.OPT_RBIT + " - RabbitMQ Server Status")
        y += 1
        win.addstr(y, x, "---------------------------")
        y += 1
        win.addstr(y, x, self.OPT_START + " - Start All")
        y += 1
        win.addstr(y, x, self.OPT_STOP + " - Stop All")
        y += 1
        win.addstr(y, x, self.OPT_DEPLOY + " - Deploy INplan")
        win.refresh()

    def paint(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 6, self.name)
        self.screen.refresh()
        self.paint_win()
        self.paint_report()
        self.paint_log()

    def get_display(self, option):
        syscmd = SystemCmd()
        if option == ESC_KEY:
            self.screen_display = MAIN_SCREEN
        elif option == ord(self.OPT_DISK):
            syscmd.execute_cmd(TMP_PATH, "df -h")
        elif option == ord(self.OPT_PS):
            syscmd.inplan_ps_report()
        elif option == ord(self.OPT_RBIT):
            syscmd.execute_cmd(TMP_PATH, PROCESS_RABBIT_CMD_STATUS)
        elif option == ord(self.OPT_START):
            StatusManager(self.screen).start_all()
        elif option == ord(self.OPT_STOP):
            StatusManager(self.screen).stop_all()
        elif option == ord(self.OPT_DEPLOY):
            StatusManager(self.screen).deploy_inplan()
        else:
            self.manage_log_menu(option)
        return self.screen_display


class DatabaseWindow(GenericWindow):
    def __init__(self, screen, screen_display=DDBB_SCREEN):
        self.screen_display = screen_display
        self.name = "INplan Console Manager - [Database Management]"
        self.menu_win_name = " [Choose an option] "
        self.OP_EXPORT = "1"
        self.OP_INPORT = "2"
        self.OP_CLEAR = "3"
        self.OP_STATS = "4"
        GenericWindow.__init__(self, screen, screen_display)

    def paint_win(self, y=1, x=1):
        syscmd = SystemCmd()
        win = WindowMaker(x, y)
        win.create_color_win(self.menu_win_name, curses.color_pair(4))
        status = syscmd.check_process_status(PROCESS_MONGODB_ID)
        x = 2
        y = 2
        color_pair = 2
        if status == STARTED:
            color_pair = 3
        win.addstr(y, x, "Mongo Database Must be Running", curses.color_pair(color_pair))
        y += 2
        win.addstr(y, x, self.OP_EXPORT + " - Export Databases")
        y += 1
        win.addstr(y, x, self.OP_INPORT + " - Import Databases")
        y += 1
        win.addstr(y, x, self.OP_CLEAR + " - Drop databases")
        y += 1
        win.addstr(y, x, self.OP_STATS + " - Generate Stats CSV Files")
        win.refresh()

    def paint(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 6, self.name)
        self.screen.refresh()
        self.paint_win()
        self.paint_report()
        self.paint_log()

    def get_display(self, option):
        mongo = MongoManager(self.screen)
        if option == ESC_KEY:
            self.screen_display = MAIN_SCREEN
        elif option == ord(self.OP_EXPORT):
            mongo.export_ddbb()
        elif option == ord(self.OP_INPORT):
            mongo.import_ddbb()
        elif option == ord(self.OP_CLEAR):
            mongo.drop_ddbb()
        elif option == ord(self.OP_STATS):
            mongo.ddbb_stats()
        else:
            self.manage_log_menu(option)
        return self.screen_display


class LogWindow(GenericWindow):
    def __init__(self, screen, screen_display=LOG_SCREEN):
        self.screen_display = screen_display
        self.name = "INplan Console Manager - [Applications Logs]"
        self.menu_win_name = " [Choose an option] "
        self.OP_CORE = "1"
        self.OP_ATV = "2"
        self.OP_INDEX = "3"
        self.OP_ALERT = "4"
        self.OP_PRES = "5"
        self.OP_JMX = "6"
        self.OP_JBOSS = "7"
        self.OP_MONGO = "8"
        self.OP_CACHE = "9"
        self.OP_NODE = "a"
        self.OP_AXIS = "b"
        self.OP_AINS = "c"
        self.OP_ANSP = "d"
        self.OP_APT = "e"
        self.OP_RABBIT = "f"
        GenericWindow.__init__(self, screen, screen_display)

    def paint_win(self, y=1, x=1, rows=22, cols=39):
        win = WindowMaker(x, y, rows, cols)
        win.create_color_win(self.menu_win_name, curses.color_pair(4))
        x = 2
        y = 1
        win.addstr(y, x, self.OP_CORE + " - Core")
        y += 1
        win.addstr(y, x, self.OP_ATV + " - Core Atvs")
        y += 1
        win.addstr(y, x, self.OP_INDEX + " - Core Indicators")
        y += 1
        win.addstr(y, x, self.OP_ALERT + " - Core Alerts")
        y += 1
        win.addstr(y, x, self.OP_PRES + " - Core Presentation")
        y += 1
        win.addstr(y, x, self.OP_JMX + " - Core JMX [Disabled]")
        y += 1
        win.addstr(y, x, self.OP_JBOSS + " - JBoss Server")
        y += 1
        win.addstr(y, x, self.OP_MONGO + " - MongoDB")
        y += 1
        win.addstr(y, x, self.OP_CACHE + " - Cache")
        y += 1
        win.addstr(y, x, self.OP_NODE + " - Node")
        y += 1
        win.addstr(y, x, self.OP_AXIS + " - Axis")
        y += 1
        win.addstr(y, x, self.OP_AINS + " - AINS")
        y += 1
        win.addstr(y, x, self.OP_ANSP + " - ANSP")
        y += 1
        win.addstr(y, x, self.OP_APT + " - APT")
        y += 1
        win.addstr(y, x, self.OP_RABBIT + " - RabbitMq [Disabled]")
        y += 2
        win.addstr(y, x, ESC_MSG, curses.A_BOLD)
        win.refresh()

    def paint(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.addstr(0, 6, self.name)
        self.screen.refresh()
        self.paint_report()
        self.paint_win()

    def get_display(self, option):
        if option == ESC_KEY:
            self.screen_display = MAIN_SCREEN
        elif option == ord(self.OP_CORE):
            self.tail_dialog(PROCESS_CORE_LOG)
        elif option == ord(self.OP_ATV):
            self.tail_dialog(PROCESS_ATV_LOG)
        elif option == ord(self.OP_INDEX):
            self.tail_dialog(PROCESS_INDEX_LOG)
        elif option == ord(self.OP_ALERT):
            self.tail_dialog(PROCESS_ALERT_LOG)
        elif option == ord(self.OP_PRES):
            self.tail_dialog(PROCESS_PRES_LOG)
        elif option == ord(self.OP_JMX):
            pass
        elif option == ord(self.OP_JBOSS):
            self.tail_dialog(PROCESS_JBOSS_LOG)
        elif option == ord(self.OP_MONGO):
            self.tail_dialog(PROCESS_MONGO_LOG)
        elif option == ord(self.OP_CACHE):
            self.tail_dialog(PROCESS_CACHE_LOG)
        elif option == ord(self.OP_NODE):
            self.tail_dialog(PROCESS_NODE_LOG)
        elif option == ord(self.OP_AXIS):
            self.tail_dialog(PROCESS_AXIS_LOG)
        elif option == ord(self.OP_AINS):
            self.tail_dialog(PROCESS_AINS_LOG)
        elif option == ord(self.OP_ANSP):
            self.tail_dialog(PROCESS_ANSP_LOG)
        elif option == ord(self.OP_APT):
            self.tail_dialog(PROCESS_APT_LOG)
        elif option == ord(self.OP_RABBIT):
            pass
        return self.screen_display


def main(screen):
    screen_display = MAIN_SCREEN
    option = "1"
    """ Inits the curses appliation """
    # initscr() returns a window object representing the entire screen.
    # screen = curses.initscr()
    # turn off automatic echoing of keys to the screen
    # curses.noecho()
    # turn on automatic echoing of keys to the screen
    curses.echo()
    # Enable non-blocking mode. Keys are read directly, without hitting enter.
    curses.cbreak()
    # Disable the mouse cursor.
    # curses.curs_set(0)
    # screen.keypad(1)
    # Enable colorous output.
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    while True:
        # Checheamos condicion de salida
        if option == ord(MAIN_OPT_QUIT) and screen_display == MAIN_SCREEN:
            break
        try:
            if screen_display == MAIN_SCREEN:
                current_win = MainWindow(screen)
            elif screen_display == START_SCREEN:
                current_win = StartWindow(screen)
            elif screen_display == STOP_SCREEN:
                current_win = StopWindow(screen)
            elif screen_display == STATUS_SCREEN:
                current_win = StatusWindow(screen)
            elif screen_display == DDBB_SCREEN:
                current_win = DatabaseWindow(screen)
            elif screen_display == LOG_SCREEN:
                current_win = LogWindow(screen)
            current_win.paint()
            option = current_win.getch()
            # current_win.finish()
            screen_display = current_win.get_display(option)

        except Exception, e:
            # current_win.finish()
            os.system("clear")
            print("Error: %s" % e)
            raw_input("Press enter")
            print ("")
            pass
        else:
            pass
    curses.endwin()

if __name__ == '__main__':
    curses.wrapper(main)
