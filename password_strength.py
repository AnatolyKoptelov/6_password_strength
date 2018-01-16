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
    return minimum - 1 + int(pow(
        maximum - minimum + 1,
        min(current_value, best_value)/best_value
        ))


def summ_matched_keys_values(dict_1, dict_2):
    return sum([dict_1[key] for key in dict_2.keys() if isinstance(
        dict_1[key], int
        )
    ])


def check_by_patterns(checks, password):

    def summ_matched_values(dict_1, list_1):
        return sum([dict_1[key] for key in list_1 if isinstance(
            dict_1[key], int
            )
        ])

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
    for test_name, pattern in patterns.items():
        function, logic = pattern
        checks[test_name] = int((function(password) is not None) == logic)
    checks['charsets'] = summ_matched_values(checks, charsets)
    checks['max_charsets_rate'] = len(charsets)
    checks['formats'] = summ_matched_values(checks, formats)
    checks['max_formats_rate'] = len(formats)
    return checks


def read_files(dict_of_paths):
    dict_of_texts = {}
    for test_name, path in dict_of_paths.items():
        try:
            with open(path) as file_to_read:
                dict_of_texts[test_name] = file_to_read.read()
        except IOError:
            dict_of_texts[test_name] = None
    return dict_of_texts


def check_by_blacklist(checks, dict_of_texts, password):
    for test_name, text in dict_of_texts.items():
        if text:
            checks[test_name] = not (password.lower() in text.split('\n'))
        else:
            checks[test_name] = None
    return checks


def check_errors(checks):
    errors = ''
    for test_name, result in checks.items():
        if result is None:
            errors += 'Attention! {} test was skipped\n'.format(str(test_name))
            checks[test_name] = 1  # Test was skipped, but we trust to user
    return errors


if __name__ == '__main__':

    minimum_strenght = 1
    maximum_strenght = 10
    min_len_value = -2
    max_len_value = 2
    len_of_best_password = 16
    charsets_coeff = 4
    formats_coeff = 1
    blacklists_coeff = 3

    recommends_dict = {
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
            errors = check_errors(checks)
            if errors:
                print(colorize(errors, 'red'))

            maximum_check_range = max_len_value + (
                charsets_coeff * checks['max_charsets_rate'] +
                formats_coeff * checks['max_formats_rate'] +
                blacklists_coeff * len(blacklist_files)
                )

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
                summ_matched_keys_values(checks, blacklist_files)
                )

            check_result = sum(
                [len_value,
                 charset_value,
                 format_value,
                 blacklist_value]
                )

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
                [recommends_dict[test_name] for test_name in checks.keys()
                 if test_name in recommends_dict and checks[test_name] < 1 or (
                     test_name == 'len' and (
                         checks[test_name] < len_of_best_password
                         )
                     )]
                )

            print(colorize('\nYour password strength: {}'.format(
                str(password_strength)), color)
                )

            print(colorize(
                recommends and 'RECOMMENDATIONS:\n\n{}\n'.format(recommends)
                or 'Great! Your password is strong, ' +
                   'but how do you remember it?\n', color
                ))
