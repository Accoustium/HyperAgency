import http.cookiejar
import re
import urllib
import sqlite3

from hstest.django_test import DjangoTest, TEST_DATABASE
from hstest.check_result import CheckResult


INITIAL_USERS = [
    (1, 'Lemon_2059', 'contemp2015@protonmail.com', True),
    (2, 'RuthlessnessSirens-1882', 'oversured1842@yahoo.com', True),
    (3, 'moping_1935', 'tenons1970@outlook.com', True),
    (4, 'MillagePenstemon-1843', 'chrisman1923@yandex.com', True),
    (5, 'Archeus.1930', 'concentric1895@gmail.com', True),
    (6, 'BenzalazineCurite.1832', 'quassiin1927@live.com', True),
    (7, 'Bossa-1831', 'breena1977@live.com', False),
    (8, 'ClinkChinho_2027', 'adansonia1808@gmail.com', False),
    (9, 'RepassableTournefortian.1973', 'vomer1822@yahoo.com', False),
    (10, 'debenture-1898', 'average2014@yahoo.com', False),
]

INITIAL_VACANCIES = [
    (1, 'Botanist'),
    (2, 'Signwriter'),
    (3, 'Stewardess'),
    (4, 'Medical Secretary'),
    (5, 'Stone Cutter'),
    (6, 'Musician'),
]

INITIAL_RESUMES = [
    (7, 'Charge Hand'),
    (8, 'Occupations'),
    (9, 'Milklady'),
    (10, 'Auctioneer'),
]


class HyperJobTest(DjangoTest):
    USERNAME = 'Sparrow_1949'
    PASSWORD = 's<myW8Dh'
    OCCUPATION = 'Flower Arranger'

    ELEMENT_PATTERN = '''<a[^>]+href=['"](?P<href>[a-zA-Z/_]+)['"][^>]*>'''
    cookie_jar = http.cookiejar.CookieJar()

    def check_create_resume_from_profile(self) -> CheckResult:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/home')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the home page.')

        csrf_options = re.findall(
            b'<input[^>]+value="(?P<csrf>\w+)"[^>]*>', response.read()
        )
        if not csrf_options:
            return CheckResult.false('Missing csrf_token in the form')

        try:
            response = opener.open(
                f'http://localhost:{self.port}/resume/new',
                data=urllib.parse.urlencode({
                    'description': self.OCCUPATION,
                    'csrfmiddlewaretoken': csrf_options[0],
                }).encode()
            )
        except urllib.error.URLError as err:
            return CheckResult.false(f'Cannot create resume: {err.reason}')

        try:
            page = self.read_page(f'http://localhost:{self.port}/resumes')
            description = f'{self.USERNAME}: {self.OCCUPATION}'
            if description not in page:
                return CheckResult.false(
                    f'Resumes page does not contain newly created resume'
                )
            return CheckResult.true()
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the resumes page.')

    def check_create_resumes(self) -> CheckResult:
        connection = sqlite3.connect(TEST_DATABASE)
        cursor = connection.cursor()
        try:
            cursor.executemany(
                'INSERT INTO auth_user '
                '(`id`, `username`, `email`, `is_staff`, `password`, `is_superuser`, '
                '`first_name`, `last_name`, `is_active`, `date_joined`) '
                'VALUES (?, ?, ?, ?, "", 0, "", "", 1, datetime())',
                INITIAL_USERS[len(INITIAL_VACANCIES):]
            )
            cursor.executemany(
                'INSERT INTO resume_resume (`author_id`, `description`) VALUES (?, ?)',
                INITIAL_RESUMES
            )
            connection.commit()

            cursor.execute('SELECT `author_id`, `description` FROM resume_resume')
            result = cursor.fetchall()

            for item in INITIAL_RESUMES:
                if item not in result:
                    return CheckResult.false('Check your Resume model')
            return CheckResult.true()

        except sqlite3.DatabaseError as err:
            return CheckResult.false(str(err))

    def check_create_vacancies(self) -> CheckResult:
        connection = sqlite3.connect(TEST_DATABASE)
        cursor = connection.cursor()
        try:
            cursor.executemany(
                'INSERT INTO auth_user '
                '(`id`, `username`, `email`, `is_staff`, `password`, `is_superuser`, '
                '`first_name`, `last_name`, `is_active`, `date_joined`) '
                'VALUES (?, ?, ?, ?, "", 0, "", "", 1, datetime())',
                INITIAL_USERS[:len(INITIAL_VACANCIES)]
            )
            cursor.executemany(
                'INSERT INTO vacancy_vacancy (`author_id`, `description`) VALUES (?, ?)',
                INITIAL_VACANCIES
            )
            connection.commit()

            cursor.execute('SELECT `author_id`, `description` FROM vacancy_vacancy')
            result = cursor.fetchall()

            for item in INITIAL_VACANCIES:
                if item not in result:
                    return CheckResult.false('Check your Vacancy model')
            return CheckResult.true()

        except sqlite3.DatabaseError as err:
            return CheckResult.false(str(err))

    def check_forbid_anonymous_create(self) -> CheckResult:
        opener = urllib.request.build_opener()
        try:
            response = opener.open(f'http://localhost:{self.port}/home')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the home page.')

        csrf_options = re.findall(
            b'<input[^>]+value="(?P<csrf>\w+)"[^>]*>', response.read()
        )
        if not csrf_options:
            return CheckResult.true()

        OTHER_OCCUPATION = 'Marketing Coordinator'

        try:
            response = opener.open(
                f'http://localhost:{self.port}/resume/new',
                data=urllib.parse.urlencode({
                    'description': OTHER_OCCUPATION,
                    'csrfmiddlewaretoken': csrf_options[0],
                }).encode()
            )
            return CheckResult.false('Should not allow anonymous users create resumes')
        except urllib.error.URLError as err:
            if 'Forbidden' not in err.reason:
                return CheckResult.false(f'Wrong response for forbidden requests: {err.reason}')

        try:
            page = self.read_page(f'http://localhost:{self.port}/resumes')
            if OTHER_OCCUPATION in page:
                return CheckResult.false(
                    f'Resumes page should not contain resumes from anonymous users'
                )
            return CheckResult.true()
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the resumes page.')

    def check_forbid_to_create_vacancy(self) -> CheckResult:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/home')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the home page.')

        csrf_options = re.findall(
            b'<input[^>]+value="(?P<csrf>\w+)"[^>]*>', response.read()
        )
        if not csrf_options:
            return CheckResult.true()

        OTHER_OCCUPATION = 'Marketing Coordinator'

        try:
            response = opener.open(
                f'http://localhost:{self.port}/vacancy/new',
                data=urllib.parse.urlencode({
                    'description': OTHER_OCCUPATION,
                    'csrfmiddlewaretoken': csrf_options[0],
                }).encode()
            )
            return CheckResult.false('Should not allow usual users create vacancies')
        except urllib.error.URLError as err:
            if 'Forbidden' not in err.reason:
                return CheckResult.false(f'Wrong response for forbidden requests: {err.reason}')

        try:
            page = self.read_page(f'http://localhost:{self.port}/vacancies')
            if OTHER_OCCUPATION in page:
                return CheckResult.false(
                    f'Vacancies page should not contain vacancies from usual users'
                )
            return CheckResult.true()
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the vacancies page.')

    def check_greeting(self) -> CheckResult:
        try:
            main_page = self.read_page(f'http://localhost:{self.port}')
            if 'Welcome to HyperJob!' in main_page:
                return CheckResult.true()
            return CheckResult.false(
                'Main page should contain "Welcome to HyperJob!" line'
            )
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the menu page.'
            )

    def check_links(self) -> CheckResult:
        try:
            page = self.read_page(f'http://localhost:{self.port}')
            links = re.findall(self.ELEMENT_PATTERN, page)
            for link in (
                '/login',
                '/signup',
                '/vacancies',
                '/resumes',
                '/home',
            ):
                if link not in links:
                    return CheckResult.false(
                        f'Menu page should contain <a> element with href {link}'
                    )
            return CheckResult.true()
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the menu page.'
            )

    def check_login(self) -> CheckResult:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        try:
            response = opener.open(f'http://localhost:{self.port}/login')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the login page.')

        csrf_options = re.findall(
            b'<input[^>]+value="(?P<csrf>\w+)"[^>]*>', response.read()
        )
        if not csrf_options:
            return CheckResult.false('Missing csrf_token in the form')

        try:
            response = opener.open(
                f'http://localhost:{self.port}/login',
                data=urllib.parse.urlencode({
                    'csrfmiddlewaretoken': csrf_options[0],
                    'username': self.USERNAME,
                    'password': self.PASSWORD,
                }).encode()
            )
            if 'login' not in response.url:
                return CheckResult.true()
            return CheckResult.false('Cannot login: problems with form')
        except urllib.error.URLError as err:
            return CheckResult.false(f'Cannot login: {err.reason}')

    def check_resumes(self) -> CheckResult:
        try:
            page = self.read_page(f'http://localhost:{self.port}/resumes')
            for person, resume in zip(INITIAL_USERS[len(INITIAL_VACANCIES):], INITIAL_RESUMES):
                description = f'{person[1]}: {resume[1]}'
                if description not in page:
                    return CheckResult.false(
                        f'Resumes page should contain resumes in form <username>: <description>'
                    )
            return CheckResult.true()
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the resumes page.'
            )

    def check_signup(self) -> CheckResult:
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        try:
            response = opener.open(f'http://localhost:{self.port}/signup')
        except urllib.error.URLError:
            return CheckResult.false('Cannot connect to the signup page.')

        csrf_options = re.findall(
            b'<input[^>]+value="(?P<csrf>\w+)"[^>]*>', response.read()
        )
        if not csrf_options:
            return CheckResult.false('Missing csrf_token in the form')

        try:
            response = opener.open(
                f'http://localhost:{self.port}/signup',
                data=urllib.parse.urlencode({
                    'csrfmiddlewaretoken': csrf_options[0],
                    'username': self.USERNAME,
                    'password1': self.PASSWORD,
                    'password2': self.PASSWORD,
                }).encode()
            )
            if f'login' in response.url:
                return CheckResult.true()
            return CheckResult.false('Cannot signup: problems with form')
        except urllib.error.URLError as err:
            return CheckResult.false(f'Cannot signup: {err.reason}')

    def check_vacancies(self) -> CheckResult:
        try:
            page = self.read_page(f'http://localhost:{self.port}/vacancies')
            for person, vacancy in zip(INITIAL_USERS, INITIAL_VACANCIES):
                description = f'{person[1]}: {vacancy[1]}'
                if description not in page:
                    return CheckResult.false(
                        f'Vacancies page should contain vacancies in form <username>: <description>'
                    )
            return CheckResult.true()
        except urllib.error.URLError:
            return CheckResult.false(
                'Cannot connect to the vacancies page.'
            )
