
from abc import abstractmethod
import asyncio

class Output(asyncio.Queue):

    @abstractmethod
    async def put(self, obj):...


class PrintOutput(Output):

    async def put(self, obj):
        print(f'{obj}')

