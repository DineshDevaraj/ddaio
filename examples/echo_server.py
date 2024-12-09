
#import asyncio
import ddaio as asyncio


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


async def handle_client(reader, writer):
    while True:
        request = await reader.read(255)
        print(request)
        if not request:
            break
        writer.write(request)
        await writer.drain()


async def run_server():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()


asyncio.run(run_server())

