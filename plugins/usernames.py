import random

import utils

async def acher(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'lo acher che bontà ♫')

async def aethernum(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'da decidere')

async def alpha(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Italian luck jajaja')

async def consecutio(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  text = 'opss{} ho lasciato il pc acceso tutta notte'.format('s' * random.randint(0, 3))
  await self.send_reply(room, user, text)

async def duck(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'quack')

async def edgummet(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'soccontro')

async def francyy(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'ei qualcuno ha qualche codice tcgo??? :3')

async def haund(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, '( ͡° ͜ʖ ͡°)')

async def howkings(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Che si vinca o si perda, v0lca merda :3')

async def inflikted(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  letters = {1: 'I',
             2: 'N',
             3: 'F',
             4: 'L',
             5: 'I',
             6: 'K',
             7: 'T',
             8: 'E',
             9: 'D'}
  shuffled = sorted(letters, key=lambda x: random.random() * x / len(letters))
  text = ''
  for i in shuffled:
    text += letters[i]
  await self.send_reply(room, user, 'ciao {}'.format(text))

async def lange(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Haund mi traduci questo post?')

async def milak(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'No Maria io esco')

async def mister(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Master')
async def mistercantiere(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'MasterCantiere')

async def oizys(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'no')

async def r0spe(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'buondì')

async def silver97(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  tiers = ['OU', 'Ubers', 'UU', 'RU', 'NU', 'PU', 'LC', 'Monotype', 'Anything Goes',
           '1v1', 'ZU', 'CAP', 'Doubles OU', 'Doubles Ubers', 'Doubles UU', 'VGC']
  await self.send_reply(room, user, 'qualcuno mi passa un team {}'.format(random.choice(tiers)))

async def smilzo(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'mai na gioia')

async def specn(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Vi muto tutti')

async def swculone(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'hue')

async def thequasar(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Basta con le pupazzate')

async def trev(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'gioco di merda')

async def uselesstrainer(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'kek')

async def v0lca(self, room, user, arg):
  if room is not None and not utils.is_voice(user):
    return
  await self.send_reply(room, user, 'Porco mele...')
