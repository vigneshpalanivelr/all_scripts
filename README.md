# Scripts Usage
- Configuration file for Ansible
	```
	- /etc/ansible/ansible.cfg
	```

- Change the logging directory to playbook directory
	```
    - remote_tmp        = /tmp
    - host_key_checking = False
    - log_path          = /root/python_sql_scripts/ansible/logs/ansible-playbook.log
	```

- Manual Commands to execute
	```
    - ansible-playbook site.yml --extra-vars "ins_pgsql=pgsql_install" --tags=pgsql_install
    - ansible-playbook site.yml --extra-vars "ins_pgsql=pgsql_install uin_pgsql=pgsql_uninstall" --tags=pgsql_install --tags=pgsql_uninstall
    
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
    - ansible-playbook site.yml --extra-vars "set_ci=setup_cloud_init" --tags=setup_cloud_init

    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group cre_grp=create_group" --tags=create_group
    - ansible-playbook site.yml -i inventory --extra-vars "username=vignesh password=vignesh group_name=root_group tag_group=yes cre_usr=create_user userComment='Root User'" --tags=create_user
    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group add_sudo=add_sudoers" --tags=add_sudoers

    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group del_sudo=remove_sudoers" --tags=remove_sudoers
    - ansible-playbook site.yml -i inventory --extra-vars "username=vignesh del_usr=delete_user" --tags=delete_user
    - ansible-playbook site.yml -i inventory --extra-vars "group_name=root_group del_grp=delete_group" --tags=delete_group
	```
