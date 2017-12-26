import re

# RegExp for date fomate
DATE = '(0[1-9]|[12][0-9]|3[01])' +\
       '[- /.]?(0[1-9]|1[012])' +\
       '[- /.]?((19|20)\d\d|\d\d$)'

# Path to blacklist file
FILE = './10_million_password_list_top_100000.txt'

RECOMEND = {
        'len': 'Your password is too short. Increase it lenght!',
        'digits': 'Use numerical digits for increasing strenght!',
        'loletters': 'Use lower-case letters for increasing strenght!',
        'upletters': 'Use upper-case letters for increasing strenght!',
        'symbols': 'Use special chars, such as @, #, for increasing strenght!',
        'dateformate': 'Your password match the formate of calendar dates, ' +
                       'change your password!',
        'blacklist': 'Your password found in a password blacklist, ' +
                     'change it immediately!'
        }


# Returns special color string RED:[0-3] YELLOW:[4-7] GREEN:[8-10]
def get_color(number):
    colors = {
          'red': '\x1b[1;31;40m',
          'yellow': '\x1b[1;33;40m',
          'green': '\x1b[1;32;40m'
          }
    return number < 4 and colors['red'] or\
        number > 7 and colors['green'] or\
        colors['yellow']


def find_str_in_file(string, filename):
    try:
        f = open(filename, 'r')
    except IOError as error:
        print(get_color(0) + 'Blacklist dictionary not found\n' +
              str(error) + '\nSkiping blacklist test' + '\x1b[0m')
        return False
    for line in f:
        if line.strip() == string:
            return True
    return False


def check_password(passw):
    return {
        'len': len(passw),
        'digits': re.search('[0-9]', passw) and 1 or 0,
        'loletters': re.search('[a-z]', passw) and 1 or 0,
        'upletters': re.search('[A-Z]', passw) and 1 or 0,
        'symbols': re.search('[\W_]', passw) and 1 or 0,
        'dateformate': not(re.match(DATE, passw)) and 1 or 0,
        'blacklist': not(find_str_in_file(passw, FILE)) and 1 or 0
        }


def get_password_strength(passw):
    checks = check_password(passw)

    # value of password lenght [min= -3: max=2]
    max_len_value = 2
    len_value = min(((checks['len']-1) // 4 - 2), max_len_value)

    # value of using different charsets [min=4: max=16]
    sharset_value = 4*(
                       checks['digits'] +
                       checks['loletters'] +
                       checks['upletters'] +
                       checks['symbols']
                      )

    # Calculate strenght: [max:int(1,111^22) = 10; min:int(1,111^1) = 1]
    strength = int(pow(1.111, len_value +
                       sharset_value +
                       checks['dateformate'] +
                       3*checks['blacklist']))

    recomend = '\n'.join([RECOMEND[key] for key in checks.keys()
                         if checks[key] < 1
                         or (key == 'len' and checks[key] < 17)])
    return {
        'strength': strength,
        'recomend': recomend
        }


if __name__ == '__main__':
    passw = ' '
    while passw:
        passw = input('Input a password for checking or tap Enter for exit: ')
        if passw:
            password_strength = get_password_strength(passw)
            color = get_color(password_strength['strength'])

            print(color + '\n' + 'Your password strength: ' +
                  str(password_strength['strength']) + '\n')
            print((password_strength['recomend'] and 'RECOMENDATIONS:\n\n' +
                   password_strength['recomend'] +
                   '\n\n'
                   or 'Great! Your password is strong,' +
                   'but how do you remember it?\n') + '\x1b[0m')
