import json
import sqlite3
import discord
import interactions
import requests
import requests_cache
from discord.ext import commands
from interactions import (Button, ButtonStyle, OptionType, SlashContext, ActionRow, StringSelectMenu, Embed, listen, slash_command, slash_option)
from interactions.api.events import Component
from interactions.ext.paginators import Paginator
from datetime import datetime, timezone
from dateutil import parser
import traceback
from interactions import slash_command, SlashContext, Modal, ShortText, ParagraphText
import time

# todo: faire while currentwar == inwar ... et pereil pour les autre status

conn = sqlite3.connect('CocPlayer.db') # connection a la base de donnée
cursor = conn.cursor() # creation d'une variable pour interagire avec la base de donnée 


TOKEN = "MTExODUzODE2NDI2OTc1MjMyMA.G9au5g.hReBnZrtyN09Cf0oam5cnzqdj4zhNf64TYa9f8"
intents = discord.Intents.default() # permitions du bot 
intents.message_content = True
intents.presences = True
intents.members = True
bot = interactions.Client(token=TOKEN) # crée le bot

GDCBotheader = {
    'authorization' : 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImMzYzAzNDE0LTcyYTQtNDYxZC04YTA1LTA4NTE5NjIzM2ZmNSIsImlhdCI6MTY4Njc2OTk1Niwic3ViIjoiZGV2ZWxvcGVyLzc4ZjdjMzM2LWM2NjUtYzdmYi0xYzhkLTE0YjlhZTY4NjEwMiIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjgxLjY0LjI1NS4xMTkiXSwidHlwZSI6ImNsaWVudCJ9XX0._YGz_-sXj7XvIDH9sM9KqggUVK9VpkwKaYbk87VESOH3WAfMWoOOXkVmvimNrVs-REoSyveWaEjvx5M3S6BAPQ'
} # header pour l'api de clash of clan


################################################
#
#       message when the bot is ready
#
################################################

@listen()
async def on_ready(): # quand le bod est pret 
    print(f'{bot.user} est en marche') #afficher ceci dans le terminal
    
###############################################



#       search command



###############################################

@slash_command(name = 'recherchejoueur', description = "rechercher des joueur selon leurs stats") # on crée une commande et on initialiser sont nom et sa description 
async def rechercheJoueur(ctx): # la fonction qui est rattacher a cette commande 
    components: list[ActionRow] = [ActionRow(Button(style=ButtonStyle.BLURPLE, label='les joueurs ayant le plus de trophée', custom_id="trophy", ), Button(style=ButtonStyle.BLURPLE, label='les plus actifs dans les jeux de clans', custom_id="jdc"), Button(style=ButtonStyle.BLURPLE, label='les joueur dans un clan français ayant donné le plus de troupes', custom_id="don"))] #on crée la partie interactive du message 
    await ctx.send('selectionner les statistiques que vous désirer' , components=components,) # on definis le contenue du message et on rattache la partie interactive du message 


################################################
#
#       currentwar commands
#
################################################


@slash_command(name='gdc', description="visualiser la gdc dun clan")
@slash_option(name='id', description='le tag du clan', required=True, opt_type=OptionType.STRING)
async def gdc(ctx : SlashContext, id):
    channel = ctx.channel
    id=id[1:]

    try:
        url = f"https://api.clashofclans.com/v1/clans/%23{id}/currentwar"
        response = requests.get(url, headers=GDCBotheader)
        currentwar = response.json()  
        currentwar = json.dumps(currentwar)
        currentwar = json.loads(currentwar)
        starTime = currentwar['startTime']
        starTime = parser.parse(starTime)
        time_difference = starTime  -  datetime.now(timezone.utc)
        hours = time_difference.seconds // 3600 
        minutes = (time_difference.seconds % 3600) // 60
        clanInfo = currentwar['clan']
        clanMemberInfo = clanInfo['members']
        clanMemberInfo = sorted(clanMemberInfo, key= lambda x : x['mapPosition'])
        opponentInfo = currentwar['opponent']
        opponentMemberInfo = opponentInfo['members']
        opponentMemberInfo = sorted(opponentMemberInfo, key= lambda x : x['mapPosition'])
        embed = Embed(title = f"**{clanInfo['name']}   {clanInfo['stars']}**          vs           {opponentInfo['stars']}   {opponentInfo['name']}" if float(clanInfo['destructionPercentage']) > float(opponentInfo['destructionPercentage']) else f"{clanInfo['name']} {clanInfo['stars']}   vs   **{opponentInfo['stars']}   {opponentInfo['name']}**", color=interactions.Color.from_rgb(255, 128, 0))
        embed.set_thumbnail(url=clanInfo['badgeUrls']['small'])
        embed.add_field(name=f"pourcentage de destruction : {clanInfo['destructionPercentage']}%    |     {opponentInfo['destructionPercentage']}%", value=f"**attaques : {clanInfo['attacks']}    |     {opponentInfo['attacks']}" + f"\nla guerre se termine dans : {int(hours)} heures et {int(minutes)} minutes**" if currentwar['state'] == 'inWar' else (f"\n**la guerre commence dans : {int(hours)} heures et {int(minutes)} minutes**" if currentwar['state'] == 'preparation'else 'la guerre est terminé !'),  inline=False)
        message = await ctx.send(embed=embed)
        print(int(currentwar['teamSize']/5))
        while currentwar['state'] == 'preparation':
            time_difference = starTime  -  datetime.now(timezone.utc)
            hours = time_difference.seconds // 3600 
            minutes = (time_difference.seconds % 3600) // 60
            preparationEmbed = Embed(title = f"{clanInfo['name']}   {clanInfo['stars']}          vs           {opponentInfo['stars']}   {opponentInfo['name']}", color=interactions.Color.from_rgb(255, 128, 0))
            preparationEmbed.set_thumbnail(url=clanInfo['badgeUrls']['small'])
            preparationEmbed.add_field(name=f"pourcentage de destruction : {clanInfo['destructionPercentage']}%    |     {opponentInfo['destructionPercentage']}%", value=f"**attaques : {clanInfo['attacks']}    |     {opponentInfo['attacks']}" + f"\nla guerre commence dans : {int(hours)} heures et {int(minutes)} minutes**",  inline=False)
            await ctx.edit(message=message,embed=preparationEmbed)
            time.sleep(1)
        for a in range(int(currentwar['teamSize']/5)):
            clanValue=""
            opponentValue =""
            embeds = Embed(color=interactions.Color.from_rgb(255, 128, 0))
            for i in range(5):
                i = i + a * 5
                try:
                    for z in range(len(opponentMemberInfo)):
                        if opponentMemberInfo[z]['tag'] == clanMemberInfo[i]['bestOpponentAttack']['attackerTag']:
                            opponentMemberInfodef = opponentMemberInfo[z]['mapPosition']
                            opponentMemberInfodefName = opponentMemberInfo[z]['name']
                            break
                    try:
                        clanValue = clanValue + "**{}. {}** {}  {} \n\n".format(
                            clanMemberInfo[i]['mapPosition'],
                            clanMemberInfo[i]['name'],
                            ("" if len(clanMemberInfo[i]['attacks']) == 2 else ":crossed_swords:" ),
                            "{}. {} :star::star::star:".format(
                                opponentMemberInfodef,
                                opponentMemberInfodefName
                            ) if clanMemberInfo[i]['bestOpponentAttack']['stars'] == 3 else (
                                "{}. {} :star::star:".format(
                                    opponentMemberInfodef,
                                    opponentMemberInfodefName
                                ) if clanMemberInfo[i]['bestOpponentAttack']['stars'] == 2 else (
                                    "{}. {} :star:".format(
                                        opponentMemberInfodef,
                                        opponentMemberInfodefName
                                    ) if clanMemberInfo[i]['bestOpponentAttack']['stars'] == 1 else 
                                    "{}. {}: 0 étoile".format(
                                            opponentMemberInfodef,
                                            opponentMemberInfodefName
                                    )
                                )
                            )
                        )
                    except Exception: 
                        clanValue = clanValue + "**{}. {} :crossed_swords::crossed_swords: ** {} \n\n".format(
                            clanMemberInfo[i]['mapPosition'],
                            clanMemberInfo[i]['name'],
                            "{}. {} :star::star::star:".format(
                                opponentMemberInfodef,
                                opponentMemberInfodefName
                            ) if clanMemberInfo[i]['bestOpponentAttack']['stars'] == 3 else (
                                "{}. {} :star::star:".format(
                                    opponentMemberInfodef,
                                    opponentMemberInfodefName
                                ) if clanMemberInfo[i]['bestOpponentAttack']['stars'] == 2 else (
                                    "{}. {} :star:".format(
                                        opponentMemberInfodef,
                                        opponentMemberInfodefName
                                    ) if clanMemberInfo[i]['bestOpponentAttack']['stars'] == 1 else 
                                    "{}. {}: 0 étoile".format(
                                            opponentMemberInfodef,
                                            opponentMemberInfodefName
                                    )
                                )
                            )
                        )
                except Exception:
                    try:
                        clanValue = clanValue + f"**{clanMemberInfo[i]['mapPosition']}. {clanMemberInfo[i]['name']} {'' if len(clanMemberInfo[i]['attacks']) == 2 else ':crossed_swords:' }** n'a pas encore été attaqué\n\n"
                    except Exception:
                        clanValue = clanValue + f"**{clanMemberInfo[i]['mapPosition']}. {clanMemberInfo[i]['name']} :crossed_swords::crossed_swords:** n'a pas encore été attaqué \n\n"

                try:
                    for z in range(len(clanMemberInfo)):
                        if clanMemberInfo[z]['tag'] == opponentMemberInfo[i]['bestOpponentAttack']['attackerTag']:
                            opponentMemberInfodef = clanMemberInfo[z]['mapPosition']
                            opponentMemberInfodefName = clanMemberInfo[z]['name']
                            break
                    try : 
                        opponentValue = opponentValue + " **{}. {} {}** {} \n\n".format(
                            opponentMemberInfo[i]['mapPosition'],
                                opponentMemberInfo[i]['name'], 
                                    ("" if len(opponentMemberInfo[i]['attacks']) == 2 else ":crossed_swords:" ), 
                                "{}. {}: :star::star::star:".format(
                                    opponentMemberInfodef,
                                    opponentMemberInfodefName
                                ) if opponentMemberInfo[i]['bestOpponentAttack']['stars'] == 3 else (
                                    "{}. {}: :star::star:".format(
                                        opponentMemberInfodef,
                                        opponentMemberInfodefName
                                    ) if opponentMemberInfo[i]['bestOpponentAttack']['stars'] == 2 else (
                                        "{}. {}: :star:".format(
                                            opponentMemberInfodef,
                                            opponentMemberInfodefName
                                        ) if opponentMemberInfo[i]['bestOpponentAttack']['stars'] == 1 else
                                        "{}. {}: 0 étoile".format(
                                            opponentMemberInfodef,
                                            opponentMemberInfodefName
                                        )
                                    )
                                )
                            )
                    except Exception: 
                        opponentValue = opponentValue + " **{}. {} :crossed_swords::crossed_swords:** {} \n\n".format(
                            opponentMemberInfo[i]['mapPosition'],
                                opponentMemberInfo[i]['name'], 

                                "{}. {}: :star::star::star:".format(
                                    opponentMemberInfodef,
                                    opponentMemberInfodefName
                                ) if opponentMemberInfo[i]['bestOpponentAttack']['stars'] == 3 else (
                                    "{}. {}: :star::star:".format(
                                        opponentMemberInfodef,
                                        opponentMemberInfodefName
                                    ) if opponentMemberInfo[i]['bestOpponentAttack']['stars'] == 2 else (
                                        "{}. {}: :star:".format(
                                            opponentMemberInfodef,
                                            opponentMemberInfodefName
                                        ) if opponentMemberInfo[i]['bestOpponentAttack']['stars'] == 1 else
                                        "{}. {}: 0 étoile".format(
                                            opponentMemberInfodef,
                                            opponentMemberInfodefName
                                        )
                                    )
                                )
                            )
                except Exception : 
                    try:
                        opponentValue = opponentValue + f" **{opponentMemberInfo[i]['mapPosition']}. {opponentMemberInfo[i]['name']} {'' if len(opponentMemberInfo[i]['attacks']) == 2 else ':crossed_swords:' }** n'a pas encore été attaqué\n\n"
                    except Exception:
                        opponentValue = opponentValue + f" **{opponentMemberInfo[i]['mapPosition']}. {opponentMemberInfo[i]['name']} :crossed_swords::crossed_swords:** n'a pas encore été attaqué\n\n"
            embeds.add_field(name='votre clan' , value=clanValue , inline=True)
            print(clanValue) 
            embeds.add_field(name='le clan adverse', value=opponentValue, inline=True )
            print(opponentValue)
            message =  await channel.send(embed=embeds)
            message.edit(content='ptn yes')


            
            
                           
    except Exception:
        traceback.print_exc()
        await ctx.send('fesfefsf')



@slash_command(name = 'pa', description = "afficher les stats d'un joueur")
async def _p(ctx: SlashContext):
    message = await ctx.send(embeds=Embed(title='????'))
    await ctx.edit(message=message, embed=Embed(title='////////////////////////////////'))
################################################
#
#        coc profile command
#
################################################


@slash_command(name = 'p', description = "afficher les stats d'un joueur")
@slash_option(name = 'tag', description="tag du joueur", required=True, opt_type=OptionType.STRING )
async def p(ctx : SlashContext, tag : str) :
    try: 
        player_id = tag[1:]
        url = f"https://api.clashofclans.com/v1/players/%23{player_id}"
        response = requests.get(url, headers=GDCBotheader)
        user_json = response.json()  
        user_json = json.dumps(user_json)
        user_json = json.loads(user_json)      
        # embed message
        embed_profile = discord.Embed(title=user_json['name'], description="profil d'"+ user_json['name'], color=discord.Color.random())
        embed_profile.add_field(name="Champ 1", value="Valeur 1", inline=False)
        embed_profile.add_field(name="Champ 2", value="Valeur 2", inline=False) 
        embeds = embed_profile.to_dict()
        await ctx.send(embeds=embeds)
    except KeyError:
        await ctx.send("Erreur : tag du joueur invalide.")
    except Exception: # si il y a une erreur qui n'est pas mentionner plus haut 
        await ctx.send("Erreur : veuillez réessayer plus tard.")


################################################
#
#       if button click                                                                               
#
################################################


@listen()
async def on_component(event: Component):
    ctx = event.ctx    
    if event.ctx.custom_id == 'trophy':
        embeds = []
        for i in range(25):
            cursor.execute('SELECT * FROM Player ORDER BY trophée DESC, LvlDuClan ASC LIMIT 5 OFFSET ?', (0+5*i,))
            resultat = cursor.fetchall()
            embeds_ = Embed(title='Les joueur dans un clan français ayant le plus de trophée') 
            for line in resultat:
                embed = f'hdv : **{line[0]}**  |  psedo : **{line[1]}**  |  Tag du joueur : **{line[2]}**  |  nombre de trophée : **{line[3]}**  |  Niveau : **{line[4]}**  |  étoiles de guerre : **{line[5]}**  |  préference de guerre : **{line[6]}**  |  capacité de renfort donné : **{line[7]}**  |  point aux jeux de clan totale : **{line[8]}**  |  badge1 : **{line[9]}**  |  badge2 : **{line[10]}**  |  badge3 : **{line[11]}**.'
                embeds_.add_field(name=line[1], value=embed) # type: ignore
            embeds.append(embeds_)   
        
        paginator = Paginator.create_from_embeds(bot, *embeds)
        paginator.show_select_menu = True
        
        await paginator.send(ctx)

    elif event.ctx.custom_id == 'jdc':
        embeds = []
        for i in range(25):
            cursor.execute('SELECT * FROM Player ORDER BY pointsJDCTotal DESC, LvlDuClan ASC LIMIT 5 OFFSET ?', (0+5*i,))
            resultat = cursor.fetchall()
            embeds_ = Embed(title='Les joueur dans un clan français ayant fait le plus de point au jeux de clan') 
            for line in resultat:
                embed = f'hdv : **{line[0]}**  |  psedo : **{line[1]}**  |  Tag du joueur : **{line[2]}**  |  nombre de trophée : **{line[3]}**  |  Niveau : **{line[4]}**  |  étoiles de guerre : **{line[5]}**  |  préference de guerre : **{line[6]}**  |  capacité de renfort donné : **{line[7]}**  |  point aux jeux de clan totale : **{line[8]}**  |  badge1 : **{line[9]}**  |  badge2 : **{line[10]}**  |  badge3 : **{line[11]}**.'
                embeds_.add_field(name=line[1], value=embed) # type: ignore
            embeds.append(embeds_)   
        
        paginator = Paginator.create_from_embeds(bot, *embeds)
        paginator.show_select_menu = True
        
        await paginator.send(ctx)

    elif event.ctx.custom_id == 'don':
        embeds = []
        for i in range(25):
            cursor.execute('SELECT * FROM Player ORDER BY donnationTotal DESC, LvlDuClan ASC LIMIT 5 OFFSET ?', (0+5*i,))
            resultat = cursor.fetchall()
            embeds_ = Embed(title='Les joueur dans un clan français ayant donnée de troupes') 
            for line in resultat:
                embed = f'hdv : **{line[0]}**  |  psedo : **{line[1]}**  |  Tag du joueur : **{line[2]}**  |  nombre de trophée : **{line[3]}**  |  Niveau : **{line[4]}**  |  étoiles de guerre : **{line[5]}**  |  préference de guerre : **{line[6]}**  |  capacité de renfort donné : **{line[7]}**  |  point aux jeux de clan totale : **{line[8]}**  |  badge1 : **{line[9]}**  |  badge2 : **{line[10]}**  |  badge3 : **{line[11]}**.'
                embeds_.add_field(name=line[1], value=embed) # type: ignore
            embeds.append(embeds_)   
        
        paginator = Paginator.create_from_embeds(bot, *embeds)
        paginator.show_select_menu = True
        
        await paginator.send(ctx)


################################################
#
#       ldc command                                                                              
#
################################################


def ldcsetup(ctx): 
    ldc(ctx)
    return ctx     


# ldc preview in one select channel update if sth is new
def ldc(user_message, war_tag_id, war_tags):
    return
    #init_ldc(user_message)
    #ldc_find_war_tag_id(war_tags, war_tag_id)
# ldc preview in one select channel update if sth is new


async def init_ldc(user_message):
    clan_id = str(user_message[10:])
    clan_api_id = str(user_message[11:])
    url = "https://api.clashofclans.com/v1/clans/%23"+ str(clan_api_id) + "/currentwar/leaguegroup" 
    response = requests.get(url, headers=GDCBotheader)
    setup1 = response.json()
    setup_json = json.dumps(setup1)
    war_tags = json.loads(setup_json)
    return war_tags


def id(user_message):
    clan_id = str(user_message[10:])
    return clan_id


def ldc_udate_data(war_tag_id):
    requests_cache.install_cache('api_cache')
    url = "https://api.clashofclans.com/v1/clanwarleagues/wars/%23" + war_tag_id
    response = requests.get(url, headers=GDCBotheader)
    if not response.from_cache:
        requests_cache.cache_response(response)
    previous_response = requests_cache.get_cache().get(url)
    if previous_response is not None and previous_response.content != response.content:
        ldc_info = requests.get(url, headers=GDCBotheader)
        ldc_info = response.json()
        ldc_info = json.dumps(ldc_info)
        ldc_info = json.loads(ldc_info)
        if float(ldc_info['clan']['destructionPercentage']) < float(ldc_info['opponent']['destructionPercentage']):
            title = ldc_info['clan']['name'] + '  ' +ldc_info['clan']['stars'] + '   vs   ' + '**' + ldc_info['opponent']['stars'] + '**' + '   **' + ldc_info['opponent']['name'] + '**'
        else: 
            title = '**' +ldc_info['clan']['name'] + '**' + '  ' +'**' +ldc_info['clan']['stars']+ '**' + '   vs   ' +  ldc_info['opponent']['stars']  +'  '+  ldc_info['opponent']['name'] 
        embed_profile = discord.Embed(title=title, description=None, color=discord.Color.random())
        embed_profile.add_field(name="Champ 1", value="Valeur 1", inline=True)
        embed_profile.add_field(name="Champ 2", value="Valeur 2", inline=True) 
        return embed_profile
    

# ldc preview in one select channel update if sth is new
async def ldc_find_war_tag_id(war_tags, clan_id):
    for round in war_tags['rounds']:
        for war_tags in round['warTags']:
            war_tag_id = war_tags
            war_tag_id = str(war_tag_id[1:])
            print(war_tags)
            url = "https://api.clashofclans.com/v1/clanwarleagues/wars/%23" + war_tag_id
            response = requests.get(url, headers=GDCBotheader)
            setup2 = response.json()
            setup2_ = json.dumps(setup2)
            setup2_json = json.loads(setup2_)
            if war_tags == '#0':
                break
            elif (setup2_json['clan']['tag'] == clan_id or setup2_json['opponent']['tag'] == clan_id) and setup2_json['state'] == 'inWar':
                print('real id is: '+ war_tag_id)
            return war_tag_id
                        

bot.start() 
