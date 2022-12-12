import time
from enum import IntEnum
from threading import Event

from mycroft_bus_client import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils.log import LOG
from ovos_utils.network_utils import is_connected_dns, is_connected_http


class ConnectivityState(IntEnum):
    """ State of network/internet connectivity.

    See also:
    https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html
    """

    UNKNOWN = 0
    """Network connectivity is unknown."""

    NONE = 1
    """The host is not connected to any network."""

    PORTAL = 2
    """The Internet connection is hijacked by a captive portal gateway."""

    LIMITED = 3
    """The host is connected to a network, does not appear to be able to reach
    the full Internet, but a captive portal has not been detected."""

    FULL = 4
    """The host is connected to a network, and appears to be able to reach the
    full Internet."""


class ConnectivityEvents(PHALPlugin):

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-connectivity-events", config=config)
        self.sleep_time = 60
        self.stopping = Event()
        self.state = ConnectivityState.UNKNOWN
        self.bus.on("ovos.PHAL.internet_check", self.handle_check)
        if not self.config.get('disable_scheduled_checks'):
            self.bus.emit(Message("ovos.PHAL.internet_check"))

    def run(self):
        if self.config.get('disable_scheduled_checks'):
            self.stopping.wait()
        while not self.stopping.wait(self.sleep_time):
            self.handle_check(None)

    def shutdown(self):
        PHALPlugin.shutdown(self)
        self.stopping.set()

    def update_state(self, new_state: ConnectivityState, message: Message):
        """
        Handle a state change and emit the appropriate bus message(s).
        emits `mycroft.network.connected` if network is newly connected
        emits `mycroft.internet.connected` if internet is newly connected
        emits `mycroft.network.disconnected` if network is newly disconnected
        emits `mycroft.internet.disconnected` if internet is newly disconnected
        emits `enclosure.notify.no_internet` if new state has
            some networking but no internet
        :param new_state: Current connection state
        :param message: Message associated with request to check internet state
        """
        message = message or Message("connectivity_check")
        LOG.info(f"Network state changed to: {new_state.value}")
        if new_state == ConnectivityState.FULL:  # Gained internet
            if self.state <= ConnectivityState.NONE:  # Gained network
                self.bus.emit(message.reply("mycroft.network.connected"))
            self.bus.emit(message.reply("mycroft.internet.connected"))
        elif new_state > ConnectivityState.NONE:  # Gained non-internet network
            if self.state <= ConnectivityState.NONE:  # Gained network
                self.bus.emit(message.reply("mycroft.network.connected"))
            if self.state >= ConnectivityState.FULL:  # Lost internet
                self.bus.emit(message.reply("mycroft.internet.disconnected"))
                self.bus.emit(message.reply("enclosure.notify.no_internet"))
        else:  # Lost some amount of networking
            if self.state >= ConnectivityState.FULL:  # Lost internet
                self.bus.emit(message.reply("mycroft.internet.disconnected"))
            if self.state >= ConnectivityState.NONE:  # Lost network
                self.bus.emit(message.reply("mycroft.network.disconnected"))
            self.bus.emit(message.reply("enclosure.notify.no_internet"))

        self.state = new_state
        if self.state == ConnectivityState.FULL:
            self.bus.emit(message.reply("mycroft.internet.state",
                                        {"state": "connected"}))
        else:
            self.bus.emit(message.reply("mycroft.internet.state",
                                        {"state": "disconnected"}))
        if self.state > ConnectivityState.NONE:
            self.bus.emit(message.reply("mycroft.network.state",
                                        {"state": "connected"}))
        else:
            self.bus.emit(message.reply("mycroft.network.state",
                                        {"state": "disconnected"}))

    def handle_check(self, message=None):
        """
        Handle a request to check internet state from messagebus API or thread
        """
        if not is_connected_dns():
            state = ConnectivityState.NONE
        elif not is_connected_http():
            state = ConnectivityState.LIMITED
        else:
            state = ConnectivityState.FULL

        if state != self.state:
            self.update_state(state, message)

        if message:
            self.bus.emit(message)
