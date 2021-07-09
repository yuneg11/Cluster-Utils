# Cluster Utils

## GPU status

Prepare `hosts.json` under `~/.bin/` directory or specify it with `-f` option.
The format of `hosts.json` is described [here](#format-of-hostsjson)

### Basic usage

- Show memory: `$ python3 gpu.py` or `$ python3 gpu.py mem`

  Example output:

  ```
  [server1]  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB
  [server2] 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB
  [server3]  9431 MB |  9397 MB |  9171 MB |  9149 MB |  9431 MB |  9397 MB |  9171 MB |  9149 MB
  ```

- Show utilization: `$ python3 gpu.py util`

  Example output:

  ```
  [server1]  33 % |   4 % |  29 % |  41 % |  11 % |  24 % |   4 % |  20 %
  [server2]  98 % |  98 % |  98 % |  98 % |  98 % |  98 % |  98 % |  98 %
  [server3]  37 % |  33 % |  41 % |  20 % |  32 % |  10 % |  37 % |  28 %
  ```

- Show memory and utilization: `$ python3 gpu.py all`

  Example output:

  ```
  [server1]  7709M /  33% |  7709M /   4% |  7709M /  29% |  7709M /  41% |  7709M /  11% |  7709M /  24% |  7709M /   4% |  7709M /  20%
  [server2] 10019M /  98% | 10019M /  98% | 10019M /  98% | 10019M /  98% | 10019M /  98% | 10019M /  98% | 10019M /  98% | 10019M /  98%
  [server3]  9431M /  37% |  9397M /  33% |  9171M /  41% |  9149M /  20% |  9431M /  32% |  9397M /  10% |  9171M /  37% |  9149M /  28%
  ```

### Advanced usage

- Watch mode

  `$ python3 gpu.py -i` or `$ python3 gpu.py -i <second>` (update interval)

  Example command: `$ python3 gpu.py -i 3`

- Specify target servers

  `$ python3 gpu.py -t <server-name>...`

  Example command:

  `$ python3 gpu.py -t server3 server2`

  ```
  [server3]  9431 MB |  9397 MB |  9171 MB |  9149 MB |  9431 MB |  9397 MB |  9171 MB |  9149 MB
  [server2] 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB
  ```

- Specify another `hosts.json` file

  `$ python3 gpu.py -f <hosts-file-path>`

  Example command:

  `$ python3 gpu.py -f ~/myhosts.json`

- Show detail information for debugging

  `$ python3 gpu.py --debug`

  Without debug option (show simple error message):

  ```
  [server1]  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB
  [server2] Connection error
  [server3]  9431 MB |  9397 MB |  9171 MB |  9149 MB |  9431 MB |  9397 MB |  9171 MB |  9149 MB

  Cannot connect to some server monitor(s).
  Please contact to admin.
  ```

  With debug option (show error number and reason):

  ```
  [server1]  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB
  [server2] [Errno 111] Connection refused
  [server3]  9431 MB |  9397 MB |  9171 MB |  9149 MB |  9431 MB |  9397 MB |  9171 MB |  9149 MB

  Cannot connect to some server monitor(s).
  Please contact to admin.
  ```

  With debug option in watch mode (show query time):

   ```
  [server1]  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB |  7709 MB
  [server2] 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB | 10019 MB
  [server3]  9431 MB |  9397 MB |  9171 MB |  9149 MB |  9431 MB |  9397 MB |  9171 MB |  9149 MB

  query time: 0.222 s
  ```

### Help message

`$ python3 gpu.py -h`

```
Remote GPU Monitor

usage: gpus [-h] {all, mem, util} [-i [INTERVAL]] [-t <TARGET ...>]

arguments:
  all:  Print memory and utilization of GPU
  mem:  Print memory of GPU
  util: Print utilization of GPU

optional arguments:
  -h, --help                       Print this help screen
  -t, --target-hosts <TARGET...>   Specify target host names to monitor
  -i, --interval [INTERVAL]        Use watch mode if given; seconds update interval
  -f, --hosts-file                 Path to the 'hosts.json' file
  -d, --debug                      Show information for debugging
```

## Common instructions

### Format of `hosts.json`

```jsonc
{
    // Specify the primary(tcp) connection and the secondary(ssh) connection.
    // Fallback to the secondary connection if there is a problem with the primary.
    "<Name of server 0>": {
        "tcp": ["<Address of server 0>", <tcp port of server 0>],
        "ssh": ["<User name>@<Address of server 0>", <ssh port of server 0>]
    },
    // Specify only primary(tcp) connection.
    // Cannot fallback to the secondary connection even if there is a problem with the primary.
    "<Name of server 1>": {
        "tcp": ["<Address of server 1>", <tcp port of server 1>]
    },
    // Specify only secondary(ssh) connection.
    // DO NOT use this format if the primary connection is available.
    // Warning message will be shown.
    "<Name of server 2>": {
        "ssh": ["<User name>@<Address of server 2>", <ssh port of server 2>]
    },
    ...
}
```

Example:

```json
{
    "siml01": {
        "tcp": ["10.11.0.2", 65432],
        "ssh": ["siml@10.11.0.2", 22]
    },
    "siml02": {
        "tcp": ["10.12.0.2", 65432],
        "ssh": ["siml@10.12.0.2", 22]
    },
    "siml03": {
        "tcp": ["10.12.0.2", 65432]
    }
}
```
