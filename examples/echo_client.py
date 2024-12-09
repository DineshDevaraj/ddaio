
import time
#import asyncio
import ddaio as asyncio


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


async def tcp_echo_client(message):

    reader, writer = await asyncio.open_connection(HOST, PORT)

    max_seconds = 15
    total_request = 0
    seconds_count = 0
    request_per_second = 0
    start_time = time.time()

    while True:

        # print(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        # print(f'Received: {data.decode()!r}')

        current_time = time.time()
        if current_time - start_time >= 1:
            seconds_count += 1
            print(f"{seconds_count} {request_per_second}")
            total_request += request_per_second
            start_time = current_time
            request_per_second = 0
            if seconds_count == max_seconds:
                break

        request_per_second += 1

    print(f"Average RPS: {total_request // seconds_count}")
    writer.close()


asyncio.run(tcp_echo_client('Hello World!'))

