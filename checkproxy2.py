import asyncio
import httpx
from httpx_socks import AsyncProxyTransport
from tqdm import tqdm

def load_proxies(filename):
    with open(filename, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

async def check_proxy(proxy, progress_bar):
    url = 'http://www.google.com'
    proxy_parts = proxy.split(":")
    ip, port = proxy_parts[0], int(proxy_parts[1])

    working_schemes = []  # Store working schemes for this proxy

    for scheme in ["http", "https", "socks4", "socks5"]:
        proxy_url = f"{scheme}://{ip}:{port}"

        try:
            if scheme in ['http', 'https']:
                async with httpx.AsyncClient(proxies=proxy_url, timeout=500) as client:
                    response = await client.get(url)
            elif scheme in ['socks4', 'socks5']:
                transport = AsyncProxyTransport.from_url(proxy_url)
                async with httpx.AsyncClient(transport=transport, timeout=500) as client:
                    response = await client.get(url)

            if response.status_code == 200:
                working_schemes.append(scheme)  # Add working scheme to the list
        except Exception as e:
            pass

    progress_bar.update(1)
    return proxy, working_schemes  # Return proxy and its working schemes

async def main():
    proxies = load_proxies('proxy_list.txt')
    progress_bar = tqdm(total=len(proxies), desc="Đang kiểm tra proxy", ncols=100)

    tasks = [check_proxy(proxy, progress_bar) for proxy in proxies]
    results = await asyncio.gather(*tasks)

    with open('proxytype.txt', 'w') as f:
        for proxy, schemes in results:
            if schemes:  # If at least one scheme worked
                f.write(f"{proxy} - {'/'.join(schemes)}\n")  # Write proxy and schemes
            else:
                f.write(f"{proxy} - Invalid\n")  # Mark invalid proxies

    progress_bar.close()

asyncio.run(main())
