import discord
import os
import sanic
import json
import aiohttp
import traceback

from discord.ext import commands
app = sanic.Sanic(
  "AccountInfo"
)
bot = commands.Bot(
  command_prefix="!"
)

filename = "accounts.json"

class web:
  async def post(url: str, data=None, headers=None):
    async with aiohttp.ClientSession() as session:
      async with session.request(
        method="POST",        
        url=url,
        data=data,
        headers=headers
      ) as r:
        data = await r.text()
        try:
          return json.loads(data)
        except:
          return data
      
  async def get(url: str, data=None, headers=None):
    async with aiohttp.ClientSession() as session:
      async with session.request(
        method="GET",        
        url=url,
        data=data,
        headers=headers
      ) as r:
        data = await r.text()
        try:
          return json.loads(data)   
        except:
          return data
    
class epicgames:
  async def code_to_data(code: str):
    data = await web.post(
      url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
      data=f"grant_type=authorization_code&code={code}",
      headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=",
      }
    )
    return data
  
  async def code_to_auths(code: str):
    data = await epicgames.code_to_data(code=code)
    auths = await web.post(
      f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{data['account_id']}/deviceAuth",
      headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {data['access_token']}"
      }
    )
    print(auths)
    auths.pop("created")
    return auths

def add_to_auths(info):
  with open(filename) as f:
    file = json.load(f)
  file.append(info)
  indented = json.dumps(
    file, 
    indent=2
  )
  with open(filename) as fp:
    json.dump(indented, fp)
  return

async def check_backend():
  status = await web.get(url='https://StoreAccounts.pirxcy1942.repl.co')
  if status  == {'status': 'Online'}:
    return status
  else:
    return False

async def send_error(ctx, error, full_error):
  embed=discord.Embed(
    title="An Error Occured Executing A Task.", 
    description=f"```py\n{full_error}\n{error}\n```"
  )
  return await ctx.send(embed=embed)

@app.route('/')
async def index(request):
  return sanic.response.json({'status': 'Online'})

@bot.event
async def on_ready():
  await app.create_server(
    host='0.0.0.0',
    port=os.environ['PORT'],
    return_asyncio_server=True,
  )

@bot.command()
async def backend(ctx):
  try:
    status = await check_backend()
    if status == {'status': 'Online'}:
      embed=discord.Embed(
        title="Backend Status.", 
        description=f"```json\n{status}\n```"
      )
      await ctx.send(embed=embed)
    else:
      embed=discord.Embed(
        title="Backend Status.", 
        description=f"```diff\n- Offine\n```"
      )
      await ctx.send(embed=embed)
  except Exception as e:
    await send_error(
      ctx=ctx, 
      error=e, 
      full_error=traceback.format_exc()
    )
  
@bot.command()
async def login(ctx):
  try:
    status = await check_backend()
    if status == {'status': 'Online'}:
      pass
    else:
      embed = discord.Embed(title="Backend Offline, Try again Later.")
      return await ctx.send(embed=embed)
    embed = discord.Embed(
      title="Please Enter a Valid Exchange Code", url="https://rebrand.ly/authcode"
    )
    await ctx.send(embed=embed)

    def check(msg):
      return msg.author == ctx.author and len(msg.content) == 32

    code = await bot.wait_for(
      "message", 
      check=check
    )

    auths = await epicgames.code_to_auths(code=code.content)
    add_to_auths(auths)

  except Exception as e:
    await send_error(
      ctx=ctx, 
      error=e, 
      full_error=traceback.format_exc()
    )

bot.run(os.environ['MADEBYPIRXCY'])
