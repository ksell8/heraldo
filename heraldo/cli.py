import argparse
import signal
import threading

from heraldo import Advertiser, IBeacon


def cmd_ibeacon(args: argparse.Namespace) -> None:
    beacon = IBeacon(
        uuid=args.uuid,
        major=args.major,
        minor=args.minor,
        tx_power=args.tx_power,
    )

    stop_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
    signal.signal(signal.SIGINT, lambda *_: stop_event.set())

    kwargs = {}
    if args.adapter:
        kwargs["adapter_path"] = args.adapter

    with Advertiser(**kwargs) as advertiser:
        if args.name:
            advertiser.set_alias(args.name)
        advertiser.register(beacon, args.ad_type)
        print(f"Advertising iBeacon {args.uuid} (major={args.major}, minor={args.minor}). Press Ctrl+C to stop.")
        stop_event.wait()


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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
