# CI/CD in AWS Cloud Automation
- SetUp Using Python and Ansible
- Remove Using Ansible


###  Available Scripts and Usages
| Python | Ansible | Action |
| ------ | ------ | ------ |
| copyLocalRemote | enable_epel_repo | Enable All Repos(EPEL, Jenkins,) Maven |
| copyLocalRemote | setup_cloud_init | SetUP Cloud Init(Not Starting)|
| packageInstallation | list_install | Install All Default Packages | 
| packageInstallation | jenkins_install | Install Jenkins |
| packageInstallation | ![#f03c15](`Yet To Create`) | Ansible |
| configChanges | setup_cloud_init | Enable Services(Enables & Starting) |
| configChanges | python_modules | Install Python Modules |
| pluginsInstallation | jenkins_plugin | Install Jenkins Plugins |
| pluginsInstallation | `Yet To Create` | Add Credential to Jenkins |
| createUserGroup | create_group | Create Group |
| createUserGroup | create_user | Create Users |
| updateSSHSudoers | `Yet To Create` | Add SSH File |
| `Yet To Create` | terraform_install | Install Terraform |
| `Yet To Create` | packer_install | Install Packer |
| `Yet To Create` | pgsql_install | Install PostgreSQL |
| `Yet To Create` | configure_cw | Configure CW for EC2 |
| `Yet To Create` | mount_volumes | Mount Volumes on EC2 |

###  Requirements and Installation
Requirments
1) [Git](https://github.com/) : To clone the project
2) [Python](https://www.python.org/) : To execute the codes

Install the Dependencies and start the server.

```sh
/bin/yum install git-core -y
/bin/yum install python2 -y
```

### Python Usage
Provided that below assumptions were made
1) RHEL
2) GitHub Password
3) Group Name

```sh
/bin/git clone https://github.com/vigneshpalanivelr/all_scripts.git
cd /root/all_scripts/python/ && /bin/python copyLocalRemote.py 7
cd /root/all_scripts/python/ && /bin/python packageInstallation.py -install -pkg ansible -pkg jenkins
cd /root/all_scripts/python/ && /bin/python configChanges.py 7 -py_module -start -service SSH -service jenkins
cd /root/all_scripts/python/ && /bin/python pluginsInstallation.py -install -list 
cd /root/all_scripts/python/ && /bin/python pluginsInstallation.py -descrptn gitCreds -username vigneshpalanivelr -password <password>
cd /root/all_scripts/python/ && /bin/python createUserGroup.py group create --group_name root_group --user_name jenkins --add_to_grp
cd /root/all_scripts/python/ && /bin/python updateSSHSudoers.py -add_sudo -sudo root_group

systemctl status updateSSHSudoersInitd
```

### Ansible Usage
Provided that below assumptions were made
1) Username
2) Password
3) Group Name
4) TF Version
5) Packer Version
6) PostgreSQL Version

```sh
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "set_epel=set_epel_repo RHEL=7" --tags=enable_epel_repo
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "set_ci=setup_cloud_init RHEL=7" --tags=setup_cloud_init
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "ins_all=list_install" --tags=list_install

cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "ins_jenkins=jenkins_install" --tags=jenkins_install
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "jenkins_plugin=jenkins_plugin" --tags=jenkins_plugin

cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "python_modules=python_modules" --tags=python_modules

cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group cre_grp=create_group" --tags=create_group
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "username=vignesh password=vignesh group_name=root_group tag_group=yes cre_usr=create_user userComment='Root User'" --tags=create_user
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group add_sudo=add_sudoers" --tags=add_sudoers

cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "ins_tf=terraform_install tfVersion=0.12.7" --tags=terraform_install
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "ins_packer=packer_install packerVersion=1.5.4" --tags=packer_install
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "ins_pgsql=pgsql_install PG_MAJOR=9.6 PG_MINOR=6" --tags=pgsql_install
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "cre_cw=configure_cw RHEL=8" --tags=configure_cw
cd /root/all_scripts/python/ && ansible-playbook site.yml --extra-vars "mount=mount_volumes" --tags=mount_volumes

cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "uin_all=list_uninstall" --tags=list_uninstall
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group del_sudo=remove_sudoers" --tags=remove_sudoers
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "username=vignesh del_usr=delete_user" --tags=delete_user
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group del_grp=delete_group" --tags=delete_group

cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "uin_tf=terraform_uninstall" --tags=terraform_uninstall
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "uin_packer=packer_uninstall" --tags=packer_uninstall
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "uin_pgsql=pgsql_uninstall PG_MAJOR=9.6 PG_MINOR=6" --tags=pgsql_uninstall
cd /root/all_scripts/python/ && ansible-playbook site.yml -i inventory --extra-vars "rem_cw=remove_cw" --tags=remove_cw
```

### Todos
 - Complete Ansible and Python `Yet to Create`


#### Authour
Vignesh Palanivel
