import os
import shutil
import subprocess

def copytree(source, destination, symlinks=False, ignore=None, permission=None):
	# Ref : https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
	if not os.path.exists(destination):
		os.makedirs(destination)
		shutil.copystat(source, destination)
	if os.path.isdir(source):
		copy_list = os.listdir(source)
	elif os.path.isfile(source):
		copy_list = [source.split('/')[-1]]
		source       = '/'.join(source.split('/')[:-1])
	if ignore:
		exclude	 = ignore(source, copy_list)
		copy_list       = [x for x in copy_list if x not in exclude]
	for item in copy_list:
		src = os.path.join(source, item)
		des = os.path.join(destination, item)
		if symlinks and os.path.islink(src):
			if os.path.lexists(des):
				os.remove(des)
			os.symlink(os.readlink(src), des)
			try:
				st	      = os.lstat(src)
				mode    = stat.S_IMODE(st.st_mode)
				os.lchmod(des, mode)
			except:
				pass # lchmod not available
		elif os.path.isdir(src):
			copytree(src, des, symlinks, ignore)
		else:
			shutil.copy2(src, des)
			if permission != None:
				subprocess.call(['chmod', permission, des])
