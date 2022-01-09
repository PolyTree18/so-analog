import requests
import datetime
import os
import json
import base64
from cryptography.fernet import Fernet
from utils.str_shorten import shorten_2
from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template, session, make_response
from flask.json import jsonify
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError, MismatchingStateError

requestskey = base64.urlsafe_b64encode(os.urandom(32))
#GITHUB авторизация
client_id = "github-clientID"
client_secret = "github-apptoken"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
freq = Fernet(requestskey)
app = Flask(__name__, template_folder='assets/templates')
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.debug = True
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

def get_user_info(id):
    with open("data/users.json", encoding="utf-8") as usrs:
        users = json.load(usrs)
    info = users[id]
    user = [info["nickname"], info["avatar"], info["rep"]]
    return(user)

@app.route('/')
async def index():
    with open("data/questions.json", encoding="utf-8") as qsts:
        data = json.load(qsts)
    with open("data/users.json", encoding="utf-8") as usrs:
        users = json.load(usrs)
    with open("data/qstats.json", encoding="utf-8") as qsts:
        qstats = json.load(qsts)
    try:
        github = OAuth2Session(client_id, token=session['oauth_token'])
        resp = github.get('https://api.github.com/user').json()
    except:
        user = None
    else:
        if resp.get("message") == "Bad credentials":
            user = None
        else:
            user = resp
    return render_template('index.html', questions=data, users=users, qstats=qstats,
                            get_user_info=get_user_info, shorten=shorten_2, user=user)

@app.route('/ask')
async def ask():
    with open("data/questions.json", encoding="utf-8") as qsts:
        data = json.load(qsts)
    with open("data/users.json", encoding="utf-8") as usrs:
        users = json.load(usrs)
    with open("data/qstats.json", encoding="utf-8") as qsts:
        qstats = json.load(qsts)
    try:
        github = OAuth2Session(client_id, token=session['oauth_token'])
        resp = github.get('https://api.github.com/user').json()
    except:
        user = None
    else:
        if resp.get("message") == "Bad credentials":
            user = None
        else:
            user = resp
    return render_template('ask.html', questions=data, users=users, qstats=qstats,
                            get_user_info=get_user_info, shorten=shorten_2, user=user)

@app.route('/login')
async def login():
    return(render_template('login.html'))

@app.route('/login/<provider>')
async def provider_login(provider):
    if not request.args.get('redirect_uri'):
        if provider == "github":
            github = OAuth2Session(client_id)
            authorization_url, state = github.authorization_url(authorization_base_url)
            session['oauth_state'] = state
            return redirect(authorization_url)
    elif request.args.get('redirect_uri') == "index":
        return redirect('/')


@app.route("/session", methods=["GET"])
def _session():
    try:
        github = OAuth2Session(client_id, state=session['oauth_state'])
        token = github.fetch_token(token_url, client_secret=client_secret,
                                   authorization_response=request.url)
        session['oauth_token'] = token
        u = github.get('https://api.github.com/user').json()
        uid = os.urandom(16).hex()
        with open("data/users.json", encoding="utf-8") as fp:
            dt = json.load(fp)
            if dt.get(uid) == None:
                dt[uid] = {"nickname": u["login"],
                    "reg": ["github", str(u["id"])],
                    "avatar": u["avatar_url"],
                    "rep": {
                        "all": 1,
                        "diamonds": 0,
                        "gold": 0,
                        "bronze": 0}
                }
        with open("data/users.json", "w", encoding="utf-8") as fp:
            json.dump(dt, fp)
        session["ds_uid"] = uid
    except (AccessDeniedError, MismatchingStateError, KeyError):
        pass
    return redirect(f"/")


port = int(os.environ.get('PORT', 5000))
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
app.secret_key = os.urandom(24)
app.run(host="0.0.0.0", port=port)
