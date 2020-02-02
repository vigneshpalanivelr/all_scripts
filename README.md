# postgresql_previlages_sql
- Configuration file for Ansible
	```
	- /etc/ansible/ansible.cfg
	```

- Command To Execute Ansible Playbooks
	```
	- ansible-playbook site.yml --tags=pgsql_uninstall --tags=pgsql_install
	```

- Change the logging directory to playbook directory
	```
	- log_path = /root/python_sql_scripts/ansible/logs/ansible-playbook.log
	```

- Create a Group
	```
	- ansible-playbook site.yml --extra-vars "group_name=root_group action=create_group" --tags=create_group
	```

- Create a User
	```
	- ansible-playbook site.yml --extra-vars "username=test password=test group_name=root_group tag_group=yes action=create_user" --tags=create_user
	```

- Delete a User
	```
	- ansible-playbook site.yml --extra-vars "username=test action=delete_user" --tags=delete_user
	```

- Delete a Group
	```
	ansible-playbook site.yml --extra-vars "group_name=root_group action=delete_group" --tags=delete_group
	```
