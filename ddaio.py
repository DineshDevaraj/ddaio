
import types
import socket
import inspect
import selectors

from collections import deque

default_selector = selectors.DefaultSelector()
Socket = socket.socket


class Future:

    def __init__(self):
        self.task = None
        self.handler = None

    def __await__(self):
        return (yield self)


class Task:

    _task_id = 0

    def __init__(self, coro):

        Task._task_id += 1

        self.task_id = Task._task_id
        self.coro_arg = None
        self.stack = deque()
        self.coro = coro

    def run(self):
        try:
            #print(self.coro.cr_frame)
            result = self.coro.send(self.coro_arg)
            if inspect.iscoroutine(result):
                self.stack.append(self.coro)
                self.coro = result
            elif isinstance(result, Future):
                result.task = self
        except StopIteration:
            if not self.stack:
                raise
            self.coro = self.stack.pop()


class EventLoop:

    _task_dict = {}
    _ready_task = deque()

    @staticmethod
    def add_task(coro):
        task = Task(coro)
        EventLoop._task_dict[task.task_id] = task
        EventLoop._ready_task.append(task)

    @staticmethod
    def run_till_complete():

        while EventLoop._task_dict:

            try:

                if EventLoop._ready_task:
                    task = EventLoop._ready_task.popleft()
                    task.run()
                    continue

                if not len(default_selector.get_map()):
                    """ 
                    All tasks are complete and there are 
                    no sockets to wait for. Hence exit 
                    """
                    break

                event_list = default_selector.select()
                for key, mask in event_list:
                    future: Future = key.data
                    result = future.handler()
                    EventLoop._ready_task.append(future.task)
                    future.task.coro_arg = result

            except StopIteration:
                del(EventLoop._task_dict[task.task_id])


class Writer:

    def __init__(self, socket_inst):
        self.socket_inst: Socket = socket_inst

    def write(self, data: bytes):
        self.socket_inst.sendall(data)

    async def drain(self):
        pass

    def close(self):
        self.socket_inst.close()


class Reader:

    def __init__(self, socket_inst):
        self.socket_inst: Socket = socket_inst

    def handler(self):
        default_selector.unregister(self.socket_inst)
        return self.socket_inst.recv(32)

    @types.coroutine
    def read(self, length):
        future = Future()
        future.target = self
        future.handler = self.handler
        default_selector.register(
            self.socket_inst,
            selectors.EVENT_READ,
            future,
        )
        return (yield future)


async def open_connection(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return Reader(s), Writer(s)


async def _client_handler_def(reader, write):
    pass


class ASocket:

    _client_handler = _client_handler_def

    def __init__(self, socket_inst):
        #print(f"{socket_inst.fileno()=}")
        self.socket_inst = socket_inst
        self.conn = None
        self.addr = None

    @staticmethod
    async def new_connection(coro):
        await coro

    def accept(self):
        self.conn, self.addr = self.socket_inst.accept()
        #print(f"{self.conn.fileno()=}")
        coro = ASocket._client_handler(
            Reader(self.conn),
            Writer(self.conn)
        )
        EventLoop.add_task(ASocket.new_connection(coro))

    def __aenter__(self):
        future = Future()
        future.handler = self.accept
        default_selector.register(
            self.socket_inst,
            selectors.EVENT_READ,
            future
        )
        self.socket_inst.listen()
        return future

    def __aexit__(self, *exception):
        return Future()

    async def serve_forever(self):
        pass

async def start_server(client_handler, host, port):
    ASocket._client_handler = client_handler
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    return ASocket(s)


async def gather(*coro_list):
    for coro in coro_list:
        EventLoop.add_task(coro)
    EventLoop.run_till_complete()


def run(coro):
    EventLoop.add_task(coro)
    EventLoop.run_till_complete()

