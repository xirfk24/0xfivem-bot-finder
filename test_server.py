import httpx
import asyncio

async def test_server(address):
    url = f'http://{address}/players.json'
    print(f'\nTesting: {url}')
    print('='*60)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers={'User-Agent': 'CitizenFX/1'})
            print(f'[OK] Status: {res.status_code}')

            data = res.json()
            print(f'[OK] Players found: {len(data)}')

            if len(data) > 0:
                print(f'\nSample player data:')
                print(data[0])

            return True

    except httpx.TimeoutException:
        print('[ERROR] Connection timeout (server tidak respond)')
        return False
    except httpx.ConnectError:
        print('[ERROR] Cannot connect (server offline atau IP salah)')
        return False
    except Exception as e:
        print(f'[ERROR] {type(e).__name__} - {e}')
        return False

async def main():
    # Test beberapa server
    servers = [
        ('31.58.143.167:30120', 'INDOPRIDE'),
        ('104.234.180.56:30120', 'TRIAD'),
        ('49.128.187.110:30120', 'NUSAV'),
    ]

    print('\n[*] Testing FiveM Servers...\n')

    for address, name in servers:
        print(f'\n[*] {name}')
        await test_server(address)
        print()

if __name__ == '__main__':
    asyncio.run(main())
