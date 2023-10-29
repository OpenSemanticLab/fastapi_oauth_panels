import os
import re
import fastapi
import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

import json
from pprint import pprint
import starlette
#from fastapi import FastAPI
from starlette.config import Config
#from starlette.requests import Request
#from starlette.middleware.sessions import SessionMiddleware
from starlette_authlib.middleware import AuthlibMiddleware as SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from authlib.jose import JsonWebEncryption, jwt

from mwoauth import ConsumerToken, Handshaker, AccessToken

#from sliders.pn_app import createApp
from osw_app.pn_app import createApp

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
# 128 bit key to sign the JWT
jwt_key = bytes.fromhex("74738ff5536759589aee98fffdcd1876")
# 128 bit key to encrypt the JWT as JWE
jwe_key = bytes.fromhex("74738ff5536759589aee98fffdcd1876")

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

def get_jwe_from_json(json_payload) -> str:
    
    # create the JWT
    jwt_header = {'alg': 'HS256'}
    jwt_payload = json_payload
    jwt_encoded = jwt.encode(jwt_header, jwt_payload, jwt_key)

    # create the JWE
    jwe = JsonWebEncryption()
    jwe_header = {'alg': 'A128KW', 'enc': 'A128CBC-HS256'}
    jwe_payload = jwt_encoded
    jwe_encrypted = jwe.serialize_compact(jwe_header, jwe_payload, jwe_key)

    return jwe_encrypted.decode('utf-8')

def get_json_from_jwe(jwe_encrypted: str) -> dict:
    jwe_encrypted = jwe_encrypted.encode('utf-8')
    # decrypt the JWE
    jwe = JsonWebEncryption()
    data = jwe.deserialize_compact(jwe_encrypted, jwe_key)
    jwe_header = data['header']
    payload = data['payload']

    # decode the JWT
    claims = jwt.decode(payload, jwt_key)
    return claims

def get_osw(osw_token) -> OSW:
    cm = CredentialManager()

    cm.add_credential(cred=CredentialManager.OAuth1Credential(
        iri="wiki-dev.open-semantic-lab.org",
        consumer_token= key,
        consumer_secret= secret,
        access_token= osw_token['oauth_token'],
        access_secret= osw_token['oauth_token_secret']
    ))
    wtsite = WtSite(WtSite.WtSiteConfig(iri="wiki-dev.open-semantic-lab.org", cred_mngr=cm))
    osw = OSW(site=wtsite)
    return osw
    #my_entity = model.Item(
    #    label=[model.Label(text="MyItem")]#, statements=[model.Statement(predicate="IsA")]
    #)
    #pprint(my_entity)

    #osw.store_entity(my_entity)

    #my_entity2 = osw.load_entity("Item:" + OSW.get_osw_id(my_entity.uuid))
    #pprint(my_entity)

    #osw.delete_entity(my_entity)

@app.get('/')
async def homepage(request: Request):
    pprint( request.session)
    encrypted_token = request.session.get('osw_token')
    if encrypted_token:
        token = get_json_from_jwe(encrypted_token)
        print("USER GET")
        osw = get_osw(token)
        pn.state.cache['osw'] = osw
        pn.state.cache['osw_user'] = token["username"]
        data = json.dumps(token["username"])
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
        userinfo = handshaker.identify(AccessToken( token["oauth_token"], token["oauth_token_secret"]))
        token["username"] = userinfo['username']
    except OAuthError as error:
        pprint(error)
        return HTMLResponse(f'<h1>{error.error}</h1>')
    pprint(token)
    #pprint( request.session)

    # OAuth2 / OICD
    user = userinfo #token.get('userinfo')
    if token:
        print("USER SET")
        # in general, large objects seem to fail to be stored in the session
        # therefore, we store only token, secret and username (all encrypted)
        request.session['osw_token'] = get_jwe_from_json(token)
        pprint( request.session)

    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('osw_token', None)
    return RedirectResponse(url='/')


if __name__ == '__main__':
    print("MAIN")
    import uvicorn
    uvicorn.run(app, host=host, port=port)