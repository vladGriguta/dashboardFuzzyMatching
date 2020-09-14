# Fuzzy String Matching Application


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


### Unsolved:
1. memory crashes in production: find smaller test sample
2. accept submission of multiple file formats
3. Upldate loading bar