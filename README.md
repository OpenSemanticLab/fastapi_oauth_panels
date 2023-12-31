# FastAPI OAuth Panels

Combines python FastAPI, authlib and panels to provide OAuth-protected apps. A javascript equivalent can be found here: https://github.com/RepoLab/apiclient-wiki/

## How it works
1. The opens the webpage with an empty session => login screen is displayed
![Alt text](docs/image_login-screen.png)
2. Clicking login redirects to the OAuth provider
![Alt text](docs/image_accept-screen.png)
1. If accepted, the user is redirected again to the app, which stores the access token encrypted in the session cookie (until logged out). The access token allows the app to act on behalf of the user, e. g. to query or edit content:
![Alt text](docs/image_app-screen.png)

## Run examples
Clone the repo and cd to it

### Google as OAuth Provider
create a client here: https://console.cloud.google.com/apis/credentials/oauthclient

create a .env file:
```env
GOOGLE_CLIENT_ID=<your_key>
GOOGLE_CLIENT_SECRET=<your_secret>
```

```bash
uvicorn main_google_login:app --port 8001 --host 127.0.0.1
```

### OSW/OSL mediawiki as OAuth Provider
create a client here (example): https://your.domain.com/wiki/Special:OAuthConsumerRegistration/propose

powershell:
```powershell
$env:OAUTH_CLIENT_ID = '...'; $env:OAUTH_CLIENT_SECRET = '...'; $env:APP_SESSION_SECRET = '!secret';$env:APP_JWT_KEY = '74738ff5536759589aee98fffdcd1876'; $env:APP_JWE_KEY = '74738ff5536759589aee98fffdcd1877'; $env:OSW_SERVER = 'https://your.domain.com'; $env:APP_HOST = 'localhost'; $env:APP_PORT = '5454'; uvicorn main_osw_login:app --port 5454 --host 'localhost'
```

bash:
```bash
export OAUTH_CLIENT_ID = '...'; export OAUTH_CLIENT_SECRET = '...'; export APP_SESSION_SECRET = '!secret'; export APP_JWT_KEY = '74738ff5536759589aee98fffdcd1876'; export APP_JWE_KEY = '74738ff5536759589aee98fffdcd1877'; export OSW_SERVER = 'https://your.domain.com'; export APP_HOST = 'localhost'; export APP_PORT = '5454'; uvicorn main_osw_login:app --port 5454 --host 'localhost'
```

## Further reading:

* https://panel.holoviz.org/how_to/integrations/FastAPI.html
* https://github.com/authlib/demo-oauth-client/tree/master/fastapi-google-login
* https://github.com/authlib/demo-oauth-client/blob/master/fastapi-twitter-login/app.py
* https://docs.authlib.org/en/latest/jose/
* https://github.com/lepture/authlib/blob/master/tests/jose/test_jwe.py