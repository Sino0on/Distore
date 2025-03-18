import asyncio
from services.translater import Translater


async def main():
    trans = Translater()
    await trans.update_translations()
    # await trans.test_select(lang='ky')

if __name__ == "__main__":
    asyncio.run(main())

