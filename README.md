# socks-fragmenter
A program which listens on localhost:1357 with a socks5 proxy, fragments hello world into 1-Byte packets and sends out the request
<br>
Now lets first install the required packages
first clone this repository :
```shell
git clone https://github.com/bigwhoman/socks-fragmenter.git
cd ./socks-fragmenter
```
Afterwards, install the required packages
```shell
python3 -m pip install -r requiements.txt
```
Now run the code : 
```bash
python3 fragmenter.py
```
Now if we trace the packets with wireshark, we could see that the client hello would be fragmented into 1-Byte packets and then sent.
<br>
This is because most sni detectors would simply track down the client hello based on its size and if the size is changed, then the connection is almost unrecgonizable.