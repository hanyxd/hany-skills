---
name: linux-bluetooth-audio
description: Use when Bluetooth audio isn't reaching headphones on Linux.
---

# Linux Bluetooth audio troubleshooting (PipeWire/WirePlumber)

For Arch and PipeWire-based desktops (incl. Omarchy). The goal is always to find WHY sound has nowhere to go — usually a device-class or profile problem, not a routing problem.

## Procedure (in this order)

1. **Confirm what audio devices actually exist, and whether a BT sink exists:**
   ```
   wpctl status    # look under Audio → Devices and Sinks
   pactl list short sinks
   ```
   A phone named as a BT device that appears under Devices but has NO line under Sinks = no audio output path.

2. **Read the card's profile — this alone usually nails it:**
   ```
   pactl list cards | grep -A40 bluez_card | grep -E "form_factor|bluez5.profile|Active Profile"
   ```
   - `form_factor = phone` with only `audio-gateway` (A2DP Source) available = audio SOURCE, never an output. A phone is not headphones; it will never appear as a sink.
   - `bluez5.profile = "off"` = BlueZ created the device but it never connected as an audio profile → no node, no sink.

3. **Check paired vs. connected devices:**
   ```
   bluetoothctl devices        # every known device
   bluetoothctl info <MAC>     # per-device Paired/Connected/Class/Icon
   ```
   Root cause is almost always: **no headphone-class device is paired at all**, so there is literally nowhere to route audio other than built-in speakers.

4. **Scan for real headphones (fresh advertise):**
   ```
   bluetoothctl --timeout 25 scan on
   ````
   Filter out ambient junk (shoplights, ELK-BLEDOM, etc.) — a real pair announces a product name or headphone icon.

## Pitfalls
- Do NOT assume routing if no sink exists — first check the DEVICE CLASS. A phone masquerading in the device list is the classic misread; check for a sink before touching PipeWire routing.
- `bluetoothctl info` saying `Connected: yes` does NOT mean audio is connected. The link can be up for other profiles while BlueZ keeps `bluez5.profile = off`. Cross-check with `wpctl status` / `pactl list cards`.
- Headphones still linked to another device (phone) will NOT re-advertise on scan. Force a fresh pairing mode: power OFF, then hold the pairing button ~5-7s until the LED blinks fast / announces "pairing". Only then scan again.
- If the scan repeatedly shows only ambient BT garbage, the pair is off, out of range, or battery-dead — or it is NOT Bluetooth at all (2.4 GHz dongle / wired) and BT will never see it.
- When BT audio works at all, `module-bluez5-device` cards with device.bus = bluetooth and spa bluez5 spaudio in /usr/lib/spa-0.2/bluez5/ confirm support is loaded — absence of a sink is a device/profile/paired problem, not missing modules.

## Standard pairing flow (once the pair is advertising)
```
bluetoothctl
  power on
  agent on
  default-agent
  scan on       # note MAC when it appears
  scan off
  pair <MAC>
  trust <MAC>
  connect <MAC>
  exit
wpctl status                   # pair should now be a Sink
wpctl set-default <SinkID>
```
Re-scan after forcing pairing mode before concluding a device is missing.
