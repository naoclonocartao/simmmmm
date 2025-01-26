import aiohttp

async def solve_captcha(b: bytes):
	async with aiohttp.ClientSession() as session:
		try:
			async with session.post(
				"https://tfmcaptchasolver.herokuapp.com/solve_captcha", data={"captcha": b}
			) as response:
				data = await response.json()
				if data:
					result = data.get("result")
		except aiohttp.client_exceptions.ClientConnectorError:
			result = None
	return result