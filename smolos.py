# smolOS by Krzysztof Krystian Jankowski
# Homepage: http://smol.p1x.in/os/

import machine
import uos
import gc
import utime

class smolOS:
    def __init__(self):
        self.name="smolOS"
        self.version = "0.9-pre"
        
        # ESP8266
        #self.version += "-esp8266"
        #self.board = "Espressif ESP8266EX"
        #self.cpu_speed_range = {"slow":80,"turbo":160} # Mhz
        #self.system_led = machine.Pin(2,machine.Pin.OUT)
        
        # XIAO 2040
        self.version += "-xiao"
        self.board = "Seeed XIAO RP2040"
        self.cpu_speed_range = {"slow":40,"turbo":133} # Mhz
        self.system_led = machine.Pin(25,machine.Pin.OUT)
        
        self.prompt = "\nsmol $: "
        self.turbo = True
        self.background_prog = ""
        self.protected_files = { "boot.py","main.py" }
        self.user_commands = {
            "help": self.help,
            "list": self.ls,
            "show": self.cat,
            "remove": self.rm,
            "clear": self.cls,
            "stats": self.stats,
            "turbo": self.toggle_turbo,
            "edit": self.ed,
            "info": self.info,
            "run": self.run,
            "stop": self.stop,
            "led": self.led,
            "exe": self.exe
        }
        self.user_commands_manual = {
            "list": "list files",
            "show <filename>": "print filename content",
            "info <filename>": "information about a file",
            "remove <filename>": "remove a file (be careful!)",
            "edit <filename>": "text editor, filename is optional",
            "clear": "clears the screen",
            "turbo": "toggles turbo mode (100% vs 50% CPU speed)",
            "stats": "system statistics",
            "run <filename>": "loads and runs user program (load first)",
            "stop": "stops and unloads latest running program",            
            "led <command>": "manipulating on-board LED. Commands: `on`, `off`",
            "exe <code>": "Running exec(code)"
        }

        self.boot()

    def boot(self):
        machine.freq(self.cpu_speed_range["turbo"] * 1000000)
        self.cls()
        self.welcome()
        self.led("boot")
        while True:
            user_input = input(self.prompt)
            parts = user_input.split()
            if len(parts) > 0:
                command = parts[0]
                if command in self.user_commands:
                    if len(parts) > 1:
                        arguments = parts[1:]
                        self.user_commands[command](*arguments)
                    else:
                        self.user_commands[command]()
                else:
                    self.unknown_function()

    def banner(self):
        print("\033[1;33;44m                                 ______  _____")
        print("           _________ ___  ____  / / __ \/ ___/")
        print("          / ___/ __ `__ \/ __ \/ / / / /\__ \ ")
        print("         (__  ) / / / / / /_/ / / /_/ /___/ / ")
        print("        /____/_/ /_/ /_/\____/_/\____//____/  ")
        print("-------------\033[1;5;7mTINY-OS-FOR-TINY-COMPUTERS\033[0;1;33;44m------------\n\033[0m")

    def welcome(self):
        self.banner()
        self.stats()
        self.print_msg("Type 'help' for a smol manual.")

    def man(self,manual):
        for cmd,desc in manual.items():
            print("\t\033[7m"+cmd+"\033[0m -",desc)
        utime.sleep(0.5)

    def help(self):
        print(self.name+ " version "+self.version+" user commands:\n")
        self.man(self.user_commands_manual)
        print("\n\033[0;32mSystem created by Krzysztof Krystian Jankowski.")
        print("Source code available at \033[4msmol.p1x.in/os/\033[0m")

    def print_err(self, error):
        print("\n\033[1;37;41m\t<!>",error,"<!>\t\033[0m")
        utime.sleep(1)

    def print_msg(self, message):
        print("\n\033[1;34;47m\t->",message,"\t\033[0m")
        utime.sleep(0.5)

    def unknown_function(self):
        self.print_err("unknown function. Try 'help'.")

    def toggle_turbo(self):
        freq = self.cpu_speed_range["turbo"]
        if self.turbo:
             freq = self.cpu_speed_range["slow"]
        machine.freq(freq * 1000000)
        self.turbo = not self.turbo
        self.print_msg("CPU speed set to "+str(freq)+" Mhz")

    def stats(self):
        print("\t\033[0mBoard:\033[1m",self.board)
        print("\t\033[0mMicroPython:\033[1m",uos.uname().release)
        print("\t\033[0m"+self.name + ":\033[1m",self.version,"(size:",uos.stat("main.py")[6],"bytes)")
        print("\t\033[0mFirmware:\033[1m",uos.uname().version)
        turbo_msg = "\033[0mIn power-saving, \033[1mslow mode\033[0m. Use `turbo` to boost speed."
        if self.turbo:
            turbo_msg = "\033[0mIn \033[1mturbo mode\033[0m. Use `turbo` for slow mode."
        print("\t\033[0mCPU Speed:\033[1m",machine.freq()*0.000001,"MHz",turbo_msg)
        print("\t\033[0mFree memory:\033[1m",gc.mem_free(),"bytes")
        print("\t\033[0mUsed space:\033[1m",uos.stat("/")[0],"bytes")
        print("\t\033[0mFree space:\033[1m",uos.statvfs("/")[0] * uos.statvfs("/")[3],"bytes")

    def cls(self):
         print("\033[2J")

    def ls(self):
        for file in uos.listdir():
            self.info(file)

    def info(self,filename=""):
        if filename == "":
            self.print_err("No file")
            return
        additional = ""
        file_size = uos.stat(filename)[6]
        if filename in self.protected_files: additional = "protected system file"
        print("\t\033[4m"+filename+"\033[0m\t", file_size, "bytes", "\t"+additional)


    def cat(self,filename=""):
        if filename == "":
            self.print_err("Failed to open the file.")
            return
        with open(filename,'r') as file:
            content = file.read()
            print(content)

    def rm(self,filename=""):
        if filename == "":
            self.print_err("Failed to remove the file.")
            return
        if filename in self.protected_files:
            self.print_err("Can not remove system file!")
        else:
            uos.remove(filename)
            self.print_msg("File '{}' removed successfully.".format(filename))

    def run(self,filename=""):
        if not self.background_prog == "":
            self.print_err("Program already running in the background. Use `stop` to stop it.")
            return
        if filename == "":
            self.print_err("Specify a file name to run (without .py).")
            return
        if filename == "main":
            self.print_err("Do *not* try that!")
            return
        
        self.print_msg("Use `stop` command to stop and unload the program.")
        exec(open(filename+".py").read())
        self.background_prog = filename
        self.print_msg("Program loaded. Starting..")
        self.exe(self.background_prog+".start()")

    def stop(self):
        if self.background_prog == "":
            self.pring_err("Nothing to stop.")
            return
        self.exe(self.background_prog+".stop()")
        self.background_prog = ""

    def exe(self,command):
        exec(command)
        
    def led(self,cmd="on"):
        if cmd in ("on",""):
            self.system_led.value(0)
            return
        if cmd=="off":
            self.system_led.value(1)
            return
        if cmd=="boot":
            for _ in range(4):
                self.system_led.value(0)
                utime.sleep(0.1)
                self.system_led.value(1)
                utime.sleep(0.05)
            self.system_led.value(1)
            return

    # edit
    # Minimum viable text editor
    def ed(self, filename=""):
        page_size = 10
        file_edited = False
        edit_mode = True
        show_help = False
        ed_commands_manual = {
            "help": "this help",
            ">": "next page",
            "<": "previous page",
            "10 <line of text>": "replacing 10-th line with a line of text",
            "append <lines>": "append new line(s) at the end of a file, default 1",
            "write or save": "write changes to a file (not implemented yet)",
            "quit": "quit"
        }
        print("Welcome to \033[7medit\033[0m program.\nMinimum viable text editor for smol operating system")
        try:
            with open(filename,'r+') as file:
                if filename in self.protected_files:
                    self.print_err("Protected file. View only.")
                self.print_msg("Loaded existing "+filename+" file.")
                lines = file.readlines()
                line_count = len(lines)
                start_index = 0

                while True:
                    if edit_mode:
                        if start_index < line_count:
                            end_index = min(start_index + page_size,line_count)
                            print_lines = lines[start_index:end_index]

                            print("\033[7m    File:",filename,"Lines:",line_count," // `h` help, `b` back,`n` next page\t\033[0m")

                            for line_num,line in enumerate(print_lines,start=start_index + 1):
                                print(line_num,":",line.strip())
                    else:
                        if show_help:
                            self.man(ed_commands_manual)
                            print("Hit `return` (button or command) to go back to  editing.\n")                            

                    user_ed_input = input("\ned $: ")

                    if user_ed_input =="quit":
                        if file_edited:
                            self.print_msg("file was edited, `save` it first or write `quit!`")
                        else:
                            self.print_msg("edit closed")
                            break

                    if user_ed_input == "quit!":
                        self.print_msg("smolEDitor closed")
                        break

                    if user_ed_input == "help":
                        edit_mode = False
                        show_help = True
                        
                    if user_ed_input in ("","return"):
                        if not edit_mode:
                            edit_mode = True
                            show_help = False
                            
                    if user_ed_input == "append":
                        line_count += 1
                        lines.append("")

                    if user_ed_input == ">":
                        if start_index+page_size < line_count:
                            start_index += page_size
                        else:
                            self.print_msg("There is no next page. This is the last page.")

                    if user_ed_input == "<":
                        if start_index-page_size >= 0:
                            start_index -= page_size
                        else:
                            self.print_msg("Can not go back, it is a first page already.")

                    if user_ed_input in ("save","write"):
                        if filename in self.protected_files:
                            self.print_err("Protected file")
                        else:
                            self.print_err("Saving not implemented yet")

                    parts = user_ed_input.split(" ",1)
                    if len(parts) == 2:
                        if parts[0] == "append":
                            new_lines = int(parts[1])
                            line_count += new_lines
                            for _ in range(new_lines):
                                lines.append("")
                        else:
                            if filename in self.protected_files:
                                self.print_err("Protected file")
                            else:
                                line_number = int(parts[0])
                                new_content = parts[1]                                
                                if line_number > 0 and line_number < line_count:
                                    lines[line_number - 1] = new_content + "\n"
                                else:
                                    self.print_err("Invalid line number")
                        file_edited = True

        except OSError:
            if filename == "":
                self.print_err("Provide an existing file name after the `ed` command.")
            else:
                self.print_err("Failed to open the file.")

smol = smolOS()

