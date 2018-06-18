import os  
import sys
import getpass
from selenium import webdriver  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options

# enter your login credentials for kicktipp
print('*** KICKTIPP BOT ***')
print('Make sure chromedriver (http://chromedriver.chromium.org/) is in your PATH')
print('Enter your login credentials for kicktipp.de:')
YOUR_GAME_ID = input('Game ID: ')
YOUR_USERNAME = input('Name: ')
YOUR_PASSWORD = getpass.getpass('Password: ')

# definition of goal predictor
# be aware of the following shortcomings of this goal predictor
#  - only quotes for draw, win and loss are used
#  - if draw is the most probable the outcome is set to 0:0
#  - otherwise the quote of winning is used to calculate the difference of goals in the outcome of the game
#  - no goals are assumed to be scored by the loosing party
#  - this could be improved by using probabilities from bwin.com or others on the exact outcome of the game
def gamePrediction(heimQuote, drawQuote, gastQuote):
    MAXGOALS = 4
    if drawQuote < heimQuote and drawQuote < gastQuote: # a draw is most probable
        return [0,0]
    if heimQuote < gastQuote: # left side winning is most probable
        return [max(1, round(1/heimQuote**2 * MAXGOALS)), 0]
    if gastQuote < heimQuote:
        return [0, max(1, round(1/gastQuote**2 * MAXGOALS))]

# start browser
print('Start browser ...')
chrome_options = Options()  
chrome_options.add_argument('--headless') # remove to run in window mode
chrome_options.add_argument('log-level=3') # surpress output
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('test-type')
driver = webdriver.Chrome(chrome_options=chrome_options)

# login
print('Login ... ', end='')
driver.get('https://www.kicktipp.de/info/profil/login')
driver.find_element_by_id('kennung').send_keys(YOUR_USERNAME)
driver.find_element_by_id('passwort').send_keys(YOUR_PASSWORD)
driver.find_element_by_id('passwort').submit()
if driver.find_elements_by_css_selector("[class*='success']"):
    print('successful')
if driver.find_elements_by_css_selector("[class*='errors']"):
    print('failed')
    sys.exit('Name or password incorrect.')

# go to right game
print('Get general information ... ', end='')
driver.get('https://www.kicktipp.de/' + YOUR_GAME_ID + '/gesamtuebersicht')
# check that game id exists and if it exists that you are part of this game
if driver.title == 'Tipprunde nicht gefunden. | kicktipp' or driver.title == 'Die Seite konnte nicht gefunden werden | kicktipp':
    sys.exit('Game ID \'' + YOUR_GAME_ID + '\' not found')
table = driver.find_elements_by_id('ranking') # get table
if not table:
	sys.exit('Game ID \'' + YOUR_GAME_ID + '\' not found')
row = table[0].find_elements_by_css_selector("[class*='treffer']")
if not row:
	sys.exit('You are not part of the game \'' + YOUR_GAME_ID + '\'.')
# get number of days
rows = table[0].find_elements_by_css_selector('tr') # get all rows of table
col_count = len(rows[1].find_elements_by_css_selector('th')) # count number of columns of second row
day_count = col_count - 5 # substract other columns
# get current position
row = table[0].find_elements_by_css_selector("[class*='treffer']")
curPos = row[0].find_elements_by_css_selector("[class*='position']")[0].text
print('you are currently ' + curPos + '.')

print('Loop over all days in tournament ... ', end='')
# loop over all days and set bets
for i in range(0, day_count):
    print(str(i+1), end=', ')
    sys.stdout.flush()
    driver.get('https://www.kicktipp.de/' + YOUR_GAME_ID + '/tippabgabe?&spieltagIndex=' + str(i+1))
    table = driver.find_element_by_id('tippabgabeSpiele')
    for row in table.find_elements_by_css_selector('tr'):
        quote = row.find_elements_by_css_selector("[class*='kicktipp-wettquote']")
        heimTipp = row.find_elements_by_css_selector("[id*='_heimTipp']")
        gastTipp = row.find_elements_by_css_selector("[id*='_gastTipp']")
        if heimTipp and gastTipp and quote: # open to set bet
            heimQuote = float(quote[0].text.replace(',', '.'))
            drawQuote = float(quote[1].text.replace(',', '.'))
            gastQuote = float(quote[2].text.replace(',', '.'))
            goalsPredicted = gamePrediction(heimQuote, drawQuote, gastQuote)
            heimTipp[0].clear()
            heimTipp[0].send_keys(str(goalsPredicted[0]))
            gastTipp[0].clear()
            gastTipp[0].send_keys(str(goalsPredicted[1]))
    if heimTipp and gastTipp and quote: gastTipp[0].submit()
    
# close browser
print('done!')
driver.close()
print('*** KICKTIPP BOT ***')

# wait to close window
input('Press any key to quite...')