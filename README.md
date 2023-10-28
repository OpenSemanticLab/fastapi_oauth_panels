# FastAPI OAuth Panels

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
$env:OAUTH_CLIENT_ID = '...'; $env:OAUTH_CLIENT_SECRET = '...'; $env:OSW_SERVER = 'https://your.domain.com'; $env:APP_HOST = 'localhost'; $env:APP_PORT = '5454'; uvicorn main_osw_login:app --port 5454 --host 'localhost'
```

bash:
```bash
export OAUTH_CLIENT_ID = '...'; export OAUTH_CLIENT_SECRET = '...'; export OSW_SERVER = 'https://your.domain.com'; export APP_HOST = 'localhost'; export APP_PORT = '5454'; uvicorn main_osw_login:app --port 5454 --host 'localhost'
```

## Further reading:

* https://panel.holoviz.org/how_to/integrations/FastAPI.html
* https://github.com/authlib/demo-oauth-client/tree/master/fastapi-google-login
* https://github.com/authlib/demo-oauth-client/blob/master/fastapi-twitter-login/app.py