
#import asyncio
import ddaio as asyncio


async def f2():

    print("f2.enter")

    host, port = "127.0.0.1", 65432

    print("f2.wait for connection")
    reader, writer = await asyncio.open_connection(host, port)

    print("f2.wait for write complete")
    writer.write("35".encode())
    await writer.drain()

    print("f2.wait for result")
    result = await reader.read(32)
    print(f"f2.result={result}")

    print("f2.exit")
    writer.close()

    return "f2.return"


async def f1():
    print("f1.enter")
    result = await f2()
    print(f"f1.result={result}")
    print("f1.exit")


async def f3():

    print("f3.enter")

    host, port = "127.0.0.1", 65432

    print("f3.wait for connection")
    reader, writer = await asyncio.open_connection(host, port)

    print("f3.wait for write complete")
    writer.write("36".encode())
    await writer.drain()

    print("f3.wait for result")
    result = await reader.read(32)
    print(f"f3.result={result}")

    print("f3.exit")

    return "f3.return"


async def j1():
    print("j1.body")


async def main():
    await asyncio.gather(f2(), f3(), j1())


asyncio.run(main())

