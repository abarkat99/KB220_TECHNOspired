# Student-Grievance-Support-System

A Web Application for students to submit their grievances and for redressors to redress the same.

### Steps to run:
1) Clone it
2) We have used the Sendgrid API for mail you whose api key was kept in a .env file in studentg directory you may do the same if you use sendgrid otherwise you need to change the EMAIL_BACKEND in settings.py 
3) In the terminal, type the following commands:\
cd studentg\
pip3 install -r requirements.txt\
python3 manage.py runserver
4) By default, www.localhost:8000 will be for students any other subdomain or no subdomain will also be for students.\
For Redressal Body: redressal.localhost:8000\
For Admin: admin.localhost:8000\
You will need to edit hosts.py in studentg if you want to change subdomains\
If running on localhost you would also need to add entries in your OS's hosts file.
5) Login Creds:\
Username: university\
Username: institute\
Username: department\
Username: student\
Username: umember\
Password: himanshu1

### Collaborators:-
1) Abdul Aziz Barkat
2) Furqaan Thakur
3) Himanshu Patil
4) Mohtashim Ansari
5) Saloni Mishra
6) Shivam Tiwari
7) Somil Virani

## CONGRATS TO EVERYONE ON WINNING THE SIH 2020!

Special Thanks to:\
Er. Ahlam Ansari (Mentor)\
Mr. Amrullah Zunzunia (Mentor)
