import aiohttp
import asyncio
import os

groupids = open('groupids.txt', 'r').read().splitlines()

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

async def scrape(gid, session):
    try:
        async with session.get(f'https://groups.roblox.com/v1/groups/{gid}') as response:
            r = await response.json()
            fname = ''.join(x for x in r['name'] if x.lower() in 'abcdefghijklmnopqrstuvwxyz1234567890 ') + f' ({gid})'
            members = r.get('memberCount', '?')
    except Exception as e:
        print(f"Error fetching group {gid}: {e}")
        fname = gid
        members = '?'

    print(f'Started scraping {fname} ({members} members) | {len(groupids)} groups remaining')
    fname = os.path.join(output_dir, f"{fname}.txt")
    cursor = ''

    while True:
        try:
            async with session.get(f'https://groups.roblox.com/v1/groups/{gid}/users?sortOrder=Asc&limit=100&cursor={cursor}') as response:
                r = await response.json()
                users = [f"{x['user']['username']}\n" for x in r.get('data', [])]
                with open(fname, 'a') as f:
                    f.writelines(users)
                cursor = r.get('nextPageCursor')
                if not cursor:
                    break
        except Exception as e:
            print(f"Error fetching users for group {gid}: {e}")
            break

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [scrape(gid, session) for gid in groupids]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
