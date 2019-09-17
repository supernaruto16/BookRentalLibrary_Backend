# UET_BookRentalLibrary_Backend

### Installation

```bash
virtualenv venv -p python3.6
source venv/bin/activate
pip install -r requirements.txt
python init_deploy.py
gunicorn --workers=12 --thread=4 --bind 0.0.0.0:5000 wsgi:app

```

#### Development

```bash
git config credential.helper store
pip freeze > requirements.txt

