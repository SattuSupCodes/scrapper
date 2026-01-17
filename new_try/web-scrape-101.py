import socket
import re
import urllib3

HOST = 'www.google.com'  # Server hostname or IP address
PORT = 443               # The standard port for HTTP is 80, for HTTPS it is 443

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
client_socket.connect(server_address)

request_header = b'GET / HTTP/1.0\r\nHost: www.google.com\r\n\r\n'
client_socket.sendall(request_header)

response = ''
while True:
    recv = client_socket.recv(1024)
    if not recv:
        break
    response += recv.decode('utf-8')

print(response)
client_socket.close()
html_content = '<p>Price : 19.99$</p>'
pattern = r'Price\s*:\s*(\d+\.\d{2})\$'

match = re.search(pattern, html_content)
if match:
    print(match.group(1))  # Output: 19.99
# http = urllib3.PoolManager()
# r = http.request('GET', 'http://www.google.com')
# print(r.data)
user_agent_header = urllib3.make_headers(user_agent="<USER AGENT>")
pool = urllib3.ProxyManager('<PROXY IP>', headers=user_agent_header)
r = pool.request('GET', 'https://www.google.com/')