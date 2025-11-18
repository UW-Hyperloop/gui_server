# TCP Server and Client

Simple Python TCP server and mock client for microcontroller communication.

## Usage

### Start the Server

```bash
python server.py
```

The server will listen on `localhost:8888`.

### Start the Client

In a separate terminal:

```bash
python client.py
```

### Sending Data

**From Client to Server:**
In the client console, type:
```
send <your data here>
```

**From Server to Client(s):**
In the server console, type:
```
send <your data here>
```
This will send the message to all connected clients.

For example:
```
send Hello, microcontroller!
send {"sensor": 123, "temp": 25.5}
```

Type `quit` to exit (works in both server and client).

## Features

- **Server**: Accepts multiple client connections, can send data to all clients via console
- **Client**: Simple console interface with `send <data>` command
- **Bidirectional**: Both server and client can send and receive data in real-time

