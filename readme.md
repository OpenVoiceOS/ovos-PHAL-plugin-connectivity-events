# ovos-PHAL-plugin-connectivity-events

This is a PHAL plugin for OVOS. It watches network and internet connectivity and publishes the result on the messagebus, so skills, the GUI, and the enclosure can react to going online or offline without probing the network themselves.

## How it works

The plugin polls connectivity on an interval and tracks a connectivity state (`UNKNOWN`, `NONE`, `PORTAL`, `LIMITED`, `FULL`), modeled on [NetworkManager's connectivity states](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html). A check first tests DNS, then HTTP:

- No DNS reachable -> `NONE`
- DNS reachable but no HTTP -> `LIMITED`
- Both reachable -> `FULL`

When the state changes, the plugin emits messagebus events:

- `mycroft.network.connected` / `mycroft.network.disconnected`
- `mycroft.internet.connected` / `mycroft.internet.disconnected`
- `enclosure.notify.no_internet`

It also emits level snapshots on every check, `mycroft.network.state` and `mycroft.internet.state`, each with a `{"state": "connected"|"disconnected"}` payload.

Send `ovos.PHAL.internet_check` on the bus to trigger a check on demand. The plugin responds with `{"internet_connected": bool, "network_connected": bool}`.

## Install

```bash
pip install ovos-PHAL-plugin-connectivity-events
```

## Configuration

The plugin reads its settings from the PHAL configuration section:

```json
{
  "check_interval": 60,
  "disable_scheduled_checks": false
}
```

- `check_interval`: seconds between automatic checks. Default: 60.
- `disable_scheduled_checks`: if true, the plugin does not poll on a timer. It still responds to `ovos.PHAL.internet_check`.

## Related projects

- [OpenVoiceOS/ovos-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL): the PHAL service that loads this plugin.
- [OpenVoiceOS/ovos-plugin-manager](https://github.com/OpenVoiceOS/ovos-plugin-manager): provides plugin discovery and the `PHALPlugin` base class.
- [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client): the messagebus client used to emit and receive events.

## License

Apache-2.0
