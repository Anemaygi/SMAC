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


def moving():
  old = "touchA = "+str(touchA.value())+" touchB: "+str(touchB.value())+" touchC: "+str(touchC.value())+" touchD: "+str(touchD.value())
  sleep(3)
  new = "touchA = "+str(touchA.value())+" touchB: "+str(touchB.value())+" touchC: "+str(touchC.value())+" touchD: "+str(touchD.value())
  if old != new:
    print("DEUUUUU TRUEEEEEEEEEEEEEEE")
    print("DEUUUUU TRUEEEEEEEEEEEEEEE")
    print("DEUUUUU TRUEEEEEEEEEEEEEEE")
    print("DEUUUUU TRUEEEEEEEEEEEEEEE")
    return True

  # if touchA.value() == 1:
  #   newMoving.append("A")
  # elif touchA.value() == 0:
  #   if "A" in newMoving:
  #     newMoving.remove("A")
  
  # if touchB.value() == 1:
  #   newMoving.append("B")
  # elif touchB.value() == 0:
  #   if "B" in newMoving:
  #     newMoving.remove("B")
  
  # if touchC.value() == 1:
  #   newMoving.append("C")
  # elif(touchC.value() == 0):
  #   if "C" in newMoving:
  #     newMoving.remove("C")
    
  # if touchD.value() == 1:
  #   newMoving.append("D")
  # elif touchD.value() == 0:
  #   if "D" in newMoving:
  #     newMoving.remove("D")
  
  # newMoving.sort()
  # oldMoving.sort()

  return False

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
      # response = web_page().read()
      with open("index.html", 'r') as html:
        response = html.read()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        html.close()

    if request.find('GET /pega_temp HTTP/1.1') != -1:
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: application/json\n')
      conn.send('Connection: close\n\n')
      temp = read_ds_sensor()
      conn.sendall(dumps(str(temp)))

    if request.find('GET /pega_mexer HTTP/1.1') != -1:
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: application/json\n')
      conn.send('Connection: close\n\n')
      conn.sendall(dumps(moving()))
      
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')