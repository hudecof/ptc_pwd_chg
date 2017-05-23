#!/usr/bin/env python

import os
import sys
import traceback

import argparse
import logging

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

EXIT_CODE=os.EX_OK

def main(args):
    global EXIT_CODE

    driver = webdriver.PhantomJS(args.phantom_js)
    # main page
    driver.get("https://club.pokemon.com/us/")
    # click login link
    driver.get("https://club.pokemon.com/us/pokemon-trainer-club/login")
    el = driver.find_element_by_xpath("//form[@id='login-form']//input[@id='username']")
    el.clear()
    el.send_keys(args.login)
    el = driver.find_element_by_xpath("//form[@id='login-form']//input[@id='password']")
    el.clear()
    el.send_keys(args.current_password)
    el = driver.find_element_by_xpath("//form[@id='login-form']//input[@id='btnLogin']")
    el.click()
    try:
        el = driver.find_element_by_xpath("//form[@id='login-form']")
    except NoSuchElementException:
        logger.info("seems to be logged in")
    else:
        EXIT_CODE = os.EX_DATAERR
        driver.save_screenshot('login-error-screen.png')
        logger.error('could not login, see the screenshot')
        raise Exception('could not login, see the screenshot')

    # go to change password page
    driver.get('https://club.pokemon.com/us/pokemon-trainer-club/my-password')
    el = driver.find_element_by_xpath("//form[@id='account']//input[@id='id_current_password']")
    el.clear()
    el.send_keys(args.current_password)
    el = driver.find_element_by_xpath("//form[@id='account']//input[@id='id_password']")
    el.clear()
    el.send_keys(args.new_password)
    el = driver.find_element_by_xpath("//form[@id='account']//input[@id='id_confirm_password']")
    el.clear()
    el.send_keys(args.new_password)
    el = driver.find_element_by_xpath("//form[@id='account']//input[@type='submit']")
    el.click()
    try:
        el = driver.find_element_by_xpath("//form[@id='account']")
    except NoSuchElementException:
        logger.info("seems password is changed")
    else:
        EXIT_CODE = os.EX_DATAERR
        driver.save_screenshot('password_change-error-screen.png')
        logger.error('password not changed, see the screenshot')
        raise Exception('password not changed, see the screenshot')

     
def setup_logging(name=None, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pokemon Trainer Account Password Change.')
    parser.add_argument('-l', '--login', dest='login', action='store', required=True, help='input file type')
    parser.add_argument('-cp', '--current_password', dest='current_password', action='store', required=True, help='current password')
    parser.add_argument('-np', '--new_password', dest='new_password', action='store', required=True, help='new password')
    parser.add_argument('-pj', '--phantom_js', dest='phantom_js', action='store', default='./phantomjs/bin/phantomjs', help='PhatomJS binary')

    args = parser.parse_args()
    logger = setup_logging('ptc_pwd_chg', logging.INFO)

    try:
        main(args)
    except Exception:
        print('-'*60)
        traceback.print_exc(file=sys.stdout)
        print ('-'*60)
        logger.info('rollback due the exception')
        EXIT_CODE = os.EX_SOFTWARE if (EXIT_CODE != os.EX_OK) else EXIT_CODE

    sys.exit(EXIT_CODE)
