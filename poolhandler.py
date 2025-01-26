from typing import Dict, Optional, Tuple

import aiofiles
import aiomysql
import asyncio
import cryptjson
import re

class Pool:
	def __init__(self, client_id: str, loop: Optional[asyncio.AbstractEventLoop] = None):
		self.pool: aiomysql.Pool = None
		self.cursor: aiomysql.Cursor = None

		self.maps: Dict = {}

		self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
		self.loop.create_task(self.start())

		self.client_id: str = client_id

	async def acquire(self) -> aiomysql.Connection:
		return await self.pool.acquire()

	async def release(self, conn: aiomysql.Connection):
		await self.pool.release(conn)

	async def start(self):
		try:
			self.pool = await aiomysql.create_pool(host="remotemysql.com",
				user="iig9ez4StJ", password="v0TNEk0vsI",
				db="iig9ez4StJ", loop=self.loop,
				autocommit=True
			)
			print("[Database] Connected")
		except Exception:
			print("[Database] Connection failed")

	async def exec(
		self,
		code: str = "",
		info: str = "",
		author: str = "",
		delete: bool = False
	):
		self.maps = {}

		async with self.pool.acquire() as conn:
			async with conn.cursor() as cur:
				query, insert = "", False

				await cur.execute(
					"SELECT `json` FROM `maps` WHERE `id`='{}'"
					.format(self.client_id)
				)
				selected = await cur.fetchone()
				if not selected:
					if os.path.isfile("./maps.json"):
						async with aiofiles.open("./maps.json", "rb") as f:
							data = cryptjson.text_decode(await f.read()).decode()
							insert = True
				else:
					data = cryptjson.text_decode(selected[0]).decode()

				sep = data.split("#")
				for s in sep:
					search = re.search(r"(.*?):(.*)", s)
					if search is not None:
						self.maps[search.group(1)] = search.group(2)

				if code:
					query = "UPDATE `maps` SET `json`='{}' WHERE `id`='{}'"

					if delete:
						for _code in code.split(","):
							del self.maps[_code]

						def finish():
							print(f"[Database] {code} map deleted by {author}")
					else:
						self.maps[code] = info

						def finish():
							print(f"[Database] {code} map added by {author}")
				else:
					def finish():
						print(f"[Database] Maps storage loaded. Total length: {len(self.maps)}")

				if insert:
					query = "INSERT INTO `maps` (`id`, `json`) VALUES ('{}', '{}')"

				if query:
					data = b"#".join([code.encode() + b":" + info.encode() for code, info in self.maps.items()])
					values = (cryptjson.text_encode(data).decode(), self.client_id)
					if insert:
						values = values[::-1]
					await cur.execute(query.format(*values))

				finish()