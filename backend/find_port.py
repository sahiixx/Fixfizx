import socket
for port in range(9001, 9100):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        print(f"PORT:{port}")
        s.close()
        break
    except:
        s.close()
