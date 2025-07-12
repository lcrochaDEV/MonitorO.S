from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from ControlWebsocket.ClassWebsocket import RotasWebsocket
from ControlRequest.ClassRequest import Rotas
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

class Itens(BaseModel):
    host: str 
    port: int 
    user: str
    password: str
    commands: list

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/ont121w")
def methodGet(itens: Itens):
   return Rotas.methodGet(itens)


# SETOR WEBSOCKET
@app.get("/home")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocketServer(websocket:WebSocket, client_id: int):
    return await RotasWebsocket.websocket_endpoint(websocket, client_id)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/raspberry")
async def get():
    return HTMLResponse(raspberry)

@app.websocket("/raspberry/{client_id}")
async def websocketServer(websocket:WebSocket, client_id: int):
    return await RotasWebsocket.raspberry(websocket, client_id)

raspberry = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat Raspbarry PI</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/raspberry/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""