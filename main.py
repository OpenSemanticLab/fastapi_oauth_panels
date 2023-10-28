import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from sliders.pn_app import createApp

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def bkapp_page(request: Request):
    script = server_document('http://127.0.0.1:5001/app')
    return templates.TemplateResponse("base.html", {"request": request, "script": script})


pn.serve({'/app': createApp},
        port=5001, allow_websocket_origin=["127.0.0.1:8001"],
         address="127.0.0.1", show=False)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8001)