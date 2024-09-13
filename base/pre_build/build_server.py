import os
import textwrap
import subprocess
import pexpect
import sqlite3
import re

def date_gen(required_date):
    try:
        result = subprocess.run(
            ["date", "-j", "-f", "%Y%m%d-%H%M%S", required_date, "+%s"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error converting date: {e}")
        return None
def set_proxy(proxy_type, kadavu_sol):
    command = 'echo "{}" | openssl enc -base64 -d | cut -c 4-'.format(kadavu_sol)
    dec =  subprocess.run(command, shell=True,executable="/bin/sh",stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    dec_pas=dec.stdout.decode().strip()
    os.environ[proxy_type] = 'http://zorro:{}@proxy:3128'.format(dec_pas)

enc_pas="OTg5aGYyODA5OHJKZTM0aAo="
def unset_proxy():
   del os.environ["http_proxy"]
   del os.environ["https_proxy"]

isopath="/home/iso/"
def update_iso_path(file_path, iso):
    iso_path = "/home/iso/{}".format(iso)    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    pattern = re.compile(r'^ISO\s*=\s*')
   
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            if pattern.match(line.strip()):
                file.write(f"\tISO={iso_path}\n")
            else:
                file.write(line)
                
from pathlib import Path         
def touchfile(directory, filename):
    path = Path(directory) / filename
    if path.exists():
        os.utime(path, None)  
    else:
        path.touch()

    

class prerequisites:
    def __init__(self):
        self.cwd=os.getcwd()
        self.update_server_path=self.cwd+"/freebsd-update-server"  
        self.update_server_url="https://github.com/freebsd/freebsd-update-build.git"  
        self.logdir=self.cwd+"/logs"
        
        ##logs path##
        os.makedirs(self.logdir, exist_ok=True)
        self.pexpect_log=self.logdir+"/pexpect_log.txt"
        self.db_name=self.cwd+"/os_info.db"   
        self.stream_keygen=[]

    def git_download(self):
        if not os.path.exists(self.update_server_path):
            set_proxy("http_proxy",enc_pas)
            set_proxy("https_proxy",enc_pas)
            os.system("git clone {} freebsd-update-server".format(self.update_server_url))
            unset_proxy()
    def buildconf_update(self):
        build_conf="scripts/build.conf"
        os.chdir(self.update_server_path)
        if build_conf:
            uname_m = os.popen('uname -m').read().strip()
            open(build_conf, 'w').close()
            build_conf_content = textwrap.dedent(f"""\
            export HOSTPLATFORM={uname_m}  
            export BUILDHOSTNAME={uname_m}-builder.daemonology.net  
            export SSHKEY=/root/.ssh/id_rsa  
            MASTERACCT=root@localhost  
            MASTERDIR=/home/updates""")
            with open(build_conf,'w') as content:
                content.writelines(build_conf_content)

    def build_conf_gen(self,os_version,eol,checksum):
        os_specific_build_path=f"{self.update_server_path}/scripts/{os_version}/amd64"
        os_specific_build_path_content_file=f"{os_specific_build_path}/build.conf"
        eol_in_conf=date_gen(eol)
        print(eol_in_conf)
        os_specific_build_path_content = textwrap.dedent(f"""\
export RELH={checksum} 
export WORLDPARTS="base catpages dict doc games info manpages proflibs lib32"
export SOURCEPARTS="base bin contrib crypto etc games gnu include krb5  /\
                    \n\t\t lib libexec release rescue sbin secure share sys tools  /\
                    \n\t\t ubin usbin cddl"
export KERNELPARTS="generic"
export EOL={eol_in_conf}""")
        if  not os.path.exists(os_specific_build_path):
            os.makedirs(os_specific_build_path)
        if not os.path.isfile(os_specific_build_path_content_file) or os.path.getsize(os_specific_build_path_content_file) == 0:
            print(os_specific_build_path_content_file)
            open(os_specific_build_path_content_file, 'w').close()
            with open(os_specific_build_path_content_file,'w') as content:
                content.writelines(os_specific_build_path_content)
        elif os.path.getsize(os_specific_build_path_content_file) != 0:
            with open(os_specific_build_path_content_file, 'r') as c:
              old_content=c.read()
            if os_specific_build_path_content != old_content:
                with open(os_specific_build_path_content_file,'w') as content:
                    content.writelines(os_specific_build_path_content)
 
        if os.path.isfile(self.update_server_path+"/scripts/build.subr"):
            for i in os.listdir(isopath):
                if os_version in i:
                    iso=i
                    break
            update_iso_path(self.update_server_path+"/scripts/build.subr", iso)


            
    def publickey_signing_gen(self,password):
        command = "sh {}/scripts/make.sh".format(self.update_server_path)
        child = pexpect.spawn(command, encoding='utf-8', logfile=open(self.pexpect_log, 'w'))
        print(child)
        child.expect("password:")
        child.logfile = None ## stops the password being logged
        child.sendline(password)
        child.expect("password:")
        child.logfile = None
        child.sendline(password)
        child.expect(pexpect.EOF)
        with open(self.pexpect_log, 'r') as cont:
            return cont.readlines()


    def sqlite_table_creator(self,command,table_name,keyvalue=None):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            print(command,table_name,keyvalue)
            match command:
                case "create_table":
                    create_table_query = '''
                                CREATE TABLE IF NOT EXISTS {} (
                                    id INTEGER PRIMARY KEY,
                                    key TEXT NOT NULL,
                                )
                                '''.format(table_name)
                    cursor.execute(create_table_query)
                    conn.commit()
                    conn.close()
                    return "table created!"
                case "add_value":
                    insert_query = '''
                                INSERT INTO {} (key)
                                    VALUES (?)
                                    '''.format(table_name)
                    cursor.execute(insert_query, (keyvalue,))
                    conn.commit()
                    conn.close()
                    return True
                
                case "check_table":
                    check_empty_query = '''
                    SELECT COUNT(*) FROM {}
                    '''.format(table_name)
                    
                    try:
                        cursor.execute(check_empty_query)
                    except sqlite3.OperationalError as e:
                        return "no table"
                    result = cursor.fetchone()[0]
                    if result == 0:
                        return False
                    else:
                        return True
    
class Builder:
    def __init__(self):
        self.cwd=os.getcwd()
        self.update_server_path =self.cwd+"/freebsd-update-server" 
        self.logdir=self.cwd+"/logs" 
        os.makedirs(self.logdir, exist_ok=True)
        self.build_init_log=self.logdir+"/build_init_log.txt"
        if not os.path.isfile(self.build_init_log):
            touchfile(self.logdir,self.build_init_log)
           

    def build_init(self, os_vers: str) -> subprocess.Popen:
        command = "{}/scripts/init.sh amd64 {} &".format(self.update_server_path, os_vers)   
        with open(self.build_init_log, 'w') as log_file:
                process = subprocess.Popen(
                    command, 
                    shell=True, 
                    stdout=log_file, 
                    stderr=subprocess.STDOUT
                
                )
                print(process.pid)

