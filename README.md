# roads-cba-py - pure python module for the Cost Benefit Analysis Subsystem

## 1. Initial setup
This project requires:
* Python >= 3.8
* `pipenv` for Python virtual environment management

### 1.2. Setup the repo
* Clone this repository: `git clone URL`

* After that, run `python -m pipenv shell` to activate the Python virtual environment for this project

* Then run `pipenv install --dev` to install all required dependencies for this project. You would need to occasionally run this command as you fetch new updates from this repository

* Then run `python cba/manage.py migrate` to run all latest database migrations

* Then run `python cba/manage.py runserver` to start the development server

* And voila! You've completed the neccessary steps to set up a local development environment for this project.
