try:
  from json import loads, dumps
except:
  from ujson import loads, dumps

def read_ds_sensor():
  roms = ds_sensor.scan()
  print('Found DS devices: ', roms)
  print('Temperatures: ')
  ds_sensor.convert_temp()
  for rom in roms:
    temp = ds_sensor.read_temp(rom)
    if isinstance(temp, float):
      msg = round(temp, 2)
      print(temp, end=' ')
      print('Valid temperature')
      return msg
  return b'0.0'


def web_page():
  with open("index.html") as html:
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request, 'UTF-8')
    print('Content = %s' % request)
    if request.find("GET / HTTP/1.1") != -1:
      response = web_page().read()
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: text/html\n')
      conn.send('Connection: close\n\n')
      conn.sendall(response)
      response.close()
    elif request.find('GET /pega_temp HTTP/1.1') != -1:
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: application/json\n')
      conn.send('Connection: close\n\n')
      temp = read_ds_sensor()
      conn.sendall(dumps(str(temp)))
      
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')