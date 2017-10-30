import socket
import ssl


def parsed_url(url):
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        u = url

    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {'http': 80, 'https': 443, }
    #  默认端口
    port = port_dict[protocol]
    if ':' in host:
        h = host.split(':')
        host = h[0]
        port = int(h[1])
    return protocol, host, port, path


def socket_by_protocol(protocol):
    if protocol == 'http':
        s = socket.socket()
    else:
        # 考虑https情况
        s = ssl.wrap_socket(socket.socket())
    return s


def response_by_socket(s):
    # 返回socket读取的所有数据
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response


def parsed_response(r):
    # 把response解析出状态码 headers body
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


def get(url):
    # get请求处理url
    protocol, host, port, path = parsed_url(url)

    s = socket_by_protocol(url)
    s.connect((host, port))

    request = 'GET {} HTTP/1.1\r\nhost: {}\r\nConnection: close\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))

    response = response_by_socket(s)
    r = response.decode(encoding)

    status_code, headers, body = parsed_response(r)
    if status_code in [301, 302]:
        url = headers['location']
        return get(url)
    return status_code, headers, body


def main():
    url = 'http://movie.douban.com/top250'
    status_code, headers, body = get(url)
    print(status_code, headers, body)


if __name__ == '__main__':
    # test()
    main()
