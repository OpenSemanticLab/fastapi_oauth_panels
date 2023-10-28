import os
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

from mwoauth import ConsumerToken, Handshaker, AccessToken

from sliders.pn_app import createApp

from osw.auth import CredentialManager
import osw.model.entity as model
from osw.core import OSW
from osw.wtsite import WtSite

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="!secret")

oauth = OAuth()

host = os.environ.get('APP_HOST')
port = int(os.environ.get('APP_PORT'))
internal_host = 'localhost'
internal_port = 5001
osw_server = os.environ.get('OSW_SERVER')

key = os.environ.get('OAUTH_CLIENT_ID')
secret = os.environ.get('OAUTH_CLIENT_SECRET')


oauth.register(
    name='mediawiki',
    #api_base_url='/wiki/Special:OAuth/initiate',
    request_token_url=osw_server+'/wiki/Special:OAuth/initiate',
    access_token_url=osw_server+'/wiki/Special:OAuth/token',
    authorize_url=osw_server+'/wiki/Special:OAuth/authorize',
    client_id =key,
    client_secret=secret,
)

consumer_token = ConsumerToken(  key = key, secret=secret)
# Construct handshaker with wiki URI and consumer
handshaker = Handshaker(osw_server+"/w/index.php",
                        consumer_token)

templates = Jinja2Templates(directory="templates")

def test_osw(request):
    cm = CredentialManager()
    cm.add_credential(cred=CredentialManager.OAuth1Credential(
        iri="wiki-dev.open-semantic-lab.org",
        consumer_token= key,
        consumer_secret= secret,
        access_token= request.session['token']['oauth_token'],
        access_secret= request.session['token']['oauth_token_secret']
    ))
    wtsite = WtSite(WtSite.WtSiteConfig(iri="wiki-dev.open-semantic-lab.org", cred_mngr=cm))
    osw = OSW(site=wtsite)

    my_entity = model.Item(
        label=[model.Label(text="MyItem")]#, statements=[model.Statement(predicate="IsA")]
    )
    pprint(my_entity)

    osw.store_entity(my_entity)

    my_entity2 = osw.load_entity("Item:" + OSW.get_osw_id(my_entity.uuid))
    pprint(my_entity)

    #osw.delete_entity(my_entity)

@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    #pprint(user)
    if user:
        test_osw(request)
        data = json.dumps(user)
        script = server_document('http://' + internal_host + ':' + str(internal_port) + '/app')
        return templates.TemplateResponse("base.html", {"request": request, "script": script, "data": data})

    return HTMLResponse('<a href="/login">login</a>')

pn.serve({'/app': createApp},
        port=internal_port, allow_websocket_origin=[host + ":" + str(port)],
         address=host, show=False)


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.mediawiki.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.mediawiki.authorize_access_token(request)
        token["userinfo"] = handshaker.identify(AccessToken( token["oauth_token"], token["oauth_token_secret"]))
    except OAuthError as error:
        pprint(error)
        return HTMLResponse(f'<h1>{error.error}</h1>')
    #pprint(token)

    # OAuth2 / OICD
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        request.session['token'] = dict(token)

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