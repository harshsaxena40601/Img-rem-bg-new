import platform
import openvino as ov


def get_device_info():
    core = ov.Core()

    devices = []

    for device in core.available_devices:
        try:
            full_name = core.get_property(
                device,
                "FULL_DEVICE_NAME"
            )
        except RuntimeError:
            full_name = "Unknown"

        devices.append({
            "device": device,
            "name": full_name
        })

    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "devices": devices
    }


def print_device_info():
    info = get_device_info()

    print("\n" + "=" * 50)
    print("BACKGROUND REMOVER")
    print("SYSTEM DETECTION")
    print("=" * 50)

    print(f"\nSystem: {info['system']}")
    print(f"Machine: {info['machine']}")
    print(f"Processor: {info['processor']}")

    print("\nAvailable OpenVINO devices:")

    for item in info["devices"]:
        print(f"\n  Device: {item['device']}")
        print(f"  Name:   {item['name']}")


if __name__ == "__main__":
    print_device_info()