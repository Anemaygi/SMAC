<p align="center">
  <img src="../../src/SMAC.png" width="300" /><br/>
  Sistema de Monitoramento para Assentos de Cadeira de Roda<br/>
  <i>:desktop_computer: Relatório técnico
    <br/>:computer_mouse: Códigos</i>
</p>
<br/>

São três os arquivos utilizados pelo sistema<br/>
```code
├── boot.py
├── main.py
├── index.html
``` 
Abaixo, há uma breve descrição e explicação de cada trecho de código para cada arquivo.

<br/>


# :arrows_clockwise: boot.py

## Descrição

Script executado quando a placa com MicroPython boota. Serve para definir configurações da aplicação, como, por exemplo, quais pinos serão usados para os sensores, importação de bibliotecas e conexão da placa ao wi-fi.

## Passo a passo

Primeiramente, o arquivo importa as bibliotecas que serão usadas no projeto. Elas são:
- usocket/socket: Interface de sockets em python
- time (função sleep): Função para dar um delay no código em segundos
- machine: Módulo com funções específicas da placa utilizada
- ds18x20: Driver para sensor de temperatura DS18B20
- onewire: Biblioteca para utilizar um barramento único com o sensor de temperatura DS18B20 
- network: Módulo para utilização de redes.
- esp: Módulo com funções relacionadas ao ESP8266 e ESP32. Utilizamos sua função esp.osdebug(None) para desativar mensagens de debug de seu sistema operacional.
- gc: Garbage colector. Coleta as variáveis não acessíveis.

```py
try:
  import usocket as socket
except:
  import socket
  
from time import sleep
import machine, onewire, ds18x20, network

import esp
esp.osdebug(None)

import gc
gc.collect()
```

Em segundo lugar, definimos os pinos que serão utilizados por cada um dos sensores.

Para os sensores de temperatura, utilizaremos o pino 4. Todos serão conectados ao mesmo pino e, para isso acontecer, é necessário utilizar as bibliotecas ds18x20 para utilizar o sensor e onewire para utilizar um barramento único para todos, que podem ser identificados pelo seu ID único.

```py
ds_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
```

Em relação aos sensores de toque, basta adicioná-los nos pins que serão usados e configurá-los para entrada. Pode ser feito de maneira digital, já que o pin só retorna os valores 0 e 1, indicando se há toque ou não.

```py
touchA = machine.Pin(21, machine.Pin.IN)
touchB = machine.Pin(19, machine.Pin.IN)
touchC = machine.Pin(23, machine.Pin.IN)
touchD = machine.Pin(22, machine.Pin.IN)
```

Logo, colocamos as credenciais da rede (troque `NomeDaRede` e `SenhaDaRede` para seus valores respectivos), conectando-a na rede indicada.

```py
ssid = 'NomeDaRede'
password = 'SenhaDaRede'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
```
<br/>

# :arrow_up: main.py

## Descrição

Script principal com o programa python que será rodado. Ele é executado após `boot.py`. Serve como servidor para receber requisições em suas funções pela página web.

## Passo a passo

Importa pacotes para tratamento de json a fim de fazer a comunicação entre servidor e a página do cliente

```py
try:
  from json import loads, dumps
except:
  from ujson import loads, dumps
```

Esta função abaixo é utilizada para ler os valores dos sensores de temperatura.
Primeiramente, escaneia todos os sensores que estão conectados, são 4. Depois, pega a temperatura de cada um deles. Quando a temperatura é válida, devolve o seu valor. Caso contrário, devolve "b'0.0'"

```py
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
```

A função abaixo é para definir se o usuário está sentado na mesma posição. Há quatro sensores (touchA, touchB, touchC, touchD) no assento: cada um deles pode assumir o valor 0 ou 1. Esta função cria um array com os valores de cada um dos sensores, espera 3 segundos e cria um novo, comparando os valores da nova posição e da antiga. Caso sejam diferentes, retorna True (pois houve movimento), caso contrário, False.

Para entender seu funcionamento: Há 4 sensores A,B,C e D no assento. Uma pessoa pode sentar pressionando os 4 sensores, mas, na hora que ela se mexer, pode ser que um dos sensores deixa de ser apertado, então é possível notar que houve uma mudança de posição. Há um tempo de 3 segundos para garantir que seja uma mudança de posição considerável.

```py
def moving():
  old = "touchA = "+str(touchA.value())+" touchB: "+str(touchB.value())+" touchC: "+str(touchC.value())+" touchD: "+str(touchD.value())
  sleep(3)
  new = "touchA = "+str(touchA.value())+" touchB: "+str(touchB.value())+" touchC: "+str(touchC.value())+" touchD: "+str(touchD.value())
  if old != new:
    return True
  return False
```

Cria uma conexão na porta 80 e espera 5 conexões antes de negar

```py
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
```

O código abaixo roda sempre que o servidor está online.
Primeiramente, ele vê se algum dispositivo se conecta ao socket. A maior parte está dentro do "try"

```py
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
```

Procura uma conexão GET /, retornando o status de OK e a página principal da aplicação.

```py
if request.find("GET / HTTP/1.1") != -1:
      with open("index.html", 'r') as html:
        response = html.read()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        html.close()
```

Procura ver se o cliente mandou uma requisição "GET /pega_temp", retornando o valor encontrado pela função `read_ds_sensor()` para o lado do cliente com a temperatura do momento.

```py
    if request.find('GET /pega_temp HTTP/1.1') != -1:
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: application/json\n')
      conn.send('Connection: close\n\n')
      temp = read_ds_sensor()
      conn.sendall(dumps(str(temp)))
```

Procura ver se o cliente mandou uma requisição "GET /pega_mexer", retornando True ou False da função `moving()` 

```py
    if request.find('GET /pega_mexer HTTP/1.1') != -1:
      conn.send('HTTP/1.1 200 OK\n')
      conn.send('Content-Type: application/json\n')
      conn.send('Connection: close\n\n')
      conn.sendall(dumps(moving()))
```

Fecha a conexão

```py
conn.close()
```

Caso tenha algum erro no "try", também fecha a conexão.

```py
  except OSError as e:
    conn.close()
    print('Connection closed')
```

<br/>

# :arrow_right_hook: index.html

## Descrição

Página web que é respondida para o cliente quando ele manda uma requisição "GET /". A página é feita por HTML, CSS e, por fim, JavaScript para fazer a chamada de requisições. Como a finalidade da matéria não é desenvolvimento web, não apresentarei o HTML ou CSS, apenas as funções dos scripts em javascript.

## Passo a passo

A primeira função do script é inicializada quando a página carrega e, a cada 3 segundos de intervalo, faz uma requisição "GET /pega_temp" para o servidor. Pegando a resposta, analisa se é maior que 37°C, caso for, manda um alerta para indicar ao usuário se mexer. Sendo ou não sendo, atualiza o conteúdo da div com ID "temperaturac" para o valor respondido pelo servidor.

```js
    window.addEventListener('load', () => {
        setInterval(function(){  
            fetch("/pega_temp").then(data => {
                data.json().then(response => {
                    if(response > 37) alert("SE MEXA!");
                    document.getElementById('temperaturac').innerText = response
                    
                })
            })
        }, 3000)
    })
```

Outra função que começa quando a página carrega e utiliza 3 segundos de intervalo entre requisições serve para ver se o usuário mudou de posição, mandando uma requisição "GET /pega_mexer" para o servidor. Caso o usuário tenha mudado de posição, a página é recarregada para o cronômetro reiniciar.

```js
    window.addEventListener('load', () => {

        setInterval(function(){  
            fetch("/pega_mexer").then(data => {
                data.json().then(response => {
                    if(response == true) window.location.reload(true)
                })
            })
        }, 3000)

    })
```

O cronômetro é uma função javascript que roda do lado do cliente. Para isso, fazemos as contas de quanto tempo falta e substituímos o texto da div "timer" para este tempo.

```js
    function startTimer(duration, display) {
      var timer = duration, minutes, seconds;
      setInterval(function () {
          minutes = parseInt(timer / 60, 10);
          seconds = parseInt(timer % 60, 10);
          minutes = minutes < 10 ? "0" + minutes : minutes;
          seconds = seconds < 10 ? "0" + seconds : seconds;
          display.textContent = minutes + ":" + seconds;
          if (--timer < 0) {
            alert("SE MEXA!");  
            timer = duration;
          }
      }, 1000);
  }
  
    window.onload = function () {
        var duration = 60 * 20; // Converter para segundos
        display = document.querySelector('#timer'); // selecionando o timer
        startTimer(duration, display); // iniciando o timer
    };
```
