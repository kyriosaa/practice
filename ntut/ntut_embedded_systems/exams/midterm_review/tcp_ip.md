> NTUT Embedded Systems <br> Midterm Review <br> TCP/IP Networking

##
**1. What is an IP?**

> 32-bit, unique internet address of a host

##
**2. What is a Port?**

> 16-bit, unique identifier for specifying a process or service

##
**3. What is a MAC Address?**

> 48-bit, unique hardware identifier formatted as `XX:XX:XX:XX:XX:XX` and used for local data link layer communication. This number is burned into the hardware and cannot be changed.

##
**4. What are the 4 layers of the TCP/IP networking protocol?**

> 1. Link layer (device drivers)
> 2. Network layer (IP)
> 3. Transport layer (Port)
> 4. Application layer

##
**5. What is a Netmask?**

> A 32-bit number that "masks" an IP address to separate the Network ID from the Host ID.<br>
> 255s correspond to the network while 0s correspond to the host.
>
> Example:<br>
> IP Address: 192.168.1.101<br>
> Netmask: 255.255.255.0
>
> This netmask tells the computer that the first three numbers identify the network and the last number identifies the specific device on that network.<br>
> Any device with an IP address starting with `192.168.1` and the same netmask is considered to be on the same local network.

##
**6. What is Subnetting?**

> Subnetting is the process of taking one large network and dividing it into multiple smaller, logical sub-networks (or "subnets").<br>
> We do this because it reduces network traffic, makes us able to apply security rules between subnets, and makes the network easier to manage by grouping related devices.

##
**7. How is Netmasking and Subnetting used together?**

> We can divide the host netmask to multiple subnets.
>
> Example:<br>
> Subnet 1: Network ID `192.168.1.0` (Hosts from `.1` to `.126`)<br>
> Subnet 2: Network ID `192.168.1.128` (Hosts from `.129` to `.254`)

##
**8. Give an example of a well-known port.**

```bash
/etc/services
```

##
**9. Explain the different address types.**

> Unicast
> - Address refers to a single host, only the host with that IP will receive the data.
> - Ex: `ssh 140.113.209.65`

> Broadcast
> - Addresses that include all hosts on the local network.
> - All hosts on the same network will receive the data.
> - Ex: `arp packet`

> Multicast
> - Addresses that indentify a group of hosts
> - Only hosts on the same group will receive the data
> - Ex: `Video conference`

##
**10. What is NAT?**

> NAT stands for `Network Address Translation`<br>
> It allows for hosts using private addresses to talk to the outside internet.

<img src=./images/nat.png>

##
**11. What is ARP?**

> ARP stands for `Address Resolution Protocol`<br>
> A network protocol used ot map a device's IP address to its MAC address. Operates at the data link layer.
>
> When a device wants to send data to another device on the same network, it knows the target IP address but not the MAC address. It broadcasts an ARP request packet to all devices on the local network asking "Hey! Who has the IP address `X.X.X.X`? Please tell me your MAC address!"<br>
> The device with that IP address then replies with its MAX address in an ARP reply packet.<br>
> The requesting device then stores this mapping in its ARP cache for future use to avoid repeated requests.

##
**12. What is DNS?**

> DNS stands for `Domain Name System`<br>
> Translates human-readable domain names (e.g., `www.example.com`) into IP addresses (e.g., `192.0.2.1`) that computers use to identify each other on the internet.
>
> When you type a domain name into a browser, your device sends a DNS query to a DNS resolver usually provided by your ISP.<br>
> The resolver queries DNS servers in a hierarchical manner.<br>
> Results are cached on the browser, OS, and resolver to speed up future queries.

##
**13. How is the `socket` module used to create a web server on a Raspberry Pi Pico?**

> Web servers can use sockets as endpoints to allow for network communication between devices, where the server binds to an IP and port, listens for incoming connections, and accepts them to handle client requests.<br>
> Clients connect via their own sockets, sending HTTP requests (like GET/POST) over TCP, which makes sure we get ordered and error-free data transmission.<br>
> The server then processes these requests, generates responses, and sends them back, closing the connection afterward to complete the cycle.