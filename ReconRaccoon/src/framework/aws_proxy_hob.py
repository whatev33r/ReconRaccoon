from typing import Union
import requests
from requests_ip_rotator import ApiGateway


class AWSProxyHob:
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None

    @classmethod
    def set_credentials(cls, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY):
        cls.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
        cls.AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY

    def __init__(self):
        self.gateway = None
        self.target = None

    def init_gateway(self, target):
        self.target = target
        if not self.gateway:
            try:
                self.gateway = ApiGateway(
                    site=self.target,
                    access_key_id=self.AWS_ACCESS_KEY_ID,
                    access_key_secret=self.AWS_SECRET_ACCESS_KEY,
                    verbose=False
                )
                self.gateway.start()
            except Exception as e:
                print(f"Error: {e}")

    def get_proxy_session(self, target) -> Union[requests.Session, None]:
        self.init_gateway(target)
        if self.gateway:
            session = requests.Session()
            session.mount(target, self.gateway)
            return session
        else:
            return None

    def shutdown_api_gateway(self):
        if self.gateway:
            self.gateway.shutdown()
            self.gateway = None
