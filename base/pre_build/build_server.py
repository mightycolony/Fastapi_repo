import os
import textwrap
import subprocess
# Fetch the value of uname -m

def date_gen(required_date):
    return os.system("date -j -f '%Y%m%d-%H%M%S' '{}' '+%s'")

class prerequisites:
    ##required path##
    def __init__(self):
        self.cwd=os.getcwd()
        self.update_server_path=self.cwd+"/freebsd-update-server"  
        self.update_server_url="https://github.com/freebsd/freebsd-update-build.git"  

    def git_download(self):
        if not os.path.exists(self.update_server_path):
            os.system("git clone {} freebsd-update-server".format(self.update_server_url))
    
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

    def publickey_signing_gen(self,password):
        command = ['sh', '{}/scripts/make.sh'.format(self.update_server_path)]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.stdin.write(b'pass123\n')
        process.stdin.flush()
        stdout, stderr = process.communicate()
        


