# Reverse engineering the [edelkrone SliderOne v2](https://edelkrone.com/products/sliderone-v2)

### Table of contents
* [Why do this?](why-do-this)
* [Scope](scope)
* [Current Findings](current-findings)
* [Next Steps?](next-steps)

## Why do this?
The edelkrone "SliderOne v2" is a consumer-grade camera slider that uses BlueTooth. For many applications the 
app from the developer is sufficient. However for macro photography and [focus stacking](https://en.wikipedia.org/wiki/Focus_stacking)
the app falls short. The hope is to reverse engineer the bluetooth protocol used by the app & slider in order to 
enable simple 3rd party applications.
![edelkrone](./images/edelkrone_app.png | width=400)
## Scope
The only functionality currently planned to replicate is
1. pairing with the device
2. moving the slider right and left

None of the motion planning features or parameter tweaking is currently in-scope. I'd like to start small :)
## Current findings
Logs have been collected from adb using logcat: `adb -d logcat BleService:D BLUETOOTH:D Joystick:D BleScanner:D '*:S'`
and the hci logging tools in android `adb bugreport {filename}`. Relevant logs have been put in the
[logs directory](./logs). Three different executions have been recorded, they all follow the same general pattern

1. Pair with the slider
2. Pan to the left

The hci logs are perhaps the most useful and a comparison of the three different runs is located in the 
[/logs/analysis](./logs/analysis) folder.

what follows is my analysis of the file:
***
Event 46 is where the logs first start to diverge and have different values:
```
Event 46
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:04:09:0c:b0:00:c9
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:04:09:13:63:00:83
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:04:09:16:91:00:b4
```
This appears to correspond to a:
```
01-17 13:57:06.998  5303  5303 D BLUETOOTH: Process Command: IO_CTRL
```
message from the adb debugger console. I believe this to be some kind of initialization message going from the
app to the slider.
***
The next discrepancy occurs at event 48 it comes from the slider
```
Event 48
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:00:0c:b0:ff:ff:ff:ff:02:01:ff:00:1a:00:00:00:00:00:00:05:d4
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:00:13:63:ff:ff:ff:ff:02:01:ff:00:1a:00:00:00:00:00:00:05:8e
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:00:16:91:ff:ff:ff:ff:02:01:ff:00:1a:00:00:00:00:00:00:05:bf
```
this appears to be a response to `Event 46`
***
At event 49 all the commands from the app sync up again
```
Event 49
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0e:00:10
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0e:00:10
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0e:00:10
```
***
Event 51 and 52 seem to be call-response with canned responses
```
Event 51
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:01:00:00:3d:00:23:00:43:52:53:50:09:20:32:34:52:00:00:02:7a
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:01:00:00:3d:00:23:00:43:52:53:50:09:20:32:34:52:00:00:02:7a
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:01:00:00:3d:00:23:00:43:52:53:50:09:20:32:34:52:00:00:02:7a

Event 52
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:03:c9:04:00:d0
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:03:c9:04:00:d0
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:03:c9:04:00:d0
```
***
54 the message from the slider is dynamic, but the response from the app is static
```
Event 54
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d7:ff:ff:00:00:04:00:00:00:04:0c
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d5:ff:ff:00:00:04:00:00:00:04:0a
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d4:ff:ff:00:00:04:00:00:00:04:09

Event 55
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:03:18:00:00:1b
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:03:18:00:00:1b
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:03:18:00:00:1b
```
***
Completely canned calls from 57 and 58
```
Event 57
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:06:00:00:00:00:fa:00:00:00:00:00:00:00:00:00:00:00:00:01:00
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:06:00:00:00:00:fa:00:00:00:00:00:00:00:00:00:00:00:00:01:00
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:06:00:00:00:00:fa:00:00:00:00:00:00:00:00:00:00:00:00:01:00

Event 58
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:20:00:00:00:fa:01:20
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:20:00:00:00:fa:01:20
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:20:00:00:00:fa:01:20
```
***
Completely canned from 60 and 61
```
Event 60
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:06:00:00:00:00:fa:00:00:00:00:00:00:00:00:00:00:00:00:01:00
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:06:00:00:00:00:fa:00:00:00:00:00:00:00:00:00:00:00:00:01:00
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:06:00:00:00:00:fa:00:00:00:00:00:00:00:00:00:00:00:00:01:00

Event 61
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:1c:00:1e
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:1c:00:1e
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:1c:00:1e
```
***
Canned again with 63 and 64
```
Event 63
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:07:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:07
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:07:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:07
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:07:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:07

Event 64
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
```
***
What I think is the beginning of the slider waiting for commands
```
Event 66
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d7:ff:ff:00:00:04:00:00:00:04:0c
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d5:ff:ff:00:00:04:00:00:00:04:0a
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d4:ff:ff:00:00:04:00:00:00:04:09

Event 67
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
```
***
What I believe to be the beginning of the slider moving in log2
```
Event 129
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d7:ff:ff:00:00:04:00:00:00:04:0c
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d5:ff:ff:00:00:04:00:00:00:04:0a
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d4:ff:ff:00:00:04:00:00:00:04:09

Event 130
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:00:00:70:7f:01:02
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
```
***
Sliders moving in all different log streams
```
Event 169
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:1e:9f:70:7f:01:bf
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:00:00:70:7f:01:02
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:af:f5:70:7f:02:a6
```







```
Event 66
log 1: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d7:ff:ff:00:00:04:00:00:00:04:0c
log 2: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d5:ff:ff:00:00:04:00:00:00:04:0a
log 3: source:SldrOne	dest:Pixel 5	opcode:0x0000001b	value:02:00:64:00:00:00:00:08:c5:d4:ff:ff:00:00:04:00:00:00:04:09
```
***
this maaaybe looks like the beginning of one of the `01-17 13:14:59.392 18637 18637 D BLUETOOTH: Process Command: MANUAL_SLIDE`
```
Event 124
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:00:00:70:7f:01:02
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:02:0f:00:11
```
***
Because later _all_ the values diverge like so:
```
log 1: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:0b:6d:70:7f:01:7a
log 2: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:db:e5:70:7f:02:c2
log 3: source:Pixel 5	dest:SldrOne	opcode:0x00000012	value:06:0d:9b:74:70:7f:02:11
```

## Next Steps?
