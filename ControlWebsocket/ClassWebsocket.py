from fastapi import WebSocketDisconnect
from ControlWebsocket.ConnectServer import ConnectionManager
from  Commands.Commands import Commands
manager = ConnectionManager()   

class RotasWebsocket():
  
    @classmethod
    async def websocket_endpoint(self, websocket, client_id):

        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.send_personal_message(f"You wrote: {data}", websocket)
                await manager.broadcast(f"Client #{client_id} says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"Client #{client_id} left the chat")
    
    @classmethod
    async def raspberry(self, websocket, client_id):
     
        await manager.connect(websocket)
        try:
            while True:
                receive_front = await websocket.receive_text()
                await manager.send_personal_message(f"You wrote: {receive_front}", websocket)
                #data = Commands.cli(receive_front)
                Commands.telnetCommands()
                await manager.broadcast(f"Client #{client_id} says: {receive_front}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"Client #{client_id} foi desconectado")