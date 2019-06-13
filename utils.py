import re
import json
import hashlib
import math

import requests

def restart_bot(self):
  print('Restarting')
  requests.delete('https://api.heroku.com/apps/cerbottana/dynos',
                  headers={'Content-Type': 'application/json',
                           'Accept': 'application/vnd.heroku+json; version=3',
                           'Authorization': 'Bearer {}'.format(self.heroku_token)})


def to_user_id(user):
  userid = re.sub(r'[^a-z0-9]', '', user.lower())
  return userid

def to_room_id(room):
  roomid = re.sub(r'[^a-z0-9-]', '', room.lower())
  if not roomid:
    roomid = 'lobby'
  return roomid


def remove_accents(text):
  text = re.sub(r'à', 'a', text)
  text = re.sub(r'è|é', 'e', text)
  text = re.sub(r'ì', 'i', text)
  text = re.sub(r'ò', 'o', text)
  text = re.sub(r'ù', 'u', text)
  text = re.sub(r'À', 'A', text)
  text = re.sub(r'È|É', 'E', text)
  text = re.sub(r'Ì', 'I', text)
  text = re.sub(r'Ò', 'O', text)
  text = re.sub(r'Ù', 'U', text)
  return text

def date_format(text):
  return '{dd}/{mm}/{yyyy}'.format(dd=text[-2:], mm=text[5:7], yyyy=text[:4])


def database_request(self, action, params):
  req = requests.post(self.database_api_url,
                      data={**params,
                            'key': self.database_api_key,
                            'action': action})
  if req.text == '':
    return None
  return json.loads(req.text)


def is_voice(user):
  return user[0] in '+*%@★#&~'

def is_private(self, room):
  return room in self.private_rooms


def username_color(name):
  # pylint: disable=too-many-locals,invalid-name
  md5 = hashlib.md5(name.encode('utf-8')).hexdigest()

  h = int(md5[4:8], 16) % 360
  s = int(md5[:4], 16) % 50 + 40
  l = math.floor(int(md5[8:12], 16) % 20 + 30)

  c = (100 - abs(2 * l - 100)) * s / 100 / 100
  x = c * (1 - abs((h / 60) % 2 -1))
  m = l / 100 - c / 2

  if math.floor(h / 60) == 1:
    r1 = x
    g1 = c
    b1 = 0
  elif math.floor(h / 60) == 2:
    r1 = 0
    g1 = c
    b1 = x
  elif math.floor(h / 60) == 3:
    r1 = 0
    g1 = x
    b1 = c
  elif math.floor(h / 60) == 4:
    r1 = x
    g1 = 0
    b1 = c
  elif math.floor(h / 60) == 5:
    r1 = c
    g1 = 0
    b1 = x
  else:
    r1 = c
    g1 = x
    b1 = 0

  r = r1 + m
  g = g1 + m
  b = b1 + m
  lum = r ** 3 * 0.2126 + g ** 3 * 0.7152 + b ** 3 * 0.0722

  hlmod = (lum - 0.2) * -150
  if hlmod > 18:
    hlmod = (hlmod - 18) * 2.5
  elif hlmod < 0:
    hlmod = (hlmod - 0) / 3
  else:
    hlmod = 0

  hdist = min(abs(180 - h), abs(240 - h))
  if hdist < 15:
    hlmod += (15 - hdist) / 3

  l += hlmod

  return 'hsl({h},{s}%,{l}%)'.format(h=h, s=s, l=l)


AVATAR_IDS = {'1': 'lucas',
              '2': 'dawn',
              '3': 'youngster-gen4',
              '4': 'lass-gen4dp',
              '5': 'camper',
              '6': 'picnicker',
              '7': 'bugcatcher',
              '8': 'aromalady',
              '9': 'twins-gen4dp',
              '10': 'hiker-gen4',
              '11': 'battlegirl-gen4',
              '12': 'fisherman-gen4',
              '13': 'cyclist-gen4',
              '14': 'cyclistf-gen4',
              '15': 'blackbelt-gen4dp',
              '16': 'artist-gen4',
              '17': 'pokemonbreeder-gen4',
              '18': 'pokemonbreederf-gen4',
              '19': 'cowgirl',
              '20': 'jogger',
              '21': 'pokefan-gen4',
              '22': 'pokefanf-gen4',
              '23': 'pokekid',
              '24': 'youngcouple-gen4dp',
              '25': 'acetrainer-gen4dp',
              '26': 'acetrainerf-gen4dp',
              '27': 'waitress-gen4',
              '28': 'veteran-gen4',
              '29': 'ninjaboy',
              '30': 'dragontamer',
              '31': 'birdkeeper-gen4dp',
              '32': 'doubleteam',
              '33': 'richboy-gen4',
              '34': 'lady-gen4',
              '35': 'gentleman-gen4dp',
              '36': 'madame-gen4dp',
              '37': 'beauty-gen4dp',
              '38': 'collector',
              '39': 'policeman-gen4',
              '40': 'pokemonranger-gen4',
              '41': 'pokemonrangerf-gen4',
              '42': 'scientist-gen4dp',
              '43': 'swimmer-gen4dp',
              '44': 'swimmerf-gen4dp',
              '45': 'tuber',
              '46': 'tuberf',
              '47': 'sailor',
              '48': 'sisandbro',
              '49': 'ruinmaniac',
              '50': 'psychic-gen4',
              '51': 'psychicf-gen4',
              '52': 'gambler',
              '53': 'guitarist-gen4',
              '54': 'acetrainersnow',
              '55': 'acetrainersnowf',
              '56': 'skier',
              '57': 'skierf-gen4dp',
              '58': 'roughneck-gen4',
              '59': 'clown',
              '60': 'worker-gen4',
              '61': 'schoolkid-gen4dp',
              '62': 'schoolkidf-gen4',
              '63': 'roark',
              '64': 'barry',
              '65': 'byron',
              '66': 'aaron',
              '67': 'bertha',
              '68': 'flint',
              '69': 'lucian',
              '70': 'cynthia-gen4',
              '71': 'bellepa',
              '72': 'rancher',
              '73': 'mars',
              '74': 'galacticgrunt',
              '75': 'gardenia',
              '76': 'crasherwake',
              '77': 'maylene',
              '78': 'fantina',
              '79': 'candice',
              '80': 'volkner',
              '81': 'parasollady-gen4',
              '82': 'waiter-gen4dp',
              '83': 'interviewers',
              '84': 'cameraman',
              '85': 'reporter',
              '86': 'idol',
              '87': 'cyrus',
              '88': 'jupiter',
              '89': 'saturn',
              '90': 'galacticgruntf',
              '91': 'argenta',
              '92': 'palmer',
              '93': 'thorton',
              '94': 'buck',
              '95': 'darach',
              '96': 'marley',
              '97': 'mira',
              '98': 'cheryl',
              '99': 'riley',
              '100': 'dahlia',
              '101': 'ethan',
              '102': 'lyra',
              '103': 'twins-gen4',
              '104': 'lass-gen4',
              '105': 'acetrainer-gen4',
              '106': 'acetrainerf-gen4',
              '107': 'juggler',
              '108': 'sage',
              '109': 'li',
              '110': 'gentleman-gen4',
              '111': 'teacher',
              '112': 'beauty',
              '113': 'birdkeeper',
              '114': 'swimmer-gen4',
              '115': 'swimmerf-gen4',
              '116': 'kimonogirl',
              '117': 'scientist-gen4',
              '118': 'acetrainercouple',
              '119': 'youngcouple',
              '120': 'supernerd',
              '121': 'medium',
              '122': 'schoolkid-gen4',
              '123': 'blackbelt-gen4',
              '124': 'pokemaniac',
              '125': 'firebreather',
              '126': 'burglar',
              '127': 'biker-gen4',
              '128': 'skierf',
              '129': 'boarder',
              '130': 'rocketgrunt',
              '131': 'rocketgruntf',
              '132': 'archer',
              '133': 'ariana',
              '134': 'proton',
              '135': 'petrel',
              '136': 'eusine',
              '137': 'lucas-gen4pt',
              '138': 'dawn-gen4pt',
              '139': 'madame-gen4',
              '140': 'waiter-gen4',
              '141': 'falkner',
              '142': 'bugsy',
              '143': 'whitney',
              '144': 'morty',
              '145': 'chuck',
              '146': 'jasmine',
              '147': 'pryce',
              '148': 'clair',
              '149': 'will',
              '150': 'koga',
              '151': 'bruno',
              '152': 'karen',
              '153': 'lance',
              '154': 'brock',
              '155': 'misty',
              '156': 'ltsurge',
              '157': 'erika',
              '158': 'janine',
              '159': 'sabrina',
              '160': 'blaine',
              '161': 'blue',
              '162': 'red',
              '163': 'red',
              '164': 'silver',
              '165': 'giovanni',
              '166': 'unknownf',
              '167': 'unknown',
              '168': 'unknown',
              '169': 'hilbert',
              '170': 'hilda',
              '171': 'youngster',
              '172': 'lass',
              '173': 'schoolkid',
              '174': 'schoolkidf',
              '175': 'smasher',
              '176': 'linebacker',
              '177': 'waiter',
              '178': 'waitress',
              '179': 'chili',
              '180': 'cilan',
              '181': 'cress',
              '182': 'nurseryaide',
              '183': 'preschoolerf',
              '184': 'preschooler',
              '185': 'twins',
              '186': 'pokemonbreeder',
              '187': 'pokemonbreederf',
              '188': 'lenora',
              '189': 'burgh',
              '190': 'elesa',
              '191': 'clay',
              '192': 'skyla',
              '193': 'pokemonranger',
              '194': 'pokemonrangerf',
              '195': 'worker',
              '196': 'backpacker',
              '197': 'backpackerf',
              '198': 'fisherman',
              '199': 'musician',
              '200': 'dancer',
              '201': 'harlequin',
              '202': 'artist',
              '203': 'baker',
              '204': 'psychic',
              '205': 'psychicf',
              '206': 'cheren',
              '207': 'bianca',
              '208': 'plasmagrunt-gen5bw',
              '209': 'n',
              '210': 'richboy',
              '211': 'lady',
              '212': 'pilot',
              '213': 'workerice',
              '214': 'hoopster',
              '215': 'scientistf',
              '216': 'clerkf',
              '217': 'acetrainerf',
              '218': 'acetrainer',
              '219': 'blackbelt',
              '220': 'scientist',
              '221': 'striker',
              '222': 'brycen',
              '223': 'iris',
              '224': 'drayden',
              '225': 'roughneck',
              '226': 'janitor',
              '227': 'pokefan',
              '228': 'pokefanf',
              '229': 'doctor',
              '230': 'nurse',
              '231': 'hooligans',
              '232': 'battlegirl',
              '233': 'parasollady',
              '234': 'clerk',
              '235': 'clerk-boss',
              '236': 'backers',
              '237': 'backersf',
              '238': 'veteran',
              '239': 'veteranf',
              '240': 'biker',
              '241': 'infielder',
              '242': 'hiker',
              '243': 'madame',
              '244': 'gentleman',
              '245': 'plasmagruntf-gen5bw',
              '246': 'shauntal',
              '247': 'marshal',
              '248': 'grimsley',
              '249': 'caitlin',
              '250': 'ghetsis-gen5bw',
              '251': 'depotagent',
              '252': 'swimmer',
              '253': 'swimmerf',
              '254': 'policeman',
              '255': 'maid',
              '256': 'ingo',
              '257': 'alder',
              '258': 'cyclist',
              '259': 'cyclistf',
              '260': 'cynthia',
              '261': 'emmet',
              '262': 'hilbert-dueldisk',
              '263': 'hilda-dueldisk',
              '264': 'hugh',
              '265': 'rosa',
              '266': 'nate',
              '267': 'colress',
              '268': 'beauty-gen5bw2',
              '269': 'ghetsis',
              '270': 'plasmagrunt',
              '271': 'plasmagruntf',
              '272': 'iris-gen5bw2',
              '273': 'brycenman',
              '274': 'shadowtriad',
              '275': 'rood',
              '276': 'zinzolin',
              '277': 'cheren-gen5bw2',
              '278': 'marlon',
              '279': 'roxie',
              '280': 'roxanne',
              '281': 'brawly',
              '282': 'wattson',
              '283': 'flannery',
              '284': 'norman',
              '285': 'winona',
              '286': 'tate',
              '287': 'liza',
              '288': 'juan',
              '289': 'guitarist',
              '290': 'steven',
              '291': 'wallace',
              '292': 'bellelba',
              '293': 'benga',
              '294': 'ash',
              '#bw2elesa': 'elesa-gen5bw2',
              '#teamrocket': 'teamrocket',
              '#yellow': 'yellow',
              '#zinnia': 'zinnia',
              '#clemont': 'clemont',
              '#wally': 'wally',
              'breeder': 'pokemonbreeder',
              'breederf': 'pokemonbreederf',

              '1001': '#1001',
              '1002': '#1002',
              '1003': '#1003',
              '1005': '#1005',
              '1010': '#1010'}
