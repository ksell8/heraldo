import argparse
import signal
import threading

from heraldo import Advertiser, IBeacon, Eddystone

def _advertise(beacon, name, adapter, ad_type, label) -> None:
    stop_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: stop_event.set())

    kwargs = {}
    if adapter:
        kwargs["adapter_path"] = adapter

    with Advertiser(**kwargs) as advertiser:
        if name:
            advertiser.set_alias(name)
        advertiser.register(beacon, ad_type)
        print(f"Advertising {label}. Press Ctrl+C to stop.")
        stop_event.wait()


def cmd_ibeacon(args: argparse.Namespace) -> None:
    beacon = IBeacon(
        uuid=args.uuid,
        major=args.major,
        minor=args.minor,
        tx_power=args.tx_power,
    )
    _advertise(beacon, args.name, args.adapter, args.ad_type,
               f"iBeacon {args.uuid} (major={args.major}, minor={args.minor})")


def cmd_eddystone(args: argparse.Namespace) -> None:
    beacon = Eddystone(
        namespace=args.namespace,
        instance=args.instance,
        tx_power=args.tx_power,
    )
    _advertise(beacon, args.name, args.adapter, args.ad_type,
               f"Eddystone-UID namespace={args.namespace} instance={args.instance}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="heraldo",
        description="BLE beacon advertiser for Raspberry Pi",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    ib = sub.add_parser("ibeacon", help="Advertise an Apple iBeacon")
    ib.add_argument("--uuid", required=True, help="Beacon UUID (e.g. 550e8400-e29b-41d4-a716-446655440000)")
    ib.add_argument("--major", type=int, required=True, help="Major value (0–65535)")
    ib.add_argument("--minor", type=int, required=True, help="Minor value (0–65535)")
    ib.add_argument("--tx-power", type=int, default=-59, dest="tx_power", help="TX power in dBm (default: -59)")
    ib.add_argument("--name", help="Bluetooth adapter alias shown to scanners")
    ib.add_argument("--adapter", help="DBus adapter path (e.g. /org/bluez/hci1); uses default if omitted")
    ib.add_argument(
        "--ad-type",
        choices=["peripheral", "broadcast"],
        default="peripheral",
        dest="ad_type",
        help="Advertisement type (default: peripheral)",
    )
    ib.set_defaults(func=cmd_ibeacon)

    eu = sub.add_parser("eddystone-uid", help="Advertise an Eddystone-UID beacon")
    eu.add_argument("--namespace", required=True, help="10-byte namespace as hex (20 chars)")
    eu.add_argument("--instance", required=True, help="6-byte instance as hex (12 chars)")
    eu.add_argument("--tx-power", type=int, default=-59, dest="tx_power")
    eu.add_argument("--name", help="Bluetooth adapter alias")
    eu.add_argument("--adapter", help="DBus adapter path")
    eu.add_argument("--ad-type", choices=["peripheral", "broadcast"], default="broadcast", dest="ad_type")
    eu.set_defaults(func=cmd_eddystone)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
