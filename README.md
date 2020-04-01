```
##################################################################################################################
#	Python				Ansible				Action
##################################################################################################################
#	copyLocalRemote.py		enable_epel_repo		Enable All Repos(EPEL, Jenkins,) Maven
#	copyLocalRemote.py		setup_cloud_init		SetUP Cloud Init(Not Starting)
#	packageInstallation.py		list_install			Install All Default 
#	packageInstallation.py		jenkins_install			Install All Jenkins 
#	packageInstallation.py						Install All Ansible
#	configChanges.py		setup_cloud_init		Enable Services(Enables & Starting)
#	configChanges.py		python_modules			Install Python Modules
#	pluginsInstallation.py		jenkins_plugin			Install Jenkins Plugins
#	pluginsInstallation.py						Add Credential to Jenkins
#	createUserGroup.py		create_group			Create Group
#	createUserGroup.py		create_user			Create Users
#	updateSSHSudoers.py						Add SSH File
#	updateSSHSudoers.py		add_sudoers			Add Sudoers File
##################################################################################################################
```

# Scripts Usage
- Ansible Gather Facts
    ```
    ansible hostgroup -m setup
    ```

- Configuration file for Ansible
    ```
    /etc/ansible/ansible.cfg
    ```

- Change the logging directory to playbook directory
    ```
    1) remote_tmp        = /tmp
    2) host_key_checking = False
    3) log_path          = /root/python_sql_scripts/ansible/logs/ansible-playbook.log
    ```

- Manual Commands to execute
    ```
    - ansible-playbook site.yml -i inventory --extra-vars "ins_pgsql=pgsql_install PG_MAJOR=9.6 PG_MINOR=6" --tags=pgsql_install
    - ansible-playbook site.yml -i inventory --extra-vars "uin_pgsql=pgsql_uninstall PG_MAJOR=9.6 PG_MINOR=6" --tags=pgsql_uninstall

    - ansible-playbook site.yml -i inventory --extra-vars "ins_all=list_install" --tags=list_install
    - ansible-playbook site.yml -i inventory --extra-vars "uin_all=list_uninstall" --tags=list_uninstall

    - ansible-playbook site.yml -i inventory --extra-vars "ins_packer=packer_install packerVersion=1.5.4" --tags=packer_install
    - ansible-playbook site.yml -i inventory --extra-vars "uin_packer=packer_uninstall" --tags=packer_uninstall

    - ansible-playbook site.yml -i inventory --extra-vars "ins_tf=terraform_install tfVersion=0.12.7" --tags=terraform_install
    - ansible-playbook site.yml -i inventory --extra-vars "uin_tf=terraform_uninstall" --tags=terraform_uninstall
    
    - ansible-playbook site.yml -i inventory --extra-vars "ins_jenkins=jenkins_install" --tags=jenkins_install
    - ansible-playbook site.yml -i inventory --extra-vars "jenkins_plugin=jenkins_plugin" --tags=jenkins_plugin
    
    - ansible-playbook site.yml -i inventory --extra-vars "cre_cw=configure_cw RHEL=8" --tags=configure_cw
    - ansible-playbook site.yml -i inventory --extra-vars "rem_cw=remove_cw" --tags=remove_cw

    - ansible-playbook site.yml --extra-vars "mount=mount_volumes" --tags=mount_volumes
    - ansible-playbook site.yml -i inventory --extra-vars "set_epel=set_epel_repo RHEL=7" --tags=enable_epel_repo
    - ansible-playbook site.yml -i inventory --extra-vars "set_ci=setup_cloud_init RHEL=7" --tags=setup_cloud_init

    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group cre_grp=create_group" --tags=create_group
    - ansible-playbook site.yml -i inventory --extra-vars "username=vignesh password=vignesh group_name=root_group tag_group=yes cre_usr=create_user userComment='Root User'" --tags=create_user
    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group add_sudo=add_sudoers" --tags=add_sudoers

    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group del_sudo=remove_sudoers" --tags=remove_sudoers
    - ansible-playbook site.yml -i inventory --extra-vars "username=vignesh del_usr=delete_user" --tags=delete_user
    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group del_grp=delete_group" --tags=delete_group
	```
