from fastapi import WebSocketDisconnect
from ControlRequest.ConnectServer import ConnectionManager


manager = ConnectionManager()   
class Rotas():
  
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
    