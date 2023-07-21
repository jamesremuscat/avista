from avista.core import expose, Device
from pythonosc.udp_client import SimpleUDPClient


# NB Not a NetworkDevice as the network is abstracted by python-osc
class QuickQ(Device):

    def __init__(self, config):
        super().__init__(config)
        host = config.extra.get('host')

        self.client = SimpleUDPClient(host, 8000)

    @expose
    def activate(self, zone, button):
        self.client.send_message(f'/10scene/{button}/{zone}', [])
