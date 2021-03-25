import socket

# Send kill signal to the crawler

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("localhost", 2803))
    s.sendall(b'kill')

print("Kill signal sent")
