# Password Strength Calculator

Application for password strenght checking. Run **password_strength.py** on your terminal and type a password fro checking.
This application check password for:
 - Lenght
 - Charsets (containing numerical digit, lower-case and upper-case letter, special symbols)
 - Formate (not matching for a formate of calendar dates)
 - Blacklist (matching of one of must popular passwords)

Blacklist is in **10_million_password_list_top_100000.txt**

Password strenght range from 1(worst) to 10(best) and application give some recomendations for password strenght increasing.

# Quickstart

Run command in command line
```
python password_strength.py
```
and application will propose you to enter your password for rating
```
Input a password for checking or tap Enter for exit:
```
Then application will give you your password rating and recomendations for password streght increasing.
```
Your password strength: 1

RECOMMENDATIONS:

Your password is too short. Increase it lenght!
Use lower-case letters for increasing strenght!
Use upper-case letters for increasing strenght!
Use special chars, such as @, #, for increasing strenght!
```
# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
