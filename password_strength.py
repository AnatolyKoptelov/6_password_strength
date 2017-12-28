import re
import getpass


search_patterns = {
           'digits': re.compile('[0-9]'),
           'loletters': re.compile('[a-z]'),
           'upletters': re.compile('[A-Z]'),
           'symbols': re.compile('[\W_]')
           }

match_patterns = {
           'dateformat': re.compile(
                         """(0[1-9]|[12][0-9]|3[01])[- /.] # day
                         ?(0[1-9]|1[012])[- /.]            # month
                         ?((19|20)\d\d|\d\d$)              # year
                         """, re.X)
           }

files_to_search = {
           'blacklist': './10_million_password_list_top_100000.txt'
           }

RECOMMENDS = {
        'len': 'Your password is too short. Increase it lenght!',
        'digits': 'Use numerical digits for increasing strenght!',
        'loletters': 'Use lower-case letters for increasing strenght!',
        'upletters': 'Use upper-case letters for increasing strenght!',
        'symbols': 'Use special chars, such as @, #, for increasing strenght!',
        'dateformat': 'Your password match the format of calendar dates, ' +
                      'change your password!',
        'blacklist': 'Your password found in a password blacklist, ' +
                     'change it immediately!'
        }

# Weight of password's lenght
min_len_value = -2
max_len_value = 2
len_of_best_password = 16

# Weight of charset, format and blacklist tests
charset_coefficient = 4
format_coefficient = 1
blacklist_coefficient = 3

minimum_strenght = 1
maximum_strenght = 10

maximum_check_range = max_len_value +\
                charset_coefficient * len(search_patterns) +\
                format_coefficient * len(match_patterns) +\
                blacklist_coefficient * len(files_to_search)

def get_color(minimum, maximum, current):
    maximum_red = 0.4
    minimum_green = 0.7
    proportion = current/(maximum - minimum)
    return proportion <= maximum_red and 'red' or\
        proportion >= minimum_green and 'green' or 'yellow'


def str_to_colored(string, color):
    colors = {
          'red': '\x1b[1;31;40m',
          'yellow': '\x1b[1;33;40m',
          'green': '\x1b[1;32;40m',
          'reset': '\n\x1b[0m'
          }
    return '{}{}{}'.format(colors[color], string, colors['reset'])


def read_file(path):
    errors = ''
    try:
        with open(path) as file_to_read:
            read_data = file_to_read.read()
    except IOError as err:
        errors += '\nFile not found\n{}'.format(str(err))
        read_data = None
    return read_data, errors


def search_string(string, read_data):
    if read_data:
        for line in read_data.split('\n'):
            if line == string:
                return True
    else:
        return None
    return False


def get_rate(minimum, maximum, best_value, current_value):
    return minimum - 1 + int(pow(maximum - minimum + 1,
                             min(current_value, best_value)/best_value))


def summ_matched_keys_values(dict_1, dict_2):
    return sum([dict_1[key] for key in dict_2.keys()])


def charset_test(checks, search_patterns, password):
    for key, pattern in search_patterns.items():
        checks[key] = pattern.search(password) and 1 or 0
    return(checks)


def format_test(checks, match_patterns, password):
    for key, pattern in match_patterns.items():
        checks[key] = not pattern.match(password) and 1 or 0
    return(checks)


# Fuction is not proper (requires read_file, search_string)
def blacklist_test(checks, files_to_search, password):
    for key, path in files_to_search.items():
        read_data, errors = read_file(path)
        if read_data is not None:
            checks[key] = not search_string(password,
                                            read_data) and 1 or 0
        else:
            errors += '\nAttention, {} cheching was skipped!'.format(key) 
            checks[key] = 1  # Skipped, but we trust to user
    return checks, errors


if __name__ == '__main__':
    password = ' '
    while password:
        password = getpass.getpass(
                prompt='Input a password for checking or tap Enter for exit: ')
        if password:
            # Get tests results
            checks = {
                  'len': len(password)
                  }
            checks = charset_test(checks, search_patterns, password)
            checks = format_test(checks, match_patterns, password)
            checks, errors = blacklist_test(checks, files_to_search, password)
            if errors:
                print(str_to_colored(errors, 'red'))
            
            # Componets of strenght, based on different tests
            len_value = get_rate(minimum=min_len_value,
                                 maximum=max_len_value,
                                 best_value=len_of_best_password,
                                 current_value=checks['len'])

            charset_value = charset_coefficient * summ_matched_keys_values(
                                                   checks, search_patterns)
            format_value = format_coefficient * summ_matched_keys_values(
                                                   checks, match_patterns)
            blacklist_value = blacklist_coefficient * summ_matched_keys_values(
                                                   checks, files_to_search)

            check_result = len_value + charset_value + format_value +\
                blacklist_value

            password_strength = get_rate(minimum=minimum_strenght,
                                         maximum=maximum_strenght,
                                         best_value=maximum_check_range,
                                         current_value=check_result)

            color = get_color(minimum=minimum_strenght,
                              maximum=maximum_strenght,
                              current=password_strength)

            recommends = '\n'.join(
                [RECOMMENDS[key] for key in checks.keys()
                    if checks[key] < 1
                    or (key == 'len' and checks[key] < len_of_best_password)])

            print(str_to_colored('\nYour password strength: {}'.format(
                                             str(password_strength)), color))

            print(str_to_colored(
                recommends and 'RECOMMENDATIONS:\n\n{}\n'.format(recommends)
                or 'Great! Your password is strong, ' +
                   'but how do you remember it?\n', color))
