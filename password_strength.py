import re
import getpass


def get_color(minimum, maximum, current):
    maximum_red = 0.4
    minimum_green = 0.7
    proportion = current/(maximum - minimum)
    return proportion <= maximum_red and 'red' or (
        proportion >= minimum_green and 'green') or 'yellow'


def colorize(string, color):
    colors = {
        'red': '\x1b[1;31;40m',
        'yellow': '\x1b[1;33;40m',
        'green': '\x1b[1;32;40m',
        'reset': '\x1b[0m',
    }
    return '{}{}{}'.format(colors[color], string, colors['reset'])


def get_rate(minimum, maximum, best_value, current_value):
    return minimum - 1 + int(pow(maximum - minimum + 1,
                             min(current_value, best_value)/best_value))


def summ_matched_keys_values(dict_1, dict_2):
    return sum([dict_1[key] for key in dict_2.keys() if isinstance(
                                                            dict_1[key], int)])


def check_by_patterns(checks, password):
    charsets = ['digits', 'loletters', 'upletters', 'symbols']
    formats = ['dateformat']
    patterns = {
        'digits': (re.compile('[0-9]').search, True),
        'loletters': (re.compile('[a-z]').search, True),
        'upletters': (re.compile('[A-Z]').search, True),
        'symbols': (re.compile('[\W_]').search, True),
        'dateformat': (re.compile(
                 """(0[1-9]|[12][0-9]|3[01])[- /.] # day
                 ?(0[1-9]|1[012])[- /.]            # month
                 ?((19|20)\d\d|\d\d$)              # year
                 """, re.X).match, False),
    }
    for key, pattern in patterns.items():
        function, logic = pattern
        checks[key] = (function(password) is not None) == logic and 1 or 0
    checks['charsets'] = sum([checks[key] for key in charsets])
    checks['max_charsets_rate'] = len(charsets)
    checks['formats'] = sum([checks[key] for key in formats])
    checks['max_formats_rate'] = len(formats)
    return checks


def read_files(dict_of_paths):
    dict_of_texts = {}
    for key, path in dict_of_paths.items():
        try:
            with open(path) as file_to_read:
                dict_of_texts[key] = file_to_read.read()
        except IOError:
            dict_of_texts[key] = None
    return dict_of_texts


def check_by_blacklist(checks, dict_of_texts, password):
    for key, text in dict_of_texts.items():
        if text:
            checks[key] = not (password.lower() in text.split('\n'))
        else:
            checks[key] = None
    return checks


def check_errors(checks):
    for key, value in checks.items():
        if value is None:
            print(colorize(
                'Attention! {} test was skipped'.format(str(key)), 'red'))


if __name__ == '__main__':
    # Initial Data
    minimum_strenght = 1
    maximum_strenght = 10
    # Weight of password's lenght
    min_len_value = -2
    max_len_value = 2
    len_of_best_password = 16
    # Weight of charset, format and blacklist tests
    charsets_coeff = 4
    formats_coeff = 1
    blacklists_coeff = 3

    Recommends_Dict = {
        'len': 'Your password is too short. Increase it lenght!',
        'digits': 'Use numerical digits for increasing strenght!',
        'loletters': 'Use lower-case letters for increasing strenght!',
        'upletters': 'Use upper-case letters for increasing strenght!',
        'symbols': 'Use special chars, such as @, #, for increasing strenght!',
        'dateformat': 'Your password match the format of calendar dates, ' +
                      'change your password!',
        'blacklist': 'Your password found in a password blacklist, ' +
                     'change it immediately!',
        'names': 'Your password found in a names list, change it immediately!'
    }
    password = ' '
    while password:
        password = getpass.getpass(
                prompt='Input a password for checking or tap Enter for exit: ')
        if password:
            # Get tests results
            checks = {
                'len': len(password)
            }
            checks = check_by_patterns(checks, password)
            blacklist_files = {
                'blacklist': './10_million_password_list_top_100000.txt',
                'names': './names.txt'
            }
            checks = check_by_blacklist(
                checks,
                read_files(blacklist_files),
                password,
            )
            check_errors(checks)
            maximum_check_range = max_len_value + (
                charsets_coeff * checks['max_charsets_rate'] +
                formats_coeff * checks['max_formats_rate'] +
                blacklists_coeff * len(blacklist_files))

            # Componets of strenght, based on different tests
            len_value = get_rate(
                minimum=min_len_value,
                maximum=max_len_value,
                best_value=len_of_best_password,
                current_value=checks['len']
            )

            charset_value = charsets_coeff * checks['charsets']
            format_value = formats_coeff * checks['formats']
            blacklist_value = blacklists_coeff * (
                    summ_matched_keys_values(checks, blacklist_files))

            check_result = sum([len_value,
                                charset_value,
                                format_value,
                                blacklist_value])

            password_strength = get_rate(
                minimum=minimum_strenght,
                maximum=maximum_strenght,
                best_value=maximum_check_range,
                current_value=check_result
            )

            color = get_color(
                minimum=minimum_strenght,
                maximum=maximum_strenght,
                current=password_strength
            )

            recommends = '\n'.join(
                [Recommends_Dict[key] for key in checks.keys()
                 if key in Recommends_Dict and (
                    checks[key] is not None and checks[key] < 1
                    or (key == 'len' and checks[key] < len_of_best_password))])

            print(colorize('\nYour password strength: {}'.format(
                                             str(password_strength)), color))

            print(colorize(
                recommends and 'RECOMMENDATIONS:\n\n{}\n'.format(recommends)
                or 'Great! Your password is strong, ' +
                   'but how do you remember it?\n', color))
