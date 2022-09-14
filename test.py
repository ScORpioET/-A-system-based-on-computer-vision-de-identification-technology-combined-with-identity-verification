import socket
from requests import get


print(get('https://api.ipify.org/').text)