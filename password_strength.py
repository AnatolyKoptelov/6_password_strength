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


def check_by_patterns(checks, password):

    def summ_matched_values(results_dict, list_of_tests):
        return sum(
            [results_dict[test] for test in list_of_tests if isinstance(
                results_dict[test], int
            )]
        )

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
        checks[test_name] = (function(password) is not None) == logic
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


def check_by_stoplists(checks, dict_of_texts, password):
    checks['stoplists'] = 0
    checks['max_stoplists_rate'] = len(dict_of_texts)
    for test_name, text in dict_of_texts.items():
        if text:
            checks[test_name] = not (password.lower() in text.split('\n'))
            checks['stoplists'] += checks[test_name]
        else:
            checks[test_name] = None
            checks['stoplists'] += 1  # Test was skipped, but we trust to user
    return checks


def check_errors(checks):
    errors = ''
    for test_name, result in checks.items():
        if result is None:
            errors += 'Attention! {} test was skipped\n'.format(str(test_name))
            checks[test_name] = 1  # Test was skipped, but we trust to user
    return checks, errors


if __name__ == '__main__':

    minimum_strength = 1
    maximum_strength = 10
    min_len_value = -2
    max_len_value = 2
    len_of_best_password = 16
    charsets_coeff = 4
    formats_coeff = 1
    stoplists_coeff = 3

    recommends_dict = {
        'len': 'Your password is too short. Increase it length!',
        'digits': 'Use numerical digits for increasing strength!',
        'loletters': 'Use lower-case letters for increasing strength!',
        'upletters': 'Use upper-case letters for increasing strength!',
        'symbols': 'Use special chars, such as @, #, for increasing strength!',
        'dateformat': '{}{}'.format(
            'Your password match the format of calendar dates, ',
            'change your password!'
        ),
        'blacklist': '{}{}'.format(
            'Your password found in a password blacklist, ',
            'change it immediately!'
        ),
        'names': 'Your password found in a names list, change it immediately!',
    }
    password = ' '
    while password:
        password = getpass.getpass(
                prompt='Input a password for checking or tap Enter for exit: ')
        if password:
            checks = {
                'len': len(password)
            }
            checks = check_by_patterns(checks, password)
            stoplists_files = {
                'blacklist': './10_million_password_list_top_100000.txt',
                'names': './names.txt',
            }
            checks = check_by_stoplists(
                checks,
                read_files(stoplists_files),
                password,
            )
            checks, errors = check_errors(checks)
            print(checks)
            if errors:
                print(colorize(errors, 'red'))

            maximum_check_range = max_len_value + (
                charsets_coeff * checks['max_charsets_rate'] +
                formats_coeff * checks['max_formats_rate'] +
                stoplists_coeff * checks['max_stoplists_rate']
                )

            len_value = get_rate(
                minimum=min_len_value,
                maximum=max_len_value,
                best_value=len_of_best_password,
                current_value=checks['len']
            )

            charset_value = charsets_coeff * checks['charsets']
            format_value = formats_coeff * checks['formats']
            stoplist_value = stoplists_coeff * checks['stoplists']

            check_result = sum(
                [len_value,
                 charset_value,
                 format_value,
                 stoplist_value]
                )

            password_strength = get_rate(
                minimum=minimum_strength,
                maximum=maximum_strength,
                best_value=maximum_check_range,
                current_value=check_result
            )

            color = get_color(
                minimum=minimum_strength,
                maximum=maximum_strength,
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
                or '{}{}'.format(
                    'Great! Your password is strong, ',
                    'but how do you remember it?\n'
                ),
                color
                )
            )
