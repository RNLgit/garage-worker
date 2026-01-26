# BambuLab API Module

Python interface for BambuLab 3D printer monitoring via Cloud API and MQTT.

## Installation

```bash
pip install garage-worker
# Or install dependency directly:
pip install bambu-lab-cloud-api>=1.0.5
```

## Quick Start

```python
from garage_worker.bambulab_api import BambuPrinter

with BambuPrinter(username="your@email.com", password="yourpass") as printer:
    state = printer.get_state()
    print(f"Nozzle: {state.nozzle_temp}°C, Bed: {state.bed_temp}°C")
```

---

## 1. Local Interactive Usage

For testing and playing around with the API.

### Step 1: Get Token (One-time)

First-time authentication may prompt for email verification code (2FA).

```python
from garage_worker.bambulab_api import BambuAuthenticator, BambuClient

# Authenticate (interactive - may prompt for 2FA code)
auth = BambuAuthenticator()
token = auth.get_or_create_token(username="your@email.com", password="yourpass")
print(f"Token: {token}")  # Save this for later use

# Get device info
client = BambuClient(token=token)
devices = client.get_devices()
print(f"Devices: {devices}")

user_info = client.get_user_info()
print(f"UID: {user_info['uid']}")
```

### Step 2: Connect MQTT and Watch Live Data

```python
from garage_worker.bambulab_api import (
    BambuClient, MQTTClient, PrinterStateAccumulator
)

token = "your-saved-token"
client = BambuClient(token=token)
devices = client.get_devices()
device_id = devices[0]['dev_id']
uid = client.get_user_info()['uid']

# Accumulator merges incremental MQTT updates into complete state
accumulator = PrinterStateAccumulator()

def on_message(device_id, data):
    if not data:
        return
    state = accumulator.update(data)
    print(f"Nozzle: {state.nozzle_temp}°C | Bed: {state.bed_temp}°C | "
          f"Progress: {state.print_percent}% | WiFi: {state.wifi_signal}")

    # Access AMS data
    if state.ams:
        for unit in state.ams.units:
            print(f"  AMS {unit.unit_id}: humidity={unit.humidity}, temp={unit.temp}°C")
            for tray in unit.trays:
                if tray.tray_type:
                    print(f"    Tray {tray.tray_id_name}: {tray.tray_type} "
                          f"({tray.tray_color}), {tray.remain_percent}% left")

mqtt = MQTTClient(str(uid), token, device_id, on_message=on_message)
mqtt.connect(blocking=True)  # Blocks until Ctrl+C
```

### Using the High-Level Interface

Simpler approach that handles authentication and MQTT setup automatically:

```python
from garage_worker.bambulab_api import BambuPrinter

printer = BambuPrinter(
    username="your@email.com",
    password="yourpass",
    silent=False  # Show debug output for local testing
)
printer.connect(blocking=False)

# Check state anytime
state = printer.get_state()
print(f"Printing: {state.is_printing}")
print(f"Nozzle: {state.nozzle_temp}°C")
print(f"Progress: {state.print_percent}%")

# Get full snapshot as dict
snapshot = printer.get_snapshot()
print(snapshot)

# Access AMS info
if state.ams and state.ams.units:
    print(f"AMS humidity: {state.ams.units[0].humidity}")
    print(f"AMS temp: {state.ams.units[0].temp}°C")

printer.disconnect()
```

---

## 2. Remote Automated Polling (Django/Background)

For production use in Django management commands, Celery tasks, or background services.

### Environment Variables

Set these once on your server:

```bash
export BAMBU_USERNAME="your@email.com"
export BAMBU_PASSWORD="yourpass"
# Optional:
export BAMBU_DEVICE_ID="01P00A431300120"
export BAMBU_TOKEN="pre-saved-token"  # Skip initial auth
```

### Polling Service Example

```python
import time
import logging
from garage_worker.bambulab_api import BambuPrinter

logger = logging.getLogger(__name__)

class PrinterPoller:
    """
    Background service for polling BambuLab printer data.

    Features:
    - Silent mode (no stdout prints)
    - Auto token refresh on expiration
    - Auto reconnect on errors
    """

    def __init__(self):
        # Reads credentials from environment variables
        self.printer = BambuPrinter(silent=True)

    def run(self, interval_sec=30):
        """Run polling loop with automatic error recovery."""
        self.printer.connect(blocking=False)

        try:
            while True:
                snapshot = self.printer.get_snapshot()
                self.save_to_db(snapshot)
                time.sleep(interval_sec)

        except KeyboardInterrupt:
            logger.info("Polling stopped by user")
        except Exception as e:
            logger.error(f"Error: {e}, reconnecting...")
            self.printer.reconnect()  # Auto-refreshes token if expired
            self.run(interval_sec)
        finally:
            self.printer.disconnect()

    def save_to_db(self, snapshot):
        """Save snapshot to database."""
        # Example: Django ORM
        # PrinterReading.objects.create(**snapshot)

        logger.info(
            f"Saved: nozzle={snapshot['nozzle_temp']}°C, "
            f"bed={snapshot['bed_temp']}°C, "
            f"progress={snapshot['print_percent']}%"
        )


# Run the poller
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    poller = PrinterPoller()
    poller.run(interval_sec=30)
```

### Django Management Command

```python
# myapp/management/commands/poll_printer.py
from django.core.management.base import BaseCommand
from garage_worker.bambulab_api import BambuPrinter
import time

class Command(BaseCommand):
    help = 'Poll BambuLab printer and save readings'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=30)

    def handle(self, *args, **options):
        printer = BambuPrinter(silent=True)
        printer.connect(blocking=False)

        try:
            while True:
                snapshot = printer.get_snapshot()
                # Save to your model
                # PrinterReading.objects.create(**snapshot)
                self.stdout.write(f"Saved reading: {snapshot['print_percent']}%")
                time.sleep(options['interval'])
        finally:
            printer.disconnect()
```

### One-Shot Status Check (API Endpoint)

For quick status checks in API views:

```python
from garage_worker.bambulab_api import get_printer_status

def printer_status_view(request):
    """API endpoint returning current printer status."""
    state = get_printer_status(timeout_sec=10)  # Uses env vars

    return JsonResponse({
        "nozzle_temp": state.nozzle_temp,
        "bed_temp": state.bed_temp,
        "progress": state.print_percent,
        "status": state.gcode_state,
        "is_printing": state.is_printing,
        "remaining_minutes": state.remaining_time_min,
        "current_job": state.subtask_name,
    })
```

---

## Data Reference

### PrinterState Properties

| Property | Type | Description |
|----------|------|-------------|
| `nozzle_temp` | float | Current nozzle temperature (°C) |
| `nozzle_target_temp` | float | Target nozzle temperature (°C) |
| `bed_temp` | float | Current bed temperature (°C) |
| `bed_target_temp` | float | Target bed temperature (°C) |
| `chamber_temp` | float | Chamber temperature (°C) |
| `gcode_state` | str | "IDLE", "RUNNING", "PAUSE", "FINISH" |
| `print_percent` | int | Print progress 0-100 |
| `remaining_time_min` | int | Estimated minutes remaining |
| `layer_num` | int | Current layer number |
| `total_layer_num` | int | Total layers |
| `wifi_signal` | str | WiFi signal (e.g., "-34dBm") |
| `wifi_signal_dbm` | int | WiFi signal as integer |
| `gcode_file` | str | Current gcode filename |
| `subtask_name` | str | Current print job name |
| `cooling_fan_speed` | int | Part cooling fan % |
| `heatbreak_fan_speed` | int | Heatbreak fan % |
| `is_printing` | bool | True if printing |
| `is_idle` | bool | True if idle |
| `is_paused` | bool | True if paused |
| `ams` | AMSState | AMS data (see below) |

### AMSState Properties

| Property | Type | Description |
|----------|------|-------------|
| `units` | List[AMSUnit] | List of AMS units |
| `ams_status` | int | AMS status code |
| `tray_now` | str | Currently selected tray |
| `total_trays` | int | Total tray count |
| `loaded_trays` | List[FilamentTray] | Trays with filament |

### AMSUnit Properties

| Property | Type | Description |
|----------|------|-------------|
| `unit_id` | str | Unit ID (0, 1, 2, 3) |
| `humidity` | int | Humidity level 1-5 (lower is better) |
| `humidity_raw` | int | Raw humidity percentage |
| `temp` | float | Internal temperature (°C) |
| `trays` | List[FilamentTray] | Tray list |

### FilamentTray Properties

| Property | Type | Description |
|----------|------|-------------|
| `tray_id_name` | str | Slot name (e.g., "A00-W1") |
| `tray_type` | str | Filament type (PLA, ABS, PETG) |
| `tray_sub_brands` | str | Brand (e.g., "PLA Matte") |
| `tray_color` | str | Hex color (e.g., "FFFFFFFF") |
| `remain_percent` | int | Remaining filament % |
| `tray_weight` | int | Spool weight (g) |
| `nozzle_temp_min` | int | Min nozzle temp |
| `nozzle_temp_max` | int | Max nozzle temp |

### Snapshot Dict (for Database)

`printer.get_snapshot()` returns a flattened dict ideal for database storage:

```python
{
    "timestamp": "2024-01-26T11:04:55+11:00",

    # Temperatures
    "nozzle_temp": 220.5,
    "nozzle_target_temp": 220.0,
    "bed_temp": 55.0,
    "bed_target_temp": 55.0,
    "chamber_temp": 28.0,

    # Print state
    "gcode_state": "RUNNING",
    "print_percent": 45,
    "remaining_time_min": 120,
    "layer_num": 50,
    "total_layer_num": 200,

    # Job info
    "subtask_name": "benchy.gcode",
    "gcode_file": "benchy.gcode",

    # Fans
    "cooling_fan_speed": 100,
    "heatbreak_fan_speed": 70,

    # Network
    "wifi_signal_dbm": -34,

    # Errors
    "print_error": 0,
    "has_errors": False,

    # AMS (if available)
    "ams_unit_count": 1,
    "ams_status": 0,
    "ams_humidity": 2,
    "ams_humidity_raw": 30,
    "ams_temp": 36.3,
    "filaments": [
        {
            "slot": "A00-W1",
            "type": "PLA",
            "brand": "PLA Basic",
            "color": "FFFFFFFF",
            "remain_percent": 85
        },
        # ... more trays
    ]
}
```

---

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `BambuAuthenticator` | Token authentication (from bambu-lab-cloud-api) |
| `BambuClient` | Cloud API client for devices/user info |
| `MQTTClient` | Real-time MQTT connection |
| `PrinterState` | Complete printer state dataclass |
| `PrinterStateAccumulator` | Merges incremental MQTT updates |
| `BambuPrinter` | High-level interface (recommended) |
| `AMSState` | AMS system state |
| `AMSUnit` | Single AMS unit |
| `FilamentTray` | Single filament tray |

### Functions

| Function | Description |
|----------|-------------|
| `get_printer_status(timeout_sec=10)` | Quick one-shot status check |

---

## Troubleshooting

### Token Expired
`BambuPrinter` automatically refreshes tokens when credentials are provided. Ensure `BAMBU_USERNAME` and `BAMBU_PASSWORD` environment variables are set.

### 2FA Required
First-time authentication requires email verification. Run interactively once:
```python
auth = BambuAuthenticator()
token = auth.get_or_create_token(username="...", password="...")
```

### No Devices Found
Ensure your printer is registered in the BambuLab app and connected to the cloud.

### MQTT Connection Issues
- Check WiFi signal strength
- Ensure printer firmware is up to date
- Try `printer.reconnect()` to reset the connection
