from edu_lite import db
from edu_lite.models import Students
from passlib.hash import sha256_crypt


validate_name = False
while validate_name == False:
	name = input("Enter admin username:")
	if name == '':
		print("Name can't be blank!")
	elif ' ' in name:
		print("Name can't contain spaces!")
	elif len(name) < 3:
		print("Name is too short!")
	else:
		validate_name = True

validate_password = False
while validate_password == False:
	raw_password = input("Enter password:")
	if raw_password == '':
		print("Password can't be blank!")
	if ' ' in raw_password:
		print("Password can't contain spaces!")
	if len(raw_password) < 4:
		print("Password is too short!")
	else:
		validate_password = True

crypt_password = sha256_crypt.hash(raw_password)
new_user = Students(name, crypt_password, 1)  
db.session.add(new_user)
db.session.commit()