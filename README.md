![foodgram CI/CD workflow](https://github.com/Shadowmoses1314/social_network_project/actions/workflows/python-app.yml/badge.svg)

# Yatube Social Network
___
Yatube is a social network that allows authors to create posts on various topics, comment on posts, and follow/unfollow authors. It includes administration features, user management, post management (creation, editing, deletion), community-based grouping of posts, pagination, email messaging to users, and basic website page templates. The project is built using Python 3.7 and Django 2.2.16, and it utilizes SQLite for data storage.
___
## Stack:
___
- Python 3.7
- Django 3.2.6
___
### To run the project in development mode, follow these steps:

Clone the repository: 
```
git clone https://github.com/Shadowmoses1314/social_network_project.git
```
Set up and activate the virtual environment:
bash
Copy code
```
python -m venv venv
```
```
source venv/Scripts/activate
```
Install the dependencies from the requirements.txt
```
file: pip install -r requirements.txt
```
Navigate to the yatube/yatube directory.
Apply migrations:
Copy code
```
python manage.py makemigrations
python manage.py migrate
```
Run the project:
```
python manage.py runserver
```
#### *Backend by:*
[ShadowMoses1314](https://github.com/Shadowmoses1314)
