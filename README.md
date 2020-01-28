# postgresql_previlages_sql
Configuration file for Ansible is /etc/ansible/ansible.cfg

1) Command To Execute Ansible Playbooks
	a. ansible-playbook site.yml --tags=pgsql_uninstall --tags=pgsql_install

2) Change the logging directory to playbook directory
	a. log_path = /root/python_sql_scripts/ansible/logs/ansible-playbook.log
