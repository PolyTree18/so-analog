from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os

app = Flask(__name__)

# Эта информация получена при регистрации нового приложения
# GitHub OAuth здесь: https://github.com/settings/applications/new
client_id = "c3201935975d6ea62ba2"
client_secret = "b83b33316a641f0a2109a4e22d2b4d76a253e09f"
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'

@app.route("/")
def demo():
    """1: Авторизация пользователя.
    Перенаправление пользователя/владельца ресурса к поставщику
    OAuth (например, Github) использование URL-адреса с несколькими
    ключевыми параметрами OAuth.
    """
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)

    # Состояние используется для предотвращения CSRF, оставим на потом.
    session['oauth_state'] = state
    return redirect(authorization_url)


# 2: Авторизация пользователя, это происходит на провайдере.

@app.route("/session", methods=["GET"])
def _session():
    """ 3: Получение токена доступа.
    Пользователь был перенаправлен обратно от поставщика на
    зарегистрированный URL обратного вызова. С этим перенаправлением
    приходит код авторизации, включенный в URL-адрес перенаправления.
    Используем это, чтобы получить маркер доступа.
    """

    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    # На этом этапе уже можно получить защищенные ресурсы, сохраним
    # токен и покажем, как это делается из сохраненного токена в /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Извлечение защищенного ресурса с помощью токена OAuth 2.
    """
    github = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(github.get('https://api.github.com/user').json())


if __name__ == "__main__":
    # Это позволяет нам использовать вызов по HTTP
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
