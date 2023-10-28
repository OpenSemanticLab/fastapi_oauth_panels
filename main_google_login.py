import re
import fastapi
import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI#, Request
from fastapi.templating import Jinja2Templates

import json
from pprint import pprint
import starlette
#from fastapi import FastAPI
from starlette.config import Config
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

from sliders.pn_app import createApp


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")

#https://console.cloud.google.com/apis/credentials/oauthclient
config = Config('.env')
oauth = OAuth(config)

host = "127.0.0.1"
port = 8001

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

templates = Jinja2Templates(directory="templates")


@app.get('/')
async def homepage(request: fastapi.Request):
    user = request.session.get('user')
    pprint(user)
    if user:
        data = json.dumps(user)
        script = server_document('http://' + host + ':5001/app')
        return templates.TemplateResponse("base.html", {"request": request, "script": script, "data": data})

        #html = (
        #    f'<pre>{data}</pre>'
        #    '<a href="/logout">logout</a>'
        #)
        #return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')

pn.serve({'/app': createApp},
        port=5001, allow_websocket_origin=[host + ":" + str(port)],
         address=host, show=False)


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    pprint(token)

    # OAuth2 / OICD
    user = token.get('userinfo')
    if user:
        print("USER")
        request.session['user'] = dict(user)

    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    request.session.pop('token', None)
    return RedirectResponse(url='/')


if __name__ == '__main__':
    print("MAIN")
    import uvicorn
    uvicorn.run(app, host=host, port=port)