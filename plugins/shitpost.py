import utils

async def shitpost(self, room, user, arg):
  if room is None or not utils.is_private(self, room):
    return

  message = utils.remove_accents(arg.strip())
  if len(message) > 15:
    await self.send_reply(room, user, 'Testo troppo lungo')
    return

  text0 = ''
  text1 = ''
  text2 = ''

  if message == '':
    message = 'SHITPOST'

  message = list(message)
  for i in message:
    if i in LETTERS:
      if text0 != '':
        text0 += ' '
        text1 += ' '
        text2 += ' '
      text0 += LETTERS[i][0]
      text1 += LETTERS[i][1]
      text2 += LETTERS[i][2]

  await self.send_htmlbox(room,
                          '<pre style="margin:0">{}\n{}\n{}</pre>'.format(text0,
                                                                          text1,
                                                                          text2))


LETTERS = {'a': ['┌─┐',
                 '├─┤',
                 '┴ ┴'],
           'b': ['┌┐ ',
                 '├┴┐',
                 '└─┘'],
           'c': ['┌─┐',
                 '│  ',
                 '└─┘'],
           'd': ['┌┬┐',
                 ' ││',
                 '─┴┘'],
           'e': ['┌─┐',
                 '├┤ ',
                 '└─┘'],
           'f': ['┌─┐',
                 '├┤ ',
                 '└  '],
           'g': ['┌─┐',
                 '│ ┬',
                 '└─┘'],
           'h': ['┬ ┬',
                 '├─┤',
                 '┴ ┴'],
           'i': ['┬',
                 '│',
                 '┴'],
           'j': [' ┬',
                 ' │',
                 '└┘'],
           'k': ['┬┌─',
                 '├┴┐',
                 '┴ ┴'],
           'l': ['┬  ',
                 '│  ',
                 '┴─┘'],
           'm': ['┌┬┐',
                 '│││',
                 '┴ ┴'],
           'n': ['┌┐┌',
                 '│││',
                 '┘└┘'],
           'o': ['┌─┐',
                 '│ │',
                 '└─┘'],
           'p': ['┌─┐',
                 '├─┘',
                 '┴  '],
           'q': ['┌─┐ ',
                 '│─┼┐',
                 '└─┘└'],
           'r': ['┬─┐',
                 '├┬┘',
                 '┴└─'],
           's': ['┌─┐',
                 '└─┐',
                 '└─┘'],
           't': ['┌┬┐',
                 ' │ ',
                 ' ┴ '],
           'u': ['┬ ┬',
                 '│ │',
                 '└─┘'],
           'v': ['┬  ┬',
                 '└┐┌┘',
                 ' └┘ '],
           'w': ['┬ ┬',
                 '│││',
                 '└┴┘'],
           'x': ['─┐ ┬',
                 '┌┴┬┘',
                 '┴ └─'],
           'y': ['┬ ┬',
                 '└┬┘',
                 ' ┴ '],
           'z': ['┌─┐',
                 '┌─┘',
                 '└─┘'],
           'A': ['╔═╗',
                 '╠═╣',
                 '╩ ╩'],
           'B': ['╔╗ ',
                 '╠╩╗',
                 '╚═╝'],
           'C': ['╔═╗',
                 '║  ',
                 '╚═╝'],
           'D': ['╔╦╗',
                 ' ║║',
                 '═╩╝'],
           'E': ['╔═╗',
                 '║╣ ',
                 '╚═╝'],
           'F': ['╔═╗',
                 '╠╣ ',
                 '╚  '],
           'G': ['╔═╗',
                 '║ ╦',
                 '╚═╝'],
           'H': ['╦ ╦',
                 '╠═╣',
                 '╩ ╩'],
           'I': ['╦',
                 '║',
                 '╩'],
           'J': [' ╦',
                 ' ║',
                 '╚╝'],
           'K': ['╦╔═',
                 '╠╩╗',
                 '╩ ╩'],
           'L': ['╦  ',
                 '║  ',
                 '╩═╝'],
           'M': ['╔╦╗',
                 '║║║',
                 '╩ ╩'],
           'N': ['╔╗╔',
                 '║║║',
                 '╝╚╝'],
           'O': ['╔═╗',
                 '║ ║',
                 '╚═╝'],
           'P': ['╔═╗',
                 '╠═╝',
                 '╩  '],
           'Q': ['╔═╗ ',
                 '║═╬╗',
                 '╚═╝╚'],
           'R': ['╦═╗',
                 '╠╦╝',
                 '╩╚═'],
           'S': ['╔═╗',
                 '╚═╗',
                 '╚═╝'],
           'T': ['╔╦╗',
                 ' ║ ',
                 ' ╩ '],
           'U': ['╦ ╦',
                 '║ ║',
                 '╚═╝'],
           'V': ['╦  ╦',
                 '╚╗╔╝',
                 ' ╚╝ '],
           'W': ['╦ ╦',
                 '║║║',
                 '╚╩╝'],
           'X': ['═╗ ╦',
                 '╔╩╦╝',
                 '╩ ╚═'],
           'Y': ['╦ ╦',
                 '╚╦╝',
                 ' ╩ '],
           'Z': ['╔═╗',
                 '╔═╝',
                 '╚═╝'],
           '0': ['╔═╗',
                 '║ ║',
                 '╚═╝'],
           '1': ['╗',
                 '║',
                 '╩'],
           '2': ['╔═╗',
                 '╔═╝',
                 '╚═╝'],
           '3': ['╔═╗',
                 ' ═╣',
                 '╚═╝'],
           '4': ['╦ ╦',
                 '╚═╣',
                 '  ╩'],
           '5': ['╔═╗',
                 '╚═╗',
                 '╚═╝'],
           '6': ['╔═╗',
                 '╠═╗',
                 '╚═╝'],
           '7': ['═╗',
                 ' ║',
                 ' ╩'],
           '8': ['╔═╗',
                 '╠═╣',
                 '╚═╝'],
           '9': ['╔═╗',
                 '╚═╣',
                 '╚═╝'],
           ' ': ['  ',
                 '  ',
                 '  '],
           '!': ['║',
                 '║',
                 '▀'],
           '"': ['╚╚',
                 '  ',
                 '  '],
           '£': ['╔═╗',
                 '╬═ ',
                 '╩══'],
           '$': ['╔╬╗',
                 '╚╬╗',
                 '╚╬╝'],
           '%': ['▄ ┬ ',
                 ' ┌┘ ',
                 ' ┴ ▀'],
           '\\': ['┬ ',
                  '└┐',
                  ' ┴'],
           '(': ['┌',
                 '│',
                 '└'],
           ')': ['┐',
                 '│',
                 '┘'],
           '=': ['  ',
                 '──',
                 '──'],
           '\'': ['▀',
                  ' ',
                  ' '],
           '?': ['╔═╗',
                 ' ╔╝',
                 ' ▀ '],
           '/': [' ┬',
                 '┌┘',
                 '┴ '],
           '|': ['║',
                 '║',
                 '║'],
           '-': ['  ',
                 '──',
                 '  '],
           '+': [' │ ',
                 '─┼─',
                 ' │ '],
           ':': ['▄',
                 ' ',
                 '▀'],
           '.': [' ',
                 ' ',
                 '▀'],
           '_': ['   ',
                 '   ',
                 '───'],
           '[': ['╔',
                 '║',
                 '╚'],
           ']': ['╗',
                 '║',
                 '╝'],
           '{': ['╔',
                 '╣',
                 '╚'],
           '}': ['╗',
                 '╠',
                 '╝'],
           '#': ['  ',
                 '╬╬',
                 '╬╬'],
           '~': ['   ',
                 '╔═╝',
                 '   '],
           ',': [' ',
                 ' ',
                 '╗'],
           ';': ['▄',
                 ' ',
                 '╗'],
           '°': ['┌┐',
                 '└┘',
                 '  ']}
