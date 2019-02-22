import platform
import os

from selenium import webdriver

from ftl.ftl.settings import BASE_DIR


if platform.system().startswith('Linux'):
    executable_path = 'tests/geckodriver/geckodriver64_linux'
elif platform.system().startswith('Windows'):
    executable_path = 'tests/geckodriver/geckodriver64.exe'
elif platform.system().startswith('Darwin'):
    executable_path = 'tests/geckodriver/geckodriver64_linux'
else:
    raise EnvironmentError('Platform not supported')

browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path))
browser.get('http://localhost:8000')

assert 'Ftl-app' in browser.title
