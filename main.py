import logging as lg

lg.basicConfig(level=lg.INFO, format='[Log] %(msg)s')

lg.info('Importing dependences...')

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common import by
from selenium.webdriver import Chrome
import matplotlib.pyplot as plt
from pyautogui import press, click
import PySimpleGUI as sg
from time import sleep
from math import ceil
import requests as r
import pandas as pd
from gui import *
import bs4


def amazon_scrap(search, browser, pagesToTun=1):
    global div_class, title_class, price_class
    lg.info('Opening [Amazon]')
    browser.get('https://www.amazon.com')  # Opening the site on a browser
    lg.info('Waiting the load...')
    browser.implicitly_wait(30)  # Max time to wait the load
    lg.info('Load complete, accessing the search bar')
    browser.find_element(by.By.ID, 'twotabsearchtextbox').send_keys(search)  # Find and use the search bar
    press('enter')  # send the keys
    lg.info('Input submitted, waiting the load')
    values = []  # 30-72 items
    sleep(3)
    for p in range(0, pagesToTun):  # 6 search pages = 120-300 elements
        sleep(2)
        lg.info(f'Capturing products of page: {p + 1}...')
        divs = browser.find_elements(by.By.CSS_SELECTOR, '[class="sg-col-inner"]')  # Find all items
        for c in range(len(divs)):  # Get data of the item
            code = bs4.BeautifulSoup(divs[c].get_attribute('outerHTML'), 'html.parser')
            title = code.find('span', 'a-text-normal')
            price = code.find('span', 'a-price-whole')
            try:
                values.append([title.text, int(str(price.text).replace('.', ''))])
            except Exception as e:
                pass
        ul = browser.find_element(by.By.CLASS_NAME, 'a-pagination')
        ul.find_element(by.By.CLASS_NAME, 'a-last').click()  # Go to next search page
    if values:  # All done, return the DataFrame resumed
        lg.info('[Amazon] Scrape concluded, closing browser and saving data...')
        df = pd.DataFrame(values, columns=['Product Names', 'Prices'])
        return [ceil(df["Prices"].mean()), len(values), ceil(df["Prices"].sum())]
    else:  # ^ Prices media - items processed - total value of all items ^
        print('\nError: Can\'t locate html elements on this page')
        print('Check if the page looks like this: https://www.amazon.com/s?k=outfit')
        print('This script don\'t work for some Amazon pages, try search for hardware or common things, like chairs\n')


def shopee_scrap(search, browser):
    lg.info('Opening [Shopee]')
    browser.get('https://shopee.com')
    lg.info('Waiting the load')
    # browser.implicitly_wait(30)
    sleep(10)
    click(180, 400) # close the pop up
    lg.info('Load complete, accessing and using the search bar')
    browser.find_element(by.By.CLASS_NAME, 'shopee-searchbar-input__input').send_keys(search)  # Get and use to search
    press('enter')  # Send the keys
    sleep(4)  # Load time, this will be wbd wait in future like others sleep()
    lg.info('Load complete, scraping the page 1')
    for c in range(0, 6):  # Run the page to render and load all items (55-60)
        lg.info(f'Rendering products; progress ({c + 1}/6)')
        for p in range(0, 17):  # Press the down_arrow 17 times, do this 6 times
            press('down')  # If the user interact with the browser this will probably break
    divs = browser.find_elements(by.By.CSS_SELECTOR, '[class="col-xs-2-4 shopee-search-item-result__item"]')  # Get them
    values = []
    for c in range(len(divs)):  # Extract the information about the product
        code = bs4.BeautifulSoup(divs[c].get_attribute('outerHTML'), 'html.parser')
        title = code.find('div', '_10Wbs- _5SSWfi UjjMrh')
        price = code.find('span', '_1d9_77')
        try:
            values.append([title.text.strip(), int(str(price.text).replace('R$', ''))])  # Sometimes, return Attribute e
        except:  # Some .text values in titles are like "text". In this case, the text need to be picked manually
            try:  # Other error can occurred with price if he are bigger than 999.00 he receive 2+ points 1.000.00
                title = str(title).replace('<div class="_10Wbs- _5SSWfi UjjMrh">', '').replace('</div>', '')
                price = str(price).replace('<span class="_1d9_77">', '').replace('</span>', '').replace('\"',
                                                                                                        '').replace(',',
                                                                                                                    '.')
                try:
                    values.append([title.strip(), float(price)])  # Prices can return errors
                except:  # This code fix the None value at price variable
                    if price.count('.') >= 2:  # 1.000.00
                        while price.count('.') >= 2:
                            price = price[:-3]  # Remove .00
                    values.append([title.strip(), int(price.replace('.', '').replace('R$', ''))])
            except Exception as e:  # If unexpected error occurred
                pass
    if values:  # All done, return the info
        lg.info('[Shopee] Scrape concluded, closing browser and saving data...')
        df = pd.DataFrame(values, columns=['Product Names', 'Prices'])
        return [ceil(df["Prices"].mean()), len(values), ceil(df["Prices"].sum())]
    else:
        print('\nError: Can\'t locate html elements on this page (shopee.com)')


def graph_output(search, data):
    lg.info('Reading data...')
    dt_tb = pd.DataFrame(  # Load DataFrame to extract info
        data,
        columns=['Prices media', 'Items analyzed', 'Sum of all'],
        index=['Amazon', 'Shopee']
    )
    items_analyzed = dt_tb['Items analyzed'].values  # Values iterator    (random ascii that I make; inset/spaceship)
    prices_media = dt_tb['Prices media'].values  # Values iterator
    lg.info('Archiving data...')  # ;-;                                                ##          \/-kh}---|k
    file = open('database.txt', 'a')  # Saving the data -- on a text file           --####  -       \/-eo}--|h
    file.write(f'{search}\n{prices_media[0]} {prices_media[1]}\n')  # #               #  ##          \/-vy}-|b
    file.close()  # Close                                                           --####  -         \/-bz}|y
    lg.info('Generating graphics...')  # ;-; 2                                         ##              \/\/\|z
    plt.pie(  # Relation of items processed for each site scraped
        [items_analyzed[0], items_analyzed[1]],  # Values
        labels=['Amazon', 'Shopee'],  # Labels
        autopct="%1.2f%%",  # Show the percentage
        colors=['orange', 'red'],  # Define the colors
    )  # Generating gui graphics - Amazon, Shopee, x?  (consider this on line +- 97)
    plt.title(f'Items processed for site - Search tab: \"{search}\"')
    plt.xlabel(f'Total of items captured: {dt_tb["Items analyzed"].values[0] + dt_tb["Items analyzed"].values[1]}')
    plt.ylabel(f' Amazon: {items_analyzed[0]}{" " * 30}\nShopee: {items_analyzed[1]}{" " * 30}').set_rotation(0)
    plt.show()
    plt.bar(  # Prices media graph (bars)
        ['Amazon', 'Shopee'],  # Legends, values
        [prices_media[0], prices_media[1]],
        color=['orange', 'red'])
    plt.title(f'Prices media - {search}')
    plt.xlabel('Scraped sites')
    plt.show()
    searches = []
    amazon_l = []
    shp_l = []
    file = open('database.txt', 'r')
    lg.info('Loading database for generate plot graph')
    c = 0
    for line in file.readlines():
        c += 1
        if c % 2 != 0:  # Search
            searches.append(str(line)[:-1])  # Remove \n
        else:  # Prices
            line_iter = line.split()
            for i in range(len(line_iter)):
                line_iter[i] = int(line_iter[i])
                if i % 2 != 0:  # [1]
                    shp_l.append(line_iter[i])
                else:  # [0]
                    amazon_l.append(line_iter[i])
    file.close()
    plt.figure(facecolor='#cccccc')
    ax = plt.axes()
    ax.set_facecolor("#dddddd")
    plt.plot(searches, amazon_l, color='orange', marker='o')
    plt.plot(searches, shp_l, color='red', marker='o')
    plt.title(f'Prices media plot - Last search')
    plt.legend(['Amazon', 'Shopee'])
    plt.grid()
    plt.show()


def start(search):
    lg.info('Input received, testing sites response')
    try:
        amazon = r.get('https://www.amazon.com')  # Probably return 503
        # shopee = r.get('https://www.submarino.com')  # Too much time to respond
        if amazon.status_code == 404:
            print('Error: [https://www.amazon.com] Not found 404\n')
        else:  # Automation initialization
            lg.info('All done, initializing the process')
            data = [
                amazon_scrap(search, Chrome(), 2),
                shopee_scrap(search, Chrome())
            ]
            lg.info('Scan ended, processing the results')
            graph_output(search, data)  # Show the results
    except:
        pass


def gui():
    lg.info('Done, waiting the user input')
    sg.theme('Dark Grey13')
    title = 'KevBoyz Tools      E-commerce Scraping'
    layout = [[title_bar(title, sg.theme_button_color()[0], sg.theme_button_color()[1])],
              [sg.T('Search for:'), sg.Input(size=(35, 0))],
              [sg.Button('Start', size=(40, 0))]]
    window_main = sg.Window(title, layout, resizable=True, no_titlebar=True, grab_anywhere=True, keep_on_top=True,
                            margins=(0, 0), finalize=True)
    window_main['-TITLEBAR-'].expand(True, False, False)
    while True:  # Event Loop
        window, event, values = sg.read_all_windows(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == '-MINIMIZE-':
            minimize_main_window(window_main)
            continue
        elif event == '-RESTORE-' or (event == sg.WINDOW_CLOSED and window != window_main):
            restore_main_window(window_main)
            continue
        else:
            if event == 'Start':  # Button event
                window.close()
                return values[0]
    window.close()


while True:  # Execution loop
    lg.info('Loading graphical interface')
    search = str(gui()).strip()
    if search == 'None':
        quit(0)
    elif search.find('www.amazon.com') != -1 or search.find('https://www.') != -1:  # Invalid values processing
        print('\nError: This input don\'t accept URL\'s')
        print('Do a search like: \"pc\" or \"cpu\"\n')
    else:
        start(search)
        lg.info('All concluded, restarting the loop')

