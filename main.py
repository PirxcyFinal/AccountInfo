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
  async def post(url, data=None, headers=None):
    async with aiohttp.ClientSession() as session:
      async with session.request(
        url,
        method="POST",
        data=data,
        headers=headers,
      ) as r:
        return r.json()

class epicgames:
  async def get_access_token(code: str):
    data = await web.post(
      url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
      data=f"grant_type=authorization_code&code={code}",
      headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=",
      }
    )
    return data['access_token']
  
  async def code_to_auths(code: str):
    data = await epicgames.get_access_token(code=code)
    auths = web.post(
      f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{data['account_id']}/deviceAuth",
      headers={
        "Authorization": f"Bearer {data['access_token']}"
      }
    )
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

async def send_error(ctx, error, full_error):
  embed=discord.Embed(
    title="An Error Occured Executing A Task.", 
    description=f"```py\n{full_error}\n{error}\n```"
  )
  return await ctx.respond(embed=embed)

@app.route('/')
async def index(request):
  return sanic.response.json({'status': 'online'})

@bot.event
async def on_ready():
  await app.create_server(
    host='0.0.0.0',
    port=os.environ['MADEBYPIRXCY'],
    return_asyncio_server=True,
  )

@bot.command()
async def login(ctx):
  try:
    embed = discord.Embed(
      title="Please Enter a Valid Exchange Code", url="https://rebrand.ly/authcode"
    )
    await ctx.respond(embed=embed)

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
