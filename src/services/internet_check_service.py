import http.client


class InternetCheckService:
    @staticmethod
    def is_online():
        connection = http.client.HTTPConnection('ipecho.net', timeout=2)
        try:
            connection.request('HEAD', '/')
            connection.close()
            return True
        except:
            connection.close()
            return False
