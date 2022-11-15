import asyncio

from src.big_mac_application import BigMacApplication


async def run():
    await BigMacApplication.run()


if __name__ == '__main__':
    asyncio.run(run())
