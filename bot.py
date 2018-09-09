import discord
import config
import requests
from discord.ext import commands
from prawmod import bot as praw
import cssutils
from PIL import Image
from io import BytesIO
from urllib.parse import quote
import tinycss2
bot = commands.Bot(command_prefix='$')
apiKey = 'acc_3c625a5fe599aee'
apiSecret = '2b0f68ca176c0ce6f666a1594be1fbf6'
@bot.command()
async def resize(ctx, arg1):
    url = arg1
    coord = requests.get('https://api.imagga.com/v1/croppings?url=' + quote(url) + '&resolution=300x450&no_scaling=0',
                         auth=(apiKey, apiSecret)).json()['results'][0]['croppings'][0]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    print(image.size)
    if image.size != (312,468):
        image = image.crop((coord['x1'], coord['y1'], coord['x2'], coord['y2']))
        image.thumbnail((312,468), Image.ANTIALIAS)
    image.save('image.png')
    with open('image.png', 'rb') as f:
        await ctx.send(file=discord.File(f))

@bot.command()
async def sidebar(ctx):
    stylesheet = cssutils.parseString(praw.subreddit('nbadev').wiki['config/stylesheet'].content_md)
    for rule in stylesheet:
        print(vars(rule))
        if rule.type == rule.STYLE_RULE and rule._selectorList.selectorText == '.side .spacer:nth-of-type(1):before':
            for property in rule.style:
                if property.name == 'content':
                    await ctx.send(property.value)
                    break
# @bot.command()
# async def set(ctx, *, arg1):
#     stylesheet = cssutils.parseString(praw.subreddit('nbadev').wiki['config/stylesheet'].content_md)
#     for rule in stylesheet:
#         if rule.type == rule.STYLE_RULE and rule._selectorList.selectorText == '.side .spacer:nth-of-type(1):before':
#             for property in rule.style:
#                 if property.name == 'content':
#                     property.value = '"'+arg1+'"'
#                     break
#     # stylesheet.deleteRule(0)
#     # style = cssutils.CSSStyleDeclaration()
#     # style['content'] = arg1 # until 0.9.5: setProperty(u'color', u'red')
#     # stylerule = cssutils.CSSStyleRule(selectorText=u'.side .spacer:nth-of-type(1):before', style=style)
#     # stylesheet.add(stylerule)
#     print(type(stylesheet.cssText))
#     praw.subreddit('nbadev').wiki['config/stylesheet'].edit(stylesheet.cssText)
#     await ctx.send('changed css text')
#
@bot.command()
async def set(ctx, *, arg1):
    stylesheet = praw.subreddit('nbadev').wiki['config/stylesheet'].content_md
    lines = stylesheet.splitlines()
    for i,v in enumerate(lines):
        if v.startswith('.side .spacer:nth-of-type(1):before'):
            lines[i+1] = '    content: "'+arg1+'";'
    sheet = ""
    for line in lines:
        sheet+=(line+'\n')
    print(sheet)
    praw.subreddit('nbadev').stylesheet.update(sheet)
    await ctx.send('changed css text')
@bot.command()
async def image(ctx, *, args):
    args = args.split(',')
    url = args[0]
    coord = requests.get('https://api.imagga.com/v1/croppings?url=' + quote(url) + '&resolution=300x450&no_scaling=0',
                         auth=(apiKey, apiSecret)).json()['results'][0]['croppings'][0]
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = image.crop((coord['x1'], coord['y1'], coord['x2'], coord['y2']))
    image.thumbnail((300,450), Image.ANTIALIAS)
    image.save('image.png')
    with open('image.png', 'rb') as f:
        await ctx.send(file=discord.File(f))
        await ctx.send('Are you sure you want to use this image, with text:\n ' + args[1])
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '👌'

    try:
        reaction, user = await bot.wait_for('reaction_add', check=check)
    except Exception as e:
        print(e)
        await ctx.send('something broke')
    else:
        stylesheet = praw.subreddit('nbadev').stylesheet()
        stylesheet.upload('sb','image.png')
        await ctx.send('uploaded image')

bot.run(config.token)

