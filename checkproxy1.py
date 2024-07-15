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

    # Automatically infer scheme
    for scheme in ["http", "https", "socks4", "socks5"]:  # Prioritize common schemes
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
                print(f"Proxy {proxy_url} hoạt động.")
                return proxy_url  # Return full proxy URL
            else:
                print(f"Proxy {proxy_url} không hoạt động (status code: {response.status_code}).")
        except Exception as e:
            print(f"Proxy {proxy_url} không hoạt động (lỗi: {e}).")
            
    # If none of the schemes worked, the proxy is invalid
    progress_bar.update(1)
    return None
    

async def main():
    proxies = load_proxies('proxy_list.txt')
    progress_bar = tqdm(total=len(proxies), desc="Đang kiểm tra proxy", ncols=100)

    tasks = [check_proxy(proxy, progress_bar) for proxy in proxies]
    results = await asyncio.gather(*tasks)
    good_proxies = [proxy for proxy in results if proxy is not None]

    with open('proxygood.txt', 'w') as f:
        for proxy in good_proxies:
            f.write(f"{proxy}\n")

    progress_bar.close()
    
asyncio.run(main())
