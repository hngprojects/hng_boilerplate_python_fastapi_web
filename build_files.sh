# build_files.sh
pip3 install -r requirements.txt

# make migrations
python3 manage.py migrate 
python3 manage.py collectstatic
