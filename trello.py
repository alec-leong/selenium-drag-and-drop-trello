import os
from path import chromedriver_rel_path
from datetime import datetime as dt
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from random import randint

load_dotenv()


class TasksError(Exception):
    pass


class Trello:
    __email = os.getenv('TRELLO_EMAIL')
    __password = os.getenv('TRELLO_PASSWORD')
    __url = 'https://trello.com/'

    def __init__(self,
                 email=None,
                 password=None,
                 team_name='Software QA',
                 team_description='Atlassian’s QA team works with development teams to help ship features quickly and '
                                  'safely.',
                 board_title=f'Sprint {dt.now().strftime("%m/%d")} - '
                             f'{dt.fromtimestamp(dt.now().timestamp() + 2 * 7 * 24 * 60 * 60).strftime("%m/%d")}',
                 tasks=({
                     'name': 'TO DO',
                     'cards': ['Learn Selenium', 'Learn Jenkins']
                 }, {
                     'name': 'LO'
                 }, {
                     'name': 'MD',
                 }, {
                     'name': 'HI'
                 })):
        self.__email = Trello.__email if email is None else email
        self.__password = Trello.__password if password is None else email
        self.__team_name = team_name
        self.__team_description = team_description
        self.__board_title = board_title
        self.__tasks = tasks
        self.is_tasks_valid()
        self.__driver = webdriver.Chrome(chromedriver_rel_path)
        self.__driver.maximize_window()
        self.__driver.implicitly_wait(4)

    def is_tasks_valid(self):
        # Check length of tasks.
        n = len(self.__tasks)

        # Require at least two tasks.
        if n < 2:
            raise TasksError(f'Tasks tuple length error.\n\tActual: {n}\n\tExpected: length >= 2')

        # Check if there exists a task with one or more cards.
        for i, task in enumerate(self.__tasks):
            try:
                cards = task['cards']
            except KeyError:
                continue
            else:
                if len(cards) == 0:
                    continue
                # There exists a task with one or more cards.
                else:
                    return

        # There does not exist a task with one or more cards.
        raise TasksError('Task cards length error. Expected at least one task with one or more cards.')

    def login(self):
        self.__driver.get(Trello.__url)
        self.__driver.find_element_by_link_text('Log in').click()
        ActionChains(self.__driver).send_keys(self.__email).perform()
        self.__driver.find_element_by_id('password').send_keys(self.__password)
        self.__driver.find_element_by_id('login').click()
        WebDriverWait(self.__driver, 4)\
            .until(expected_conditions.title_is('Log in to continue - Log in with Atlassian account'))
        ActionChains(self.__driver).send_keys(self.__password).perform()
        self.__driver.find_element_by_id('login-submit').click()

        print('Log in successful...')

    def build_team(self):
        self.__driver.find_element_by_class_name('icon-add').click()
        ActionChains(self.__driver).send_keys(self.__team_name).perform()
        team_type = self.__driver.find_element_by_xpath('//label[@for="teamTypeSelect"]/following-sibling::div')
        ActionChains(self.__driver).move_to_element(team_type).click().move_by_offset(104, 32).click().perform()
        self.__driver.find_element_by_css_selector('textarea[id*="create-team-org-description"]')\
            .send_keys(self.__team_description)
        self.__driver.find_element_by_css_selector('button[data-test-id*="create-team-submit-button"]').click()
        WebDriverWait(self.__driver, 4)\
            .until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-test-id="show-later-button"]'))
            ).click()

        print('Build team successful...')

    def create_new_board(self):
        WebDriverWait(self.__driver, 4).until(expected_conditions.title_contains(self.__team_name))
        self.__driver.find_element_by_css_selector('div.board-tile').click()
        self.__driver.find_element_by_css_selector('input[data-test-id="create-board-title-input"]')\
            .send_keys(self.__board_title)
        self.__driver.find_element_by_css_selector('button[data-test-id="create-board-submit-button"]').click()

        print('Create new board successful...')

    def init_tasks(self):
        WebDriverWait(self.__driver, 4).until(expected_conditions.title_contains(f'{self.__board_title} | Trello'))

        # Initialize tasks
        for i, task in enumerate(self.__tasks):
            # Add task.
            ActionChains(self.__driver).send_keys(task['name']).perform() \
                if i == 0 \
                else self.__driver.find_element_by_css_selector('input.list-name-input').send_keys(task['name'])
            self.__driver.find_element_by_css_selector('[value="Add List"]').click()

            # Add cards to task.
            try:
                for j, card in enumerate(task['cards']):
                    self.__driver.find_element_by_xpath('//span[text()="Add a card"]').click()\
                        if j == 0\
                        else self.__driver.find_element_by_css_selector('input[value="Add Card"]').click()
                    ActionChains(self.__driver).send_keys(card).perform()
                    self.__driver.find_element_by_css_selector('input[value="Add Card"]').click()
            except KeyError:
                continue

        # Close menu.
        self.__driver.find_element_by_css_selector('a[title="Close the board menu."]').click()

        print('Initializing tasks successful...')

    def rand_drag_all_cards(self):
        src = {}
        target = {}
        idx = len(self.__tasks) - 1

        # Initialize random source task of cards to drag.
        while True:
            src['idx'] = randint(0, idx)
            task = self.__tasks[src['idx']].copy()

            try:
                cards = task['cards']
            except KeyError:
                continue
            else:
                if len(cards) != 0:
                    src['name'] = task['name']
                    src['cards'] = task['cards']
                    break

        # Initialize random target task to drop cards at.
        target['idx'] = randint(0, idx)

        while target['idx'] == src['idx']:
            target['idx'] = randint(0, idx)

        task = self.__tasks[target['idx']].copy()
        target['name'] = task['name']

        # Execute Selenium Actions drag and drop
        drop_location = self.__driver.find_element_by_xpath(f'//h2[text()="{target["name"]}"]/parent::div/div')

        for card in src['cards']:
            xpath = f'//h2[text()="{src["name"]}"]/parent::div/following-sibling::div ' \
                    f'//span[text()="{card}"]/parent::div'
            drag_card = self.__driver.find_element_by_xpath(xpath)
            ActionChains(self.__driver).drag_and_drop(drag_card, drop_location).perform()

        # Update tasks property.
        cards = self.__tasks[src['idx']]['cards'].copy()
        del self.__tasks[src['idx']]['cards']
        try:
            self.__tasks[target['idx']]['cards'] + cards
        except KeyError:
            self.__tasks[target['idx']]['cards'] = cards

        print('Random drag and drop successful...')
