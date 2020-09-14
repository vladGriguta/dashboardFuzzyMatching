# Fuzzy String Matching Application

Wellcome to fuzzy-string-matching, a web application that automizes the task of merging together lists of incomplete/misspelled names.


![Alt Text](https://github.com/vladGriguta/dashboardFuzzyMatching/blob/master/resources/walkthrough.gif)


### To run:
```
# in the terminal
pip install redis
redis-server

# to run the dashboard:
gunicorn app:server

# to view the jobs queued in the redis server:
python worker.py

```

### Unresolved Issues:
1. memory crashes in production: find smaller test sample
2. accept submission of multiple file formats
3. Upldate loading bar


### Useful commands
```

git push heroku master
heroku ps:scale worker=1
heroku logs -d worker --tail
heroku logs -d web --tail

redis-cli FLUSHDB
redis-server
python worker.py


heroku addons:create heroku-redis:hobby-dev
heroku addons:create redistogo

```