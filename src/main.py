"""
MIT License

Copyright (c) [2023] [Siddharth Upadhyay]

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



import subprocess
import datetime
import os
from pathlib import Path
from rich.console import Console
from rich.progress import track
import shutil
import argparse

# Console to log from
console = Console()


class Backup:

    home = str(Path.home())
    fonts_path = home + "/.fonts"

    # Dummy mode for debugging
    dummy_mode = False

    # False by default
    backup_fonts = False

    # Current directory by default
    backup_path = Path.cwd()

    # config_path 
    config_path = str(backup_path) + "/configs/"

    # Files to backup
    file_backups = {}

    app_with_configs = {
        "helix":[
            home + "/.config/helix/config.toml",
            home + "/.config/helix/init.lua"
        ],
        "alacritty":[
            home+ "/alacritty.yml",
            home + "/.config/alacritty/alacritty.yml",
            home + "/.alacritty.yml",
        ],
        "fish": [
            home + "/.config/fish/conf.d/",
            home + "/.config/fish/config.fish",
            home + "/.config/fish/functions/"
        ],
        "neovim":[
            home + "/nvim/init.vim",
            home + "/nvim/sysinit.vim",
            "/etc/xdg/nvim/sysinit.vim"
        ],
        "tmux" : [
            home + "/.tmux.conf",
            home + "/.config/tmux/tmux.conf" 
        ],
        "codium": [
            home + "/.config/VSCodium/User/settings.json"
        ],
        "vscode": [
            home + "/.config/Code/User/settings.json"
        ],
    }

    def arg_parse(self):
         
        parser = argparse.ArgumentParser(
            prog = 'Pyhero',
            description = 'Backs up your lovely configs \u2699 with 🐍',
            epilog = 'Refer to --help or -h for more help',
            usage = 'python3 main.py --path=[PATH] [--fonts] [--dummy] [--cargo] [--pip]'
        )

        parser.add_argument("-p","--path",type=str,required=False,help='Path to store the configurations at')

        parser.add_argument('-f','--fonts',required=False, action='store_true',help='Backup fonts too')

        parser.add_argument('--pip',required=False,action='store_true',help='Backup the list of pip packages')

        parser.add_argument('-d','--dummy',required=False,action='store_true',help='Run the program but don\'t write the files')

        parser.add_argument('-c','--cargo',required=False,action='store_true',help='Backup the list of cargo binaries installed')


        # Enable the parser
        args = parser.parse_args()

        if args.path is None:
            console.log("No path given. Hence saving in the current directory")
            console.print(f"\u2022 Saving in the directory... [bold]{self.backup_path} [/ bold]\n",end='')
        else:
            self.backup_path = Path(args.path).expanduser()
            if self.backup_path.exists() is False:
                console.log("Given path doesn'exist! Please input a valid path to save configs in")
                exit(1)
            

        with console.status("[white]Finding home directory [/ white ]") as status:

            console.print(f"\u2022 Home directory :[bold green] {self.home} [/ bold green]\n")

            for (key,value) in self.app_with_configs.items():
                status.update(f"Finding config for [yellow]{key}...[/ yellow]")
                once = False
                to_save = []
                for con_path in value:
                    if Path(con_path).exists():
                        to_save.append(con_path)
                        if once is False:
                            console.log(f"Found config for [bold]{key}...[/ bold]")
                            once = True
                        if con_path == value[-1]:
                            self.file_backups[key] = to_save
                    else:
                        if con_path == value[-1]:    
                            self.file_backups[key] = to_save

            # Find if fonts exists

            if args.fonts is True:
                self.backup_fonts = True
                status.update("Finding fonts to backup...")
                if Path(self.fonts_path).exists():
                    console.print(f"\u2022 Fonts found at [bold white]{self.fonts_path}[/ bold white]...",end='')

            else:
                self.backup_fonts = False


            cargo_bins = []
            if args.cargo is True:
                status.update("Finding cargo installed binaries...")
                cargo_list = subprocess.run(["cargo","install","--list"],capture_output=True,text=True)    
                console.print("\n\u2022 Following cargo binaries are installed:-")
                for i in cargo_list.stdout.splitlines():
                    console.print(f"\t{i}")

                # Logic for cargo binaries
                for line in cargo_list.stdout.splitlines():
                    index = line.find('v')
                    if index == -1:
                        continue
                    else:
                        cargo_bins.append(str(line[0:index]).strip())

            pip_packages = []
            if args.pip is True:

                status.update("Looking for python packages...")
                # Logic for pip packages
                pip_list = subprocess.run(["pip","list"],capture_output=True,text=True)
                console.print("\u2022 Following pip packages are installed:-")
                lines = pip_list.stdout.splitlines()[2:]
                count = 0
                pip_once = False
                for line in lines:
                    index = line.find(' ')
                    count += 1
                    pip_packages.append(line[:index])
                    if count < 10:
                        console.print(f"\t{line}")
                    else:
                        if pip_once is False:
                            console.print(f"Plus {len(lines)} more...")
                            pip_once = True
            self.config_path = str(self.backup_path) + "/configs/"
            print("\n")
            if self.dummy_mode is False:

                for i in track(self.file_backups,description='[green] Copying config files [/ green]'):
                    # This will print a path like $pwd/codium or $pwd/vim to save the 
                    # specific config file
                    dest_dir = self.config_path + i + "/"

                    # Now let's create the required directories for these files
                    # This will ensure that the directories are created

                    files = self.file_backups[i]
                    if files.__len__() != 0:
                        os.makedirs(dest_dir,exist_ok=True)            
                        for file in files :
                            path = Path(file)
                            try:
                                if path.is_dir():
                                    base_name = os.path.basename(path)
                                    full_path = dest_dir + base_name 
                                    shutil.copytree(str(path) ,full_path,dirs_exist_ok=True)
                                elif path.is_file:
                                    shutil.copy2(path,dest_dir)
                            except PermissionError:
                                console.log(f"Permission denied to copy:{path}")                


                # Now let's copy fonts
                if self.backup_fonts:
                    status.update("Copying fonts...")

                    font_dest = self.config_path + "fonts"
                    # Create dirs
                    os.makedirs(font_dest,exist_ok=True)
                    # Copy them
                    shutil.copytree(self.fonts_path,font_dest,dirs_exist_ok=True)
                    console.print(f"\u2022 Fonts have been copied to: [bold white]{font_dest}[/ bold white]")


                # Now let's save the name of pip and cargo packages/binaries
                status.update("Saving the list of pip and cargo packages...")
                pip_path = self.config_path + 'pip_pkg.txt'
                cargo_path = self.config_path + 'cargo_pkg.txt'

                if args.pip is True:
                    with open(self.config_path + 'pip_pkg.txt','w') as pipfile:
                        for i in pip_packages:
                            pipfile.write(f"{i}\n")
                    console.log("\u2022 Pip packages synced...")
                if args.cargo:
                    with open(self.config_path + "cargo_pkg.txt", 'w') as c_file:
                        for i in cargo_bins:
                            c_file.write(f"{i}\n")
                    
                    console.log("\u2022 Cargo binaries synced...")
                if args.pip:

                    console.print(f"\n\u2022 Pip packages:[bold white]{pip_path}[/ bold white]")

                if args.cargo:
                    console.print(f"\n\n\u2022 Cargo packages:[bold white]{cargo_path}[/bold white]\n")


                current_time = datetime.datetime.now().strftime("%y:%m:%d:%H:%M:%S")

                with open(self.config_path + "report.txt",'w') as tfile:
                    tfile.write(f"Backup last synced at\n{current_time} \n")        

                console.print("\u2022 All files have been successfully copied")




    
    def app_installed(self,app_name):    
        try:
            subprocess.check_output(["which",app_name])
            return True
        except subprocess.CalledProcessError:
            return False


    def run(self):

        self.arg_parse()

 





# Written only for my personal usage
if __name__ == "__main__":
    backup = Backup()
    backup.run()

    

