import time
import json
import requests
from rich import print
from discord_webhook import DiscordWebhook, DiscordEmbed

with open('config.json') as f:
    config = json.load(f)
webhook_url = config.get('webhook')
cookie = config.get('cookie')


def tprint(text: str) -> None:
    now = time.strftime('%r')
    print(f"[bold grey53][{now}] <>[/] {text}")

def get_csrf(cookie) -> str:
    return requests.post('https://auth.roblox.com/v2/logout', headers={'cookie': '.ROBLOSECURITY='+cookie}).headers['x-csrf-token']

def get_thumbnail(item_id) -> str:
    url = f'https://thumbnails.roblox.com/v1/assets?assetIds={item_id}&size=420x420&format=Png'
    return requests.get(url).json()['data'][0]['imageUrl']

def get_items() -> list:
    url = 'https://catalog.roblox.com/v1/search/items?category=Accessories&includeNotForSale=true&limit=120&salesTypeFilter=1&sortType=3&subcategory=Accessories'
    return requests.get(url).json()['data']


def get_new(current, old) -> list:
    new = [i for i in current if i not in old]

    if not new:
        tprint('[red3]nothing[/] new')
        return old
    
    tprint(f'[dark_violet]found[/] {len(new)} new items')
    return new


def get_item_info(items: list) -> list:
    payload = {'items': items}

    headers = {
        'cookie': f'.ROBLOSECURITY={cookie};',
        'x-csrf-token': get_csrf(cookie)
        }
    
    details = requests.post(
        'https://catalog.roblox.com/v1/catalog/items/details',
        json=payload,
        headers=headers
        )
    
    return details.json()['data']


def webhook(i) -> None:
    tprint(f"posting webhook for [khaki3]{i['name']}[/]")

    embed = DiscordEmbed(
        title=i['name'],
        url=f"https://www.roblox.com/catalog/{i['id']}",
        color=0x549454
        )
    embed.add_embed_field(name='Price', value=i.get('price', 'Offsale'), inline=True)
    embed.add_embed_field(name='Creator', value=i['creatorName'], inline=True)
    embed.add_embed_field(name='Description', value=f"```{i['description']}```", inline=False)
    embed.set_thumbnail(get_thumbnail(i['id']))

    wh = DiscordWebhook(
        url=webhook_url,
        username='new UGC item',
        rate_limit_retry=True
        )
    wh.add_embed(embed)
    wh.execute()
        
                        

def main() -> None:
    items = get_items()
    tprint(f'loaded {len(items)} items')
    
    while True:
        tprint('looking for new items...')
        items = get_new(get_items(), items)
        
        if len(items) < 100:
            tprint('getting item info')
            item_info = get_item_info(items)

            for item in item_info:
                webhook(item)

        time.sleep(15)

if __name__ == '__main__':
    main()
