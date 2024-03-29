<img src="Lycanthropy_Logo.png" width=300>

# L Y C A N T H R O P Y
[![forthebadge](https://forthebadge.com/images/badges/made-with-java.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/gluten-free.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

Lycanthropy is a modular post-exploitation tool instrumented with DNS and written in Java, with a distributable client to enable collaborative Red Teaming and Penetration Testing.

## Features
* DNS communication with AES-GCM-256 encryption via AAAA lookup
* Ephemeral final config and per-build password distribution
* C2 access management
* Per engagement data partitioning system
* Distributable client for collaborative testing
* New GUI (NOTE: The new gui is better on windows than in a linux graphical interface)

![image](https://user-images.githubusercontent.com/47731694/154202430-77312004-df75-4f44-80d2-cdee1ff2ffc0.png)

## Architecture
When a lycanthropy agent is executed on a target, it uses recursive lookups to route back to the DNS C2. The DNS daemon ingests and parses the requests before forwarding them onto the API backend or storing them as necessary. The API backend stores data, provides authentication and authorization, brokers configuration and package distribution, and distributes command tasks to the agents via the DNS daemon. Operators and managers send instructions to the server and receive direct output via the gui.

![image](https://user-images.githubusercontent.com/47731694/154203949-8c4818dd-c45b-4715-b8a3-751e6872e046.png)

## Installation
For quick installation, run the following. It is recommended that you turn off command line history before running the installer.sh script.

```
git clone https://github.com/kryptops/lycanthropy
cd lycanthropy
./installer.sh -u <UI admin username> -p <UI admin password> -d <<subdomain>.<domain>.<tld>> 
cd svc
python3 lysys.py
```
On an install that can access the api server (or from a terminal on the api server), run...

```
cd svc
python3 ui.py
```

## Acknowledgements
Special thanks to <a href="https://twitter.com/romz0mbie">@romz0mbie</a>, who prototyped the logo for lycanthropy
