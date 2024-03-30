"""Main app of project: Tout doux list"""

from datetime import datetime
from time import time
from json import loads, dumps
from flask import Flask, render_template, request, session, redirect, url_for, abort, g
from authlib.integrations.flask_client import OAuth
from requests import post
from models import AccountManager, run_db
from tools import verif_password, Cryptographie, Env

app = Flask(__name__)
app.secret_key = Cryptographie("APP_KEY").get_key()
oauth = OAuth(app)

env = Env()

google = oauth.register(
    name="google",
    client_id=env.get_var("GOOGLE_CLIENT_ID"),
    client_secret=env.get_var("GOOGLE_CLIENT_SECRET"),
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    authorize_params=None,
    access_token_url="https://www.googleapis.com/oauth2/v4/token",
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    client_kwargs={"scope": "openid email profile"},
    redirect_uri="http://127.0.0.1:5000/login/google/callback",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
)


def send_msg_webhook(msg):
    """Send message to discord server: Tout doux liste"""
    url = (
        "https://discordapp.com/api/webhooks/"
        + "1222549140689653760/vyS4LPlk8Bq0t9SurtkaNPuVMdh-iEjSuELwznK75xGEcVHeEOfhJc0d1M95kE3NnkyU"
    )
    data = {"username": "Tout-doux-list-webhooks", "content": msg}
    timeout_seconds = 10
    post(url, json=data, timeout=timeout_seconds)


def get_all_routes():
    """Get all routes"""
    return [rule.rule for rule in app.url_map.iter_rules()][1:]


def get_actual_route(request_):
    """Get the current route"""
    return "/" + "/".join(request_.url.split("/")[3:])


def verif_actual_route():
    """Check if the route is the current one"""
    return get_actual_route(request) in get_all_routes()


@app.before_request
def before_request():
    """Process before all requests"""
    if not session.get("stay") and verif_actual_route():
        if session.get("last_time"):
            time_difference = time() - session.get("last_time")
            time_limit = 60 * 60 * 10
            if time_difference > time_limit and "account" in session:
                del session["account"]
        session["last_time"] = time()
    g.year = datetime.now().year


@app.route("/")
def index():
    """Page of index (First page)"""
    return render_template("index.html")


@app.route("/inscription/", methods=["GET", "POST"])
def inscription():
    """Page for inscription (with google optionnal)"""
    account_manager = AccountManager()

    if request.method == "POST":
        get_input = request.form.get
        name = get_input("name")
        email = get_input("email")
        password = get_input("password")
        stay_connect = get_input("checkbox") == "true"
        error = verif_password(password)
        if not error:
            if name != name.title():
                error = "Votre nom n'a pas de majuscule(ex à mettre: Titi, Grominet)"
            elif account_manager.verif_email(email) or account_manager.verif_account(
                email, password
            ):
                error = "Ce compte existe déjà"
            elif account_manager.verif_name(name):
                error = "Ce nom existe déjà"
        if not error:
            session["account"] = account_manager.add_account(name, email, password)
            session["stay"] = stay_connect
            return redirect("/")
        return render_template("inscription.html", error=error)
    return render_template("inscription.html")


@app.route("/connexion/", methods=["GET", "POST"])
def connexion():
    """Page for connexion (with google optionnal)"""
    account_manager = AccountManager()

    if request.method == "POST":
        get_input = request.form.get
        email = get_input("email")
        password = get_input("password")
        stay_connect = get_input("checkbox") == "true"
        error = verif_password(password)
        if not error and (
            not account_manager.verif_email(email)
            or not account_manager.verif_account(email, password)
        ):
            error = "Ce compte n'existe pas"
        if not error:
            session["account"] = account_manager.to_dict_reduct(email, password)
            session["stay"] = stay_connect
            return redirect("/")
        return render_template("connexion.html", error=error[0])
    return render_template("connexion.html")


@app.route("/login/<provider>/")
def oauth_login(provider):
    """Login with google"""
    if provider not in ["google", "instagram"]:
        abort(404)

    oauth_provider = getattr(oauth, provider)
    return oauth_provider.authorize_redirect(
        url_for("authorized", provider=provider, _external=True)
    )


@app.route("/login/<provider>/callback")
def authorized(provider):
    """Callback of google connexion"""
    if provider not in ["google", "instagram"]:
        abort(404)
    oauth_provider = getattr(oauth, provider)
    token = oauth_provider.authorize_access_token()
    user_info = loads(dumps(token))["userinfo"]
    session["account"] = {"email": user_info["email"]}
    return redirect(url_for("index"))


@app.route("/logout/")
def logout():
    """Log out of the current account"""
    del session["account"]
    return render_template("signout.html")


@app.route("/contacts/", methods=["GET", "POST"])
def contacts():
    """Contacts page for sent email"""
    if request.method == "POST":
        get_input = request.form.get
        email = get_input("email")
        content = get_input("content")
        content = f"""-------------------------------------------------
From: {email} for 'vous contacter' \n{content}"""
        send_msg_webhook(content)
    return render_template("contacts.html")


@app.route("/todolist/", methods=["GET", "POST"])
def todolist():
    """Main Todolist menu"""
    return render_template("todolist.html")


if __name__ == "__main__":
    run_db()
    app.run(debug=True)
