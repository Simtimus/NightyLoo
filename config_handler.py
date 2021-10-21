import os

prefix = '.'
TOKEN = ''
vesela_host = ''
vesela_user = ''
vesela_password = ''
vesela_database = ''

school_host = ''
school_user = ''
school_password = ''
school_database = ''

is_local_run = False
if 'local_config.py' in os.listdir('.'):
	import local_config
	is_local_run = True
	prefix = '_'

	TOKEN = local_config.TOKEN
	vesela_host = local_config.vesela_host
	vesela_user = local_config.vesela_user
	vesela_password = local_config.vesela_password
	vesela_database = local_config.vesela_database

	school_host = local_config.school_host
	school_user = local_config.school_user
	school_password = local_config.school_password
	school_database = local_config.school_database
else:
	TOKEN = os.getenv('TOKEN')
	vesela_host = os.getenv('vesela_host')
	vesela_user = os.getenv('vesela_user')
	vesela_password = os.getenv('vesela_password')
	vesela_database = os.getenv('vesela_database')

	school_host = os.getenv('school_host')
	school_user = os.getenv('school_user')
	school_password = os.getenv('school_password')
	school_database = os.getenv('school_database')
