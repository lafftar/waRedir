import asyncio
from typing import Literal

import aiohttp
import discord
import httpx

from utils.custom_logger import logger
from utils.webhook import send_webhook


async def set_dns(subdomain: Literal['zalando'] = 'zalando'):
    if subdomain == 'zalando':
        user = '3QKnpMYkrH0qp3PI'
        passwd = 'x9O5QY83J68JUDhM'
    else:
        raise Exception(f'{subdomain} not recognized.')

    client = httpx.AsyncClient()
    try:
        # get current ip
        req = httpx.Request(
            method='GET',
            url='http://api.ipify.org'
        )
        ip = await client.send(req)
        ip = ip.text.strip()

        # update dns
        req = httpx.Request(
            method='POST',
            url=f'https://{user}:{passwd}'
                '@domains.google.com/nic/update'
                f'?hostname={subdomain}.winx4.net&myip={ip}',
            headers={
                'host': 'domains.google.com',
                'Authorization': 'Basic base64-encoded-auth-string User-Agent: Chrome/41.0 tibabalase@gmail.com'
            }
        )
        resp = await client.send(req)
        current_ip = resp.text.split()[1]
        subdomain = subdomain.upper()
        logger().info(f'{subdomain} has been hosted on {current_ip}')
        async with aiohttp.ClientSession() as wc:
            await (
                send_webhook(
                    embed_dict={'Message': f'**{subdomain}** has been hosted on **{current_ip}**'},
                    webhook_url='https://discord.com/api/webhooks/963134205024411668/'
                                'l14059NiFHUE_z5dlhi31GPluBt8OatvwhJzMLmbEfWN13v0L_nrtNrSJzIXX1YITZsA',
                    webhook_client=wc,
                    color=discord.Color.teal())
            )
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(set_dns(subdomain='zalando'))
