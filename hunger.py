import discord,asyncio,random,math,re
import datetime
import sys
from time import sleep
i = discord.Intents.default()
i.members=True
i.guilds = True
f = open("../.tokens").readlines() #array of tokens
client = discord.Client(intents=i)
outChan=None

class weapon:
    strength=0
    name=""
    def __init__(self,s,n):
        self.strength=s
        self.name=n

#TODO add interactivity
#two methods of doing this
#hunger games style where you can pitch in to buff a player (hard)
#TTT style where *dead* players can harm others
#i feel like both would be nice

#hunger games style i want to be where you can *buff* the current players weapon but you have to have over half of the group vote for that individual, this will only happen once per 5 in game days

#maybe i could combine them

#id also like the ability to bet on players

# realistically i dont want interaction to be overwhelming
# ok so what if you could "sponsor players"
# so someone does !h sponsor <playername>
# this makes a poll of sorts where if it wins after 5 in game days, the player will be sponsored and buffed
# if it fails then the player will get debuffed

#TODO rework bot to
# get most active players in server and use em
# create a channel called "#fighting"
# pin a message with death count, teams and player statuses
# check if the players are correct and allow adding more

weapons = [weapon(0,"hand"),weapon(1,"knife"),weapon(1.5,"dagger"),weapon(3,"rapier"), weapon(4.2, "katana" ), weapon(4, "long sword"), weapon(3.2, "short sword"), weapon(4, "cutlass" ), weapon(1.7, "brass knuckles"), weapon(3, "spear" ), weapon(1.2, "club" ), weapon(1.5, "bat" ), weapon(3, "mace" ), weapon(2, "hammer" ), weapon(1, "frying pan"), weapon(1.5, "baton" ), weapon(2.5, "nunchuck" ), weapon(3.5, "cleaver" ), weapon(2, "pickaxe" ), weapon(3, "axe" )]
sponsorWeapons = [weapon(6.66,"chainsaw"),weapon(7,"fangs"),weapon(6.4,"terrarian"),weapon(5,"boomerang"),weapon(6.9,"diamond sword"),weapon(6.2,"nail"),weapon(4.9,"ceremonial dagger")]
inj_text = [" tripped"," ate bad berries"," pissed themselves"," got attacked by numerous bees"," was down bad"]
kill_text = [" was killed by "," was brutally beaten by "," got pummeled by "," was bodyslammed by "," was eaten by "," lost their head to "]
betray_text = [" was stabbed in the back by "," was shocked to be killed by their good friend, "," opened up to, and then was promptly murdered by ","'s life was ruined by "," found out they befriended a murderer too late "]
fight_text = [" starts a fight with "]
teamUp_text = [" teams up with "," befriends "," shares a coke with "," passionately makes out with "," bones "," is down bad for "]
tie_text = [" failed to kill "," stumbled while fighting "," fell over while duelling "," was spared by "," couldnt beat "," wasnt strong enough to kill "," got bored of fighting "," had to take a break from fighting "]
bond_text = [" bonds with their team mates"," has a cosy campfire"," looks whistfully at their friends"," hugs their pals"," opens up"," talks about their trauma"," cries in the arms of their friends"]
mean_text = [" severly dissed "," fucked up talking to "," got left hanging by "," was refused by "," was left on read by "," will never truly be cared about due to the way people see them, especially "]
alone_text = [" broke up and are now alone"," decided to go their own ways"," decided that single player was more fun so they left eachother"," all decided to be alone"," stopped caring about eachother"]
cry_text = [" cries"," is alone"," sits and is cold"," wants to be hugged"," curls up in a ball"," shouts in desperation"," just wants it to end"," thinks about fortnite"," wishes they had drugs"," doesnt want to kill their friends"," parties"," flosses"," does a cool dance"," eats a nice snack"," is hopeful"]
bad_int_text = [" shouts slurs at "," abuses "," throws rocks at "," insults "," pisses on "," ignores "," decides that they really fucking hate "]
good_int_text = [" gives a cake to "," just wants to be friends with "," tries to cheer up "," tells a joke to "," sends a meme to "," fistbumps "," just hangs out with "]
noMoreFriends_text = [" cant find anyone else to join them"," has too many friends"," has a very big team","'s group scares everyone away"," chills with their bros"," has a team too large for a group hug","'s team prepares to fight"]

dead = []
#TODO event likelyhood changes over time
#interact   unlikely -> likely -> unlikely
#cry        likely -> unlikely
#loot       likely -> unlikely
#teamUp     likely -> likely -> unlikely
#fight      likely -> unlikely -> likely
#injures    unlikely -> likely -> unlikly

class instance:
    people=[]
    tracking = {}
    running=False
    channel=None
    updateAbleMessage=None
    sponsored=False

    def __init__(self,ppl,c):
        self.people=ppl
        self.running=False
        self.channel=c

    def save():
        f = open("data.txt","w")
        for inst in instances:
            f.write(str(inst.channel.id)+"-"+str(inst.updateAbleMessage.id)+"-" +str(inst.running)+"{")
            for p in inst.tracking.keys():
                f.write("["+p.name+"/"+str(inst.tracking[p].dead)+"/"+str(inst.tracking[p].kills)+\
                        "/"+p.wpn.name+"/"+str(p.wpn.strength)+\
                        "/"+str(p.s)+"/"+"\\".join([ x.name for x in p.teamMembers])+"/" +\
                        "\\".join([k.name +":" + str(v) for k,v in p.likes.items()])+"]")
            f.write("}")
        f.close()

    async def load():
        f = open("data.txt","r")
        for l in f:
            inst = instance([],0)
            outs = re.findall(r"([0-9]+?)-([0-9]+?)-(\w+?)\{\[(.*)\]\}",l)[0]
            inst.channel = await client.fetch_channel(int(outs[0]))
            inst.updateAbleMessage = await inst.channel.fetch_message(int(outs[1]))
            inst.running = (outs[2]=="True")
            usrdata = outs[3].split("][")
            usrdata = [x.split("/") for x in usrdata]
            #first pass general data
            personalDatabase = {}
            for a in usrdata:
                p = person(a[0])
                inst.tracking[p]=tracker(p)
                inst.tracking[p].dead=((a[1])=="True")
                print(inst.tracking[p].dead)
                if not inst.tracking[p].dead:
                    personalDatabase[a[0]]=p
                    inst.people.append(p)
                inst.tracking[p].kills=int(a[2])
                p.wpn.name=a[3]
                p.wpn.strength=int(a[4])
                p.s=int(a[5])
            #second pass teams n relationships
            for a in usrdata:
                if (a[1])=="False":
                    p = personalDatabase[a[0]]
                    print(p)
                    for x in a[6].split("\\"):
                        if x!=a[0]:
                            p.teamMembers.append(personalDatabase[x])
                    for x in a[7].split("\\"):
                        x = x.split(":")
                        p.likes[personalDatabase[x[0]]]=int(x[1])
            instances.append(inst)


    async def instanceUpdate(self):
        printedTeams=[]
        output="**People**\t{0} remaining\n".format(len(self.people))
        for p in self.tracking.values():
            liveStr="alive"
            if p.dead:
                liveStr="dead"
            output+="\t{0.name}:\t\tStatus - {1}, Kill Count {0.kills}\n".format(p,liveStr)
        output+="**Teams**"
        different=True
        for p in self.people:
            for t in printedTeams:
                if len(t)==len(p.teamMembers):
                    different=False
                    for j in p.teamMembers:
                        if j not in t:
                            different=True
                            break
                    if not different:
                        break
            if len(p.teamMembers)>1 and different:
                output+="\n\t"+p.teamToStr()
                printedTeams.append(p.teamMembers)
        await self.updateAbleMessage.edit(content=output)



    async def hunger(self):
        for p in self.people:
            p.father=self
            self.tracking[p]=tracker(p)
        date=0
        mainD = {}
        for p in self.people:
            mainD[p]=0
        for p in self.people:
            p.likes=mainD.copy()
        ppl =self.people.copy()
        lol = True
        while len(self.people)>1:
            if datetime.datetime.now().hour>8:
                await asyncio.sleep(3600)
                for i in range(3,9):
                    if len(self.people)==1:
                        break
                    if len(ppl)==0:
                        ppl=self.people.copy()
                    x = random.choice(ppl)
                    ppl.remove(x)
                    if x in self.people:
                        await self.act(x)
                date+=0.1
                await self.instanceUpdate()
        await self.channel.send(self.people[0].name + " won")


    async def injures(self,p):
        p.s/=1.5
        await self.channel.send(p.name + random.choice(inj_text))

    async def fight(self,x):
        me = x
        ded = x
        infighting=False
        while ded == x or (infighting and random.randrange(3)!=1):
            ded = random.choice(self.people)
            infighting=(ded in x.teamMembers)
        if infighting:
            #1 on 1
            diff = x.strength(True)-ded.strength(True)
            margin = (x.strength(True)+ded.strength(True))/2
            while len(self.people)< 4 and margin>diff>-margin:
                diff = x.strength(True)-ded.strength(True)
                margin = (x.strength(True)+ded.strength(True))/2
            if(diff>margin):
                pass
            elif diff<-margin:
                t=ded
                ded=x
                x=t
            else:
                await self.channel.send(x.name +random.choice(tie_text) + ded.name)
                for t in x.teamMembers:
                    if t!=x:
                        await t.adjustLiking(x,False,-1)
                    if t!=ded:
                        await t.adjustLiking(ded,False,-1)
                await ded.adjustLiking(x,True,-1)
                for t in x.teamMembers:
                    t.s*=0.75
                return
            await self.channel.send(ded.name + random.choice(betray_text) + x.name)
            for t in x.teamMembers:
                if t!=x:
                    await t.adjustLiking(x,False,-1)
                if t!=ded:
                    await t.adjustLiking(ded,False,-1)
            self.tracking[ded].dead=True
            self.tracking[x].kills+=1
            ded.die()
            return
        else:
            groupSize = (len(x.teamMembers) + len(ded.teamMembers))
            maxCasualties = random.randrange(0,round(groupSize/2)+1)
            while len(self.people)<4 and maxCasualties<1:
                maxCasualties = random.randrange(0,round(groupSize/2)+1)
            perDict = {}
            performances = []
            for p in x.teamMembers:
                val = p.strength()
                performances.append(val)
                perDict[val]=[0,p]
            for p in ded.teamMembers:
                val = p.strength()
                performances.append(val)
                perDict[val]=[1,p]
            performances.sort()
            teamSize = [len(x.teamMembers),len(ded.teamMembers)]
            killCounts = [0,0]
            #while self.people are still alive and too many self.people havent died
            xStr = x.name
            dStr = ded.name
            if len(x.teamMembers)>1:
                xStr = xStr+"'s team"
            if len(ded.teamMembers)>1:
                dStr = dStr+"'s team"
            if groupSize>2:
                await self.channel.send("a fight has broken out between "+dStr +" and "+ xStr)
            while killCounts[0]+killCounts[1]<maxCasualties and killCounts[0]<teamSize[0] and killCounts[1]<teamSize[1]:
                data = perDict[performances[killCounts[0]+killCounts[1]]]
                killer = data
                while killer[0]+data[0]!=1:
                    killer = perDict[random.choice(performances[killCounts[0]+killCounts[1]+1:])]
                await data[1].adjustLiking(killer[1],False,-2)
                await self.channel.send(data[1].name + random.choice(kill_text) + killer[1].name)
                self.tracking[data[1]].dead=True
                self.tracking[killer[1]].kills+=1
                data[1].die()
                killCounts[data[0]]+=1
            #end fight
            if maxCasualties==0:
                await self.channel.send(xStr + random.choice(tie_text)+dStr)
            elif killCounts[0]+killCounts[1]>=2:
                await self.channel.send("the fight has ended, with "+str(killCounts[0]+killCounts[1])+" casualties")


    async def teamUp(self,x):
        if len(self.people) > len(x.teamMembers):
            plr = random.choice(self.people)
            tries=0
            while (plr in x.teamMembers or len(plr.teamMembers)+len(x.teamMembers)>5) and tries<1000:
                plr = random.choice(self.people)
                tries+=1
            if tries>=1000:
                if len(plr.teamMembers) > len(x.teamMembers):
                    x=plr
                await self.channel.send(x.name+random.choice(noMoreFriends_text))
                return
            if x.wantsToTeam(plr):
                bigT = plr.teamMembers+x.teamMembers
                for i in bigT:
                    i.teamMembers=bigT.copy()
                await self.channel.send(x.name + random.choice(teamUp_text) + plr.name)
                await self.channel.send("team " + x.name+" now consits of " + x.teamToStr())
            else:
                await self.channel.send(x.name + random.choice(mean_text)+plr.name)
                await x.adjustLiking(plr,True,-0.5)
        else:
            await self.channel.send(x.name +random.choice(bond_text))
            for t in x.teamMembers:
                t.s*=1.25


    async def loot(self,p):
        wpn = p.wpn
        while wpn == p.wpn:
            wpn = random.choice(weapons[1:])
        await p.pickUpWeapon(wpn)

    async def cry(self,p):
        await self.channel.send(p.name + random.choice(cry_text))

    async def interact(self,p):
        other = p
        while other==p:
            other = random.choice(self.people)
        if random.random()>0.5:
            #good end
            await self.channel.send(p.name + random.choice(good_int_text) + other.name)
            await other.adjustLiking(p,True,0.5)
        else:
            await self.channel.send(p.name + random.choice(bad_int_text) + other.name)
            await other.adjustLiking(p,True,-0.5)
            #bad end

    events = [interact,cry,loot,teamUp, fight, injures]

    async def act(self,p):
        await random.choice(self.events)(self,p)

class tracker:
    name=""
    dead=False
    kills=0
    def __init__(self,p):
        self.name=p.name

class person:
    father=None
    s=100000000
    wpn=weapons[0]
    teamMembers = []
    name = "sex"
    likes = {}

    def strength(self,team=False):
        if team:
            return (self.wpn.strength+1)*(self.performance()*4)
        for t in self.teamMembers:
            sumStr = (t.wpn.strength+1)*(t.performance()*4)
        return sumStr

    def die(self):
        for t in self.teamMembers:
            if t != self:
                t.teamMembers.remove(self)
        self.dead=True
        self.father.people.remove(self)

    def performance(self,team=False):
        return (self.s+1)*((random.random()+1)/2)

    async def pickUpWeapon(self,wpn):
        if self.wpn.strength < wpn.strength:
            if self.wpn==weapons[0]:
                await self.father.channel.send(self.name + " found a " + wpn.name)
            else:
                await self.father.channel.send(self.name + " swapped their " + self.wpn.name + " for a " + wpn.name)
            self.wpn=wpn
        else:
            await self.father.channel.send(self.name + " found a " + wpn.name + " but it was worse than their " + self.wpn.name)

    def wantsToTeam(self,p,v=1):
        return (p.likes[self]>-v and self.likes[p]>-v)

    def teamToStr(self):
        return ", ".join([_.name for _ in self.teamMembers[:-1]])+" and " + self.teamMembers[-1].name

    async def adjustLiking(self,p,mutual:bool,change:float):
        if p in self.teamMembers:
            self.likes[p]+=change
            if mutual:
                p.likes[self]+=change
            if not p.wantsToTeam(self,2):
                await self.father.channel.send(p.teamToStr()+" broke up and are now alone")
                for i in self.teamMembers:
                    i.teamMembers=[i]
        for i in self.teamMembers:
            for j in p.teamMembers:
                i.likes[j]+=change
                if mutual:
                    j.likes[i]+=change

    def __init__(self,n):
        self.name=n
        self.teamMembers = [self]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


instances=[]
@client.event
async def on_ready():
    await instance.load()
    while True:
        await asyncio.sleep(3600*5)
        instance.save()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if "!fightwars" in message.content:
        global guildData
        guild = message.guild
        chan=None
        for c in guild.channels:
            if "fighting" == c.name:
                chan=c
                break
        if chan==None:
            try:
                chan = await guild.create_text_channel("fighting")
            except:
                await message.channel.send("I do not have the ability to create channels\npls giv")
                return
        await message.channel.send("i am going to use the data from this channel to find frequent users to add to the game :3")
        userRatings = {}
        usersNew = []
        async for m in message.channel.history(limit=500):
            if m.author.display_name in userRatings:
                userRatings[m.author.display_name]+=1
            else:
                userRatings[m.author.display_name]=1
        for x in sorted(userRatings.items(), key=lambda x:x[1])[:20]:
            usersNew.append(person(x[0]))
        await message.channel.send("the users im going to use are " + ", ".join(x.name for x in usersNew)+"\nuse !f remove <username> to remove from this list and !f add <username> to add\nuse !f list to display all users currently\nuse !f start to begin the game\n**oh also all messages to me now need to be sent in #fighting** <3")
        if chan.id != message.channel.id:
            await chan.send("the users im going to use are " + ", ".join(x.name for x in usersNew)+"\nuse !f remove <username> to remove from this list and !f add <username> to add\nuse !f list to display all users currently\nuse !f start to begin the game\n**oh also all messages to me now need to be sent in #fighting** <3")
        instances.append(instance(usersNew,chan))
        return
    if "!f" in message.content:
        dataFocus = None
        for d in instances:
            if message.channel.id == d.channel.id:
                dataFocus = d
                break
        if dataFocus==None:
            await message.channel.send("wrong channel xoxoxox")
        if "!f remove" in message.content and not dataFocus.running:
            unam = message.content[len("!f remove "):]
            toRemove = None
            for p in dataFocus.people:
                if unam == p.name:
                    toRemove = p
                    break
            if toRemove == None:
                await message.channel.send("i cant find that user, sorry")
            else:
                dataFocus.people.remove(toRemove)
                await message.channel.send("bang, and the dust is gone")
        if "!f add" in message.content and not dataFocus.running:
            unam = message.content[len("!f add "):]
            dataFocus.people.append(person(unam))
        if "!f start" in message.content:
            await message.channel.send("oke all ready\nstarts in T minus one hour")
            dataFocus.updateAbleMessage = await message.channel.send("this message will be updated with the game content")
            try:
                await dataFocus.updateAbleMessage.pin()
            except:
                pass
            dataFocus.running=True
            await dataFocus.hunger()
        if "!f list" in message.content:
            await message.channel.send("\n".join(x.name for x in dataFocus.people))
        if "!f sponsor" in message.content and dataFocus.running and not dataFocus.sponsored:
            unam = message.content[len("!f sponsor "):]
            toSponsor= None
            dataFocus.sponsored=True
            for p in dataFocus.people:
                if unam == p.name:
                    toSponsor= p
                    break
            if toSponsor == None:
                await message.channel.send("i cant find that user, sorry")
            else:
                m = await message.channel.send("react with \n\t👍 to sponsor the player\n\t👎 to make them suffer\nI'll check on it in 5 hours")
                mid = m.id
                await m.add_reaction("👍")
                await m.add_reaction("👎")
                await asyncio.sleep(3600*5)
                m = await dataFocus.fetch_message(mid)
                up =0
                down =0
                for r in m.reactions:
                    if r.emoji=="👎":
                        down=r.count
                    if r.emoji=="👍":
                        up=r.count
                if up > down:
                    await message.channel.send(toSponsor.name +" was successfully sponsored and has been given a op weapon")
                    wpn = toSponsor
                    while wpn == toSponsor.wpn:
                        wpn = random.choice(sponsorWeapons)
                    await toSponsor.pickUpWeapon(wpn)
                else:
                    toSponsor.s*=0.666
                    await message.channel.send("seems like "+toSponsor.name+" wasnt liked, they are now significantly weaker")
    if "!f quit" in message.content and message.author.id == 693968334328299520:
        instance.save()
        await message.channel.send("done")
        quit()

loop = asyncio.get_event_loop()
client.run(f[8])
