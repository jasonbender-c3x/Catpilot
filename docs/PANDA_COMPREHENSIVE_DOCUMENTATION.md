# Panda Comprehensive Documentation
# Focus: CAN Bus, Steering, Torque Control & Safety Systems
# Context: 2021 Chevrolet Bolt EV with Gas Interceptor Pedal

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Panda Hardware & Architecture](#panda-hardware--architecture)
3. [Safety System Architecture](#safety-system-architecture)
4. [CAN Bus Communication](#can-bus-communication)
5. [Steering Torque Control System](#steering-torque-control-system)
6. [2021 Chevrolet Bolt EV Configuration](#2021-chevrolet-bolt-ev-configuration)
7. [Gas Interceptor Pedal Integration](#gas-interceptor-pedal-integration)
8. [How to Modify Torque Limits](#how-to-modify-torque-limits)
9. [How to Pass CAN Traffic for Interior Accessories](#how-to-pass-can-traffic-for-interior-accessories)
10. [Safety Output Controls](#safety-output-controls)

---

## Executive Summary

The **panda** is a hardware CAN bus interface running on STM32 microcontrollers (F4 or H7 series) that provides safety-critical communication between catpilot and a vehicle's CAN bus network. For the 2021 Chevrolet Bolt EV with a gas interceptor pedal, panda handles:

- **Steering torque requests** via CAN messages to the vehicle's Electric Power Steering (EPS)
- **Longitudinal control** through gas/brake messages or pedal interceptor commands
- **Safety enforcement** through firmware-level validation of all CAN messages
- **CAN bus monitoring** across multiple buses (typically 4 buses: powertrain, chassis, camera, radar)

**Key Insight**: The panda operates at the **firmware level** to enforce safety constraints before any messages reach the vehicle's CAN buses. This is catpilot's primary safety mechanism.

---

## Panda Hardware & Architecture

### Hardware Specifications

**Location**: `/home/runner/work/Catpilot/Catpilot/panda/`

#### MCU Types
- **STM32F4** (F4 devices): WHITE_PANDA, GREY_PANDA, BLACK_PANDA, UNO, DOS
- **STM32H7** (H7 devices): RED_PANDA, RED_PANDA_V2, TRES, CUATRO

#### Communication Interfaces
- **USB** (primary): Vendor ID `0xbbaa`, Product IDs `0xddee` (app), `0xddcc` (bootstub)
- **SPI** (secondary): For direct MCU communication
- **CAN buses**: Up to 4 simultaneous CAN/CAN-FD buses
  - Default speed: 500 kbps (configurable per bus)
  - Supports CAN 2.0 and CAN-FD protocols

#### Board Firmware
**Main firmware**: `/home/runner/work/Catpilot/Catpilot/panda/board/main.c` (404 lines)
- Initializes hardware peripherals
- Sets up CAN transceivers
- Manages heartbeat mechanism
- Controls LED indicators
- Enforces safety modes

**Key initialization sequence** (from `main()` at line 297):
```c
1. Init interrupt table
2. Clock initialization
3. Detect board type
4. Enable peripherals (ADC, USB, SPI)
5. Set SAFETY_SILENT mode (default)
6. Enable CAN transceivers
7. Start 8Hz tick timer for heartbeat monitoring
8. Enable interrupts
```

---

## Safety System Architecture

### Safety Modes

**Location**: `/home/runner/work/Catpilot/Catpilot/panda/python/__init__.py` (Lines 119-144)

Safety modes control what CAN messages are allowed to be transmitted. The panda powers up in `SAFETY_SILENT` by default.

#### Available Safety Modes

| Mode ID | Name | Description | Use Case |
|---------|------|-------------|----------|
| 0 | `SAFETY_SILENT` | All CAN buses forced silent | Default/failsafe state |
| 19 | `SAFETY_NOOUTPUT` | Monitor only, no TX | Passive data logging |
| 17 | `SAFETY_ALLOUTPUT` | Unrestricted TX (DEBUG ONLY) | **Disabled in production firmware** |
| 3 | `SAFETY_ELM327` | OBD-II diagnostic mode | Reading diagnostic codes |
| 4 | `SAFETY_GM` | GM vehicles safety | **Used for 2021 Bolt** |
| 10 | `SAFETY_TESLA` | Tesla vehicles | - |
| 2 | `SAFETY_TOYOTA` | Toyota vehicles | - |
| ... | (other car brands) | Various car-specific modes | - |

#### GM Safety Mode Configuration

**For 2021 Chevy Bolt** (`SAFETY_GM`):
- **Safety parameter flags** (from `/selfdrive/car/gm/interface.py` line 100-104):
  ```python
  ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.gm)]
  if PEDAL_MSG in fingerprint[0]:
      ret.enableGasInterceptor = True
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_GM_GAS_INTERCEPTOR
  ```

- **Additional flags for Bolt with pedal**:
  - `FLAG_GM_HW_CAM` - Camera-based ACC hardware
  - `FLAG_GM_HW_CAM_LONG` - Camera-based longitudinal control enabled
  - `FLAG_GM_GAS_INTERCEPTOR` - Gas pedal interceptor present
  - `FLAG_GM_PEDAL_LONG` - Full longitudinal control via pedal (for no-ACC Bolts)

### Heartbeat Mechanism

**Location**: `/home/runner/work/Catpilot/Catpilot/panda/board/main.c` (Lines 143-272)

The panda requires periodic "heartbeat" messages from catpilot to maintain active safety modes:

```c
#define HEARTBEAT_IGNITION_CNT_ON 5U   // 5 seconds when ignition on
#define HEARTBEAT_IGNITION_CNT_OFF 2U  // 2 seconds when ignition off
```

**Behavior** (from `tick_handler()` at line 150):
1. Heartbeat counter increments at 8Hz
2. If counter exceeds threshold:
   - Switch to `SAFETY_SILENT` mode
   - Enter power save mode
   - Disable IR power
   - Clear `controls_allowed` flag
   - Activate siren (5 second countdown)

**Critical**: This is the primary safety mechanism preventing runaway control if catpilot crashes or loses communication.

### Controls Allowed State

**Location**: `main.c` lines 217-233

The `controls_allowed` flag enables/disables steering and throttle control:

```c
if (controls_allowed || heartbeat_engaged) {
    controls_allowed_countdown = 30U;  // 30 second timeout
}

// Exit controls if not actively engaged
if (controls_allowed && !heartbeat_engaged) {
    heartbeat_engaged_mismatches += 1U;
    if (heartbeat_engaged_mismatches >= 3U) {
        controls_allowed = false;  // Disengage after 3 seconds
    }
}
```

**LED Indicators**:
- **Green LED**: `controls_allowed` is active
- **Blue LED**: Power save mode active (blinks at 1Hz)
- **Red LED**: Heartbeat alive (fades in/out)

---

## CAN Bus Communication

### CAN Packet Structure

**Packet Header Size**: 6 bytes (`CANPACKET_HEAD_SIZE`)

**Header Format** (from `/panda/python/__init__.py` lines 38-58):
```
Byte 0: [DLC:4][Bus:3][Reserved:1]
Byte 1: Address[7:0]
Byte 2: Address[15:8]
Byte 3: Address[23:16]
Byte 4: Address[31:24]
Byte 5: Checksum (XOR of bytes 0-4 + data)
```

**DLC (Data Length Code) to Length Mapping**:
```python
DLC_TO_LEN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]
```

**Extended CAN**: Addresses >= 0x800 set extended bit in header

### Bus Numbering

**GM Vehicle Configuration** (Bolt):
```python
class CanBus:
    POWERTRAIN = 0  # Engine/transmission/EPS
    OBSTACLE = 1    # Radar
    CAMERA = 2      # Forward camera
    CHASSIS = 3     # Brakes/body control
```

### Python CAN Interface

**Location**: `/home/runner/work/Catpilot/Catpilot/panda/python/__init__.py`

#### Send CAN Message

```python
from panda import Panda

p = Panda()
p.set_safety_mode(Panda.SAFETY_GM)  # Must set safety mode first

# Send single message
p.can_send(address=0x180, dat=b"\x00\x01\x02\x03", bus=0)

# Send multiple messages (more efficient)
messages = [
    [0x180, None, b"\x00\x01\x02\x03", 0],  # [addr, _, data, bus]
    [0x181, None, b"\x04\x05", 0],
]
p.can_send_many(messages)
```

**Parameters**:
- `address`: CAN message ID (0x000-0x7FF standard, 0x800+ extended)
- `dat`: Message data (bytes, max 64 bytes for CAN-FD)
- `bus`: Bus number (0-3)
- `timeout`: Timeout in milliseconds (default 10ms)

#### Receive CAN Messages

```python
# Receive all pending messages
messages = p.can_recv()

# Returns list of tuples: [(address, 0, data, bus), ...]
for address, _, data, bus in messages:
    print(f"Bus {bus}: 0x{address:03x} = {data.hex()}")
```

**Bulk read**: Up to 16384 bytes per read from USB endpoint 1

#### CAN Configuration

```python
# Set bus speed (default 500 kbps)
p.set_can_speed_kbps(bus=0, speed=500)
p.set_can_speed_kbps(bus=1, speed=500)

# Enable/disable CAN transceiver
p.set_can_enable(bus_num=0, enable=True)

# Reset CAN communications
p.can_reset_communications()

# Clear TX queue or RX buffer
p.can_clear(bus=0)          # Clear specific bus TX queue
p.can_clear(bus=0xFFFF)     # Clear global RX queue
```

### C-Level CAN Functions

**Location**: `/home/runner/work/Catpilot/Catpilot/panda/board/main.c`

**Initialization** (line 121):
```c
can_init_all();  // Initialize all CAN peripherals
```

**Configuration**:
```c
current_board->set_can_mode(CAN_MODE_NORMAL);
current_board->enable_can_transceivers(true);
can_set_orientation(harness.status == HARNESS_STATUS_FLIPPED);
```

---

## Steering Torque Control System

### Overview

Steering in catpilot is **torque-based**, not angle-based. The system:
1. Calculates desired lateral acceleration from path planning
2. Converts lateral acceleration to steering rack torque
3. Applies rate limiting and driver override logic
4. Sends torque commands via CAN to the vehicle's EPS

### GM Steering Control Architecture

**Key Files**:
- `/selfdrive/car/gm/carcontroller.py` - Main control logic
- `/selfdrive/car/gm/gmcan.py` - CAN message creation
- `/selfdrive/car/gm/values.py` - Vehicle parameters
- `/selfdrive/controls/lib/latcontrol_torque.py` - Torque controller

### GM Steering Parameters

**Location**: `/selfdrive/car/gm/values.py` (Lines 13-24)

```python
class CarControllerParams:
    STEER_MAX = 300  # Maximum torque: 3Nm (GM limit)
    STEER_STEP = 3   # Active control: ~33Hz (every 3 frames at 100Hz)
    INACTIVE_STEER_STEP = 10  # Inactive: 10Hz
    STEER_DELTA_UP = 10      # Max increase per step
    STEER_DELTA_DOWN = 15    # Max decrease per step (faster release)
    STEER_DRIVER_ALLOWANCE = 65     # Driver torque threshold
    STEER_DRIVER_MULTIPLIER = 4
    STEER_DRIVER_FACTOR = 100
```

**Interpretation**:
- `STEER_MAX = 300`: Maps to 3Nm physical torque (internal units)
- `STEER_DELTA_UP/DOWN`: Rate limiting prevents abrupt changes
- Driver can apply torque without disengaging if below allowance

### Steering CAN Message Creation

**Location**: `/selfdrive/car/gm/gmcan.py` (Lines 44-52)

```python
def create_steering_control(packer, bus, apply_steer, idx, lkas_active):
    values = {
        "LKASteeringCmdActive": lkas_active,  # 0=inactive, 1=active
        "LKASteeringCmd": apply_steer,        # Torque value
        "RollingCounter": idx,                # 0-3 counter
        "LKASteeringCmdChecksum": 0x1000 - (lkas_active << 11) - (apply_steer & 0x7ff) - idx
    }
    return packer.make_can_msg("ASCMLKASteeringCmd", bus, values)
```

**CAN Message**: `ASCMLKASteeringCmd` on POWERTRAIN bus (0)
- Sent at 50Hz when active, 10Hz when inactive
- Includes checksum for message integrity
- Rolling counter prevents replay attacks

### Torque Application Logic

**Location**: `/selfdrive/car/gm/carcontroller.py` (Lines 108-117)

```python
if CC.latActive:
    new_steer = int(round(actuators.steer * self.params.STEER_MAX))
    apply_steer = apply_driver_steer_torque_limits(
        new_steer,
        self.apply_steer_last,
        CS.out.steeringTorque,  # Driver torque from wheel
        self.params
    )
else:
    apply_steer = 0

can_sends.append(gmcan.create_steering_control(
    self.packer_pt, CanBus.POWERTRAIN, apply_steer, idx, CC.latActive
))
```

**Process**:
1. `actuators.steer` comes from planner (normalized -1.0 to 1.0)
2. Scale to `STEER_MAX` (300 for GM)
3. Apply driver torque limits (prevents fighting driver)
4. Rate limit the change
5. Create CAN message
6. Send to panda

### Driver Torque Override Logic

**Location**: `/selfdrive/car/__init__.py` - `apply_driver_steer_torque_limits()`

```python
def apply_driver_steer_torque_limits(apply_torque, apply_torque_last, 
                                      driver_torque, params):
    # Check if driver is applying significant torque
    driver_max_torque = params.STEER_DRIVER_ALLOWANCE + \
                        abs(driver_torque) * params.STEER_DRIVER_MULTIPLIER / \
                        params.STEER_DRIVER_FACTOR
    
    # Don't apply more torque than driver allows
    apply_torque = clip(apply_torque, 
                       -driver_max_torque, 
                       driver_max_torque)
    
    # Rate limiting
    if apply_torque_last > 0:
        apply_torque = clip(apply_torque,
                           max(apply_torque_last - params.STEER_DELTA_DOWN, -params.STEER_DELTA_UP),
                           apply_torque_last + params.STEER_DELTA_UP)
    else:
        apply_torque = clip(apply_torque,
                           apply_torque_last - params.STEER_DELTA_UP,
                           min(apply_torque_last + params.STEER_DELTA_DOWN, params.STEER_DELTA_UP))
    
    return int(round(apply_torque))
```

**Key behaviors**:
- Driver torque creates a "window" for catpilot torque
- Torque changes are rate-limited to prevent jerky steering
- Asymmetric rates: can release faster than apply

### Lateral Acceleration to Torque Conversion

#### Neural Network Model (Bolt-specific)

**Location**: `/selfdrive/car/gm/interface.py` (Lines 79-90)

For the Chevy Bolt, catpilot uses a **neural network feedforward model**:

```python
if self.CP.carFingerprint in (CAR.CHEVROLET_BOLT_EUV, CAR.CHEVROLET_BOLT_CC):
    self.neural_ff_model = NanoFFModel(NEURAL_PARAMS_PATH, self.CP.carFingerprint)
    return self.torque_from_lateral_accel_neural

def torque_from_lateral_accel_neural(self, latcontrol_inputs, torque_params, ...):
    friction = get_friction(lateral_accel_error, ...)
    inputs = list(latcontrol_inputs)  # [lat_accel, gravity_adjusted, curvature, ...]
    if gravity_adjusted:
        inputs[0] += inputs[1]  # Add gravity component
    return float(self.neural_ff_model.predict(inputs)) + friction
```

**Inputs to Neural Network**:
1. Desired lateral acceleration (m/s²)
2. Gravity-adjusted component (for banking/grade)
3. Path curvature
4. Vehicle speed

**Output**: Steering torque in vehicle-specific units

**Neural network weights**: `/selfdrive/car/torque_data/neural_ff_weights.json`

#### Non-Linear Torque Params (Alternative Method)

**Location**: `/selfdrive/car/gm/interface.py` (Lines 29-34)

```python
NON_LINEAR_TORQUE_PARAMS = {
    CAR.CHEVROLET_BOLT_EUV: [2.6531724862969748, 1.0, 0.1919764879840985, 0.009054123646805178],
    CAR.CHEVROLET_BOLT_CC: [2.6531724862969748, 1.0, 0.1919764879840985, 0.009054123646805178],
    # [a, b, c, d] parameters for sigmoid + linear function
}
```

**Sigmoid + Linear Model** (lines 57-77):
```python
def sig(val):
    if val >= 0:
        return 1 / (1 + exp(-val)) - 0.5
    else:
        z = exp(val)
        return z / (1 + z) - 0.5

a, b, c, _ = non_linear_torque_params
steer_torque = (sig(lateral_accel * a) * b) + (lateral_accel * c)
return float(steer_torque) + friction
```

**Interpretation**:
- `a`: Sigmoid steepness (higher = more aggressive response)
- `b`: Sigmoid amplitude
- `c`: Linear component (ensures non-zero slope at 0)
- Friction added separately for static compensation

### Torque Controller (PID-based)

**Location**: `/selfdrive/controls/lib/latcontrol_torque.py`

This is the higher-level controller that generates desired torque:

```python
class LatControlTorque:
    def update(self, active, CS, VM, params, last_actuators, steer_limited, ...):
        # Calculate desired curvature from path
        desired_curvature = desired_curvature_last
        
        # Convert to lateral acceleration
        desired_lateral_accel = desired_curvature * CS.vEgo**2
        
        # Measure actual lateral acceleration
        actual_lateral_accel = measured_from_sensors
        
        # Low-speed compensation
        low_speed_factor = interp(CS.vEgo, LOW_SPEED_BP, LOW_SPEED_V)
        desired_lateral_accel += low_speed_factor * desired_curvature
        
        # Apply PID control
        error = desired_lateral_accel - actual_lateral_accel
        self.pid.update(error, ...)
        
        # Convert to torque using feedforward model
        output_torque = self.torque_from_lateral_accel(...)
        
        return -output_torque  # Negate for CAN convention
```

**Parameters** (from CarParams.LateralTorqueTuning):
- `kp`, `ki`, `kf`: PID coefficients
- `latAccelFactor`: Lat accel to torque scaling
- `friction`: Static friction threshold
- `useSteeringAngle`: Use wheel angle vs gyro
- `steeringAngleDeadzoneDeg`: Deadzone for angle control

---

## 2021 Chevrolet Bolt EV Configuration

### Vehicle Specifications

**Location**: `/selfdrive/car/gm/values.py` (Lines 160-166)

```python
CHEVROLET_BOLT_EUV = GMPlatformConfig(
    [
        GMCarDocs("Chevrolet Bolt EUV 2022-23", ...),
        GMCarDocs("Chevrolet Bolt EV 2022-23", ...),
    ],
    GMCarSpecs(
        mass=1669,           # kg
        wheelbase=2.63779,   # meters
        steerRatio=16.8,     # steering wheel angle / wheel angle
        centerToFrontRatio=0.4,
        tireStiffnessFactor=1.0
    ),
)
```

**Note**: 2021 Bolt EV uses same configuration as 2022-23 models

### CAN Bus Configuration

**Bolt uses Camera-based ACC** (CAMERA_ACC_CAR):
```python
ret.networkLocation = NetworkLocation.fwdCamera
ret.radarUnavailable = True  # No radar
ret.pcmCruise = True
ret.safetyConfigs[0].safetyParam |= Panda.FLAG_GM_HW_CAM
```

**Bus Layout**:
- **Bus 0 (POWERTRAIN)**: Steering, gas/brake, ECM, transmission
- **Bus 1 (OBSTACLE)**: Not used (no radar)
- **Bus 2 (CAMERA)**: Forward camera messages
- **Bus 3 (CHASSIS)**: Friction brakes, body control

### Key CAN Messages (Bolt)

#### Outgoing (catpilot → vehicle)

**Steering Command** - `ASCMLKASteeringCmd` (Bus 0):
- **Address**: Defined in DBC file
- **Rate**: 50Hz (active), 10Hz (inactive)
- **Data**:
  - `LKASteeringCmdActive`: Boolean
  - `LKASteeringCmd`: Torque (-300 to 300)
  - `RollingCounter`: 0-3
  - `LKASteeringCmdChecksum`: Integrity check

**Gas/Regen Command** - `ASCMGasRegenCmd` (Bus 0):
- **Rate**: 25Hz
- **Data**:
  - `GasRegenCmdActive`: Boolean
  - `GasRegenCmd`: Throttle position (0-65535)
  - `GasRegenFullStopActive`: At complete stop
  - Checksum

**Friction Brake Command** - `EBCMFrictionBrakeCmd` (Bus 0 or 3):
- **Rate**: 25Hz
- **Data**:
  - `FrictionBrakeCmd`: Brake pressure (0-4095)
  - `FrictionBrakeCmdActive`: Boolean
  - Mode byte (0x1=inactive, 0x9=active no brake, 0xa=braking, 0xd=full stop)

**Button Presses** - `ASCMSteeringButton` (Bus 0):
- Simulates steering wheel button presses for ACC control

#### Incoming (vehicle → catpilot)

**Steering Torque Sensor**:
- Driver applied torque
- EPS status
- Steering angle

**Vehicle Speed**:
- Wheel speeds
- Longitudinal acceleration

**Brake/Gas Pedals**:
- Brake pedal position
- Gas pedal position (or interceptor value)

**PSCM Status** - `PSCMStatus`:
- Hands-on-wheel detection
- LKA torque delivered (feedback)
- Driver applied torque

### Bolt-Specific Steering Tuning

**Location**: `/selfdrive/car/gm/interface.py` (Lines 204-210)

```python
elif candidate in (CAR.CHEVROLET_BOLT_EUV, CAR.CHEVROLET_BOLT_CC):
    ret.steerActuatorDelay = 0.2  # seconds
    CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)
    
    if ret.enableGasInterceptor:
        # ACC Bolts use pedal for full longitudinal control
        ret.flags |= GMFlags.PEDAL_LONG.value
```

**Torque tuning loaded from**: `/selfdrive/car/torque_data/override.toml` or `params.toml`

### Enable Speeds

**With Camera ACC** (Bolt EUV 2022+):
```python
ret.minEnableSpeed = 5 * CV.KPH_TO_MS    # 5 km/h
ret.minSteerSpeed = 10 * CV.KPH_TO_MS    # 10 km/h
```

**With Gas Interceptor Pedal** (lines 263-270):
```python
ret.minEnableSpeed = -1  # Can enable at any speed, even standstill
ret.stoppingControl = True
ret.autoResumeSng = True  # Stop-and-go capable
```

---

## Gas Interceptor Pedal Integration

### Overview

The gas interceptor pedal is a physical device that intercepts the accelerator pedal signal between the pedal position sensor and the ECM. It allows catpilot to:
- Override gas pedal input for longitudinal control
- Maintain full longitudinal control even on vehicles without ACC
- Enable stop-and-go functionality

**For 2021 Bolt**: Likely used on base models without ACC, or to enhance stop-and-go performance

### Detection

**Location**: `/selfdrive/car/gm/interface.py` (Lines 102-104)

```python
if PEDAL_MSG in fingerprint[0]:
    ret.enableGasInterceptor = True
    ret.safetyConfigs[0].safetyParam |= Panda.FLAG_GM_GAS_INTERCEPTOR
```

**Pedal Message**: `0x201` on bus 0

The presence of this message in the CAN fingerprint automatically enables pedal mode.

### Pedal Command Calculation

**Location**: `/selfdrive/car/gm/carcontroller.py` (Lines 59-71)

```python
@staticmethod
def calc_pedal_command(accel: float, long_active: bool) -> float:
    if not long_active: return 0.
    
    zero = 0.15625  # 40/256 (minimum pedal position)
    
    if accel > 0.:
        # Positive acceleration: scale 0-1 accel to 0.156-1.0 pedal
        pedal_gas = clip(((1 - zero) * accel + zero), 0., 1.)
    else:
        # Negative acceleration: use regen
        # -0.1 accel → 0.015625 pedal
        pedal_gas = clip(zero + accel, 0., zero)
    
    return pedal_gas
```

**Interpretation**:
- Pedal never goes to true 0 (minimum 40/256 = 15.6%)
- Positive accel: Linear scaling from 15.6% to 100%
- Negative accel: Small regen range (0-15.6%)
- Friction brakes used for stronger deceleration

### Pedal CAN Message

**Location**: `/selfdrive/car/__init__.py`

```python
def create_gas_interceptor_command(packer, gas_amount, idx):
    # gas_amount: 0.0 to 1.0
    enable = gas_amount > 0.001
    
    values = {
        "ENABLE": enable,
        "GAS_COMMAND": gas_amount,
        "GAS_COMMAND2": gas_amount,
        "COUNTER": idx,
    }
    return packer.make_can_msg("GAS_COMMAND", 0, values)
```

**Message**: `GAS_COMMAND` (0x200) on bus 0
- Sent at 25Hz (every 4th frame)
- Duplicated value for safety
- Counter for message validation

### Pedal Safety Flags

**Location**: `/selfdrive/car/gm/interface.py` (Lines 158-160, 263-274)

```python
if ret.enableGasInterceptor:
    # Set ASCM long limits when using pedal interceptor
    ret.safetyConfigs[0].safetyParam |= Panda.FLAG_GM_HW_ASCM_LONG
    
# For CC_ONLY_CAR (no ACC):
if candidate in CC_ONLY_CAR:
    ret.flags |= GMFlags.PEDAL_LONG.value
    ret.safetyConfigs[0].safetyParam |= Panda.FLAG_GM_PEDAL_LONG
```

**Panda Safety Flags** (from `/panda/python/__init__.py`):
```python
FLAG_GM_GAS_INTERCEPTOR = 256   # Pedal interceptor present
FLAG_GM_PEDAL_LONG = 128        # Full long control via pedal
FLAG_GM_HW_ASCM_LONG = 16       # ASCM-based long control limits
```

These flags tell the panda firmware:
1. A pedal interceptor is installed
2. Allow pedal commands in safety checks
3. Apply appropriate acceleration/deceleration limits

### Stop-and-Go with Pedal

**Location**: `/selfdrive/car/gm/carcontroller.py` (Lines 165-169)

```python
if self.CP.enableGasInterceptor and \
   self.apply_gas > self.params.INACTIVE_REGEN and \
   CS.out.cruiseState.standstill:
    # "Tap" the accelerator to re-engage ACC
    interceptor_gas_cmd = self.params.SNG_INTERCEPTOR_GAS  # 18/255 = 7%
    self.apply_brake = 0
    self.apply_gas = self.params.INACTIVE_REGEN
```

**Stop-and-Go (SNG) behavior**:
1. Vehicle comes to complete stop
2. catpilot waits for resume command
3. When resuming, briefly pulse pedal to 7% to "wake up" ACC
4. Transition to normal longitudinal control

**Parameters**:
```python
SNG_INTERCEPTOR_GAS = 18. / 255.  # 7% pedal
SNG_TIME = 30  # frames (0.3 seconds at 100Hz)
```

### Pedal Longitudinal Tuning

**Location**: `/selfdrive/car/gm/interface.py` (Lines 272-279)

```python
if candidate in CC_ONLY_CAR:
    ret.flags |= GMFlags.PEDAL_LONG.value
    ret.safetyConfigs[0].safetyParam |= Panda.FLAG_GM_PEDAL_LONG
    
    # PID tuning for pedal-based longitudinal
    ret.longitudinalTuning.kiBP = [0.0, 5., 35.]  # Speed breakpoints (m/s)
    ret.longitudinalTuning.kiV = [0.0, 0.35, 0.5]  # Integral gains
    ret.longitudinalTuning.kf = 0.15               # Feedforward
    ret.stoppingDecelRate = 0.8                    # m/s² when stopping
```

**Interpretation**:
- Integral gain increases with speed for stability
- No integral term at very low speeds (prevent overshoot)
- Gentle stopping deceleration rate

---

## How to Modify Torque Limits

### Understanding Current Limits

**Current Bolt steering limits** (from `/selfdrive/car/gm/values.py`):
```python
STEER_MAX = 300  # 3Nm maximum
STEER_DELTA_UP = 10    # Max increase per 30ms
STEER_DELTA_DOWN = 15  # Max decrease per 30ms
```

**Effective rate limits** (at 33Hz active steering):
- Maximum increase rate: 10 units / 30ms = **333 units/sec**
- Maximum decrease rate: 15 units / 30ms = **500 units/sec**
- Time to reach full torque from 0: **300 / 333 = 0.9 seconds**

### Method 1: Modify STEER_MAX (Most Direct)

**File**: `/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/values.py`

**Change**:
```python
class CarControllerParams:
    STEER_MAX = 400  # Increase from 300 to 400 (4Nm)
    # WARNING: Exceeding EPS limits may cause faults or damage
```

**Pros**:
- Simple, direct increase in max torque
- Proportional scaling of all torque commands

**Cons**:
- May exceed EPS hardware limits (likely 3-3.5Nm safe max)
- No safety testing at higher limits
- Could cause EPS overheating or faults

**RECOMMENDATION**: Do NOT exceed 350 (3.5Nm) without extensive testing

### Method 2: Modify Rate Limits (More Responsive)

**File**: `/home/runner/work/Catpilot/Catpilot/selfdrive/car/gm/values.py`

**Change**:
```python
class CarControllerParams:
    STEER_DELTA_UP = 15     # Increase from 10 to 15 (50% faster ramp-up)
    STEER_DELTA_DOWN = 20   # Increase from 15 to 20
```

**Pros**:
- Faster response to steering commands
- Stays within EPS torque limits
- More "aggressive" feel without exceeding hardware limits

**Cons**:
- May feel jerky if too high
- Could trigger EPS rate limit faults

**RECOMMENDATION**: Increase by 20-30% max, test carefully

### Method 3: Adjust Lateral Tuning Parameters

**File**: `/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/override.toml`

**Add or modify**:
```toml
[CHEVROLET_BOLT_EV]
LAT_ACCEL_FACTOR = 2.8  # Increase from default 2.6531
MAX_LAT_ACCEL = 2.5     # Increase max lateral accel target
FRICTION = 0.10         # Reduce friction compensation
```

**Explanation**:
- `LAT_ACCEL_FACTOR`: Scales lateral accel to torque (higher = more torque per lat accel)
- `MAX_LAT_ACCEL`: Maximum lateral acceleration target (m/s²)
- `FRICTION`: Static friction compensation (lower = less added torque)

**Pros**:
- Tuning-based approach
- Can be vehicle-specific
- Respects rate limits

**Cons**:
- Indirect control
- Requires understanding of vehicle dynamics

### Method 4: Modify Neural Network Weights (Advanced)

**File**: `/home/runner/work/Catpilot/Catpilot/selfdrive/car/torque_data/neural_ff_weights.json`

The Bolt uses a neural network to convert lateral acceleration to torque. Modifying the weights can change the torque response curve.

**CAUTION**: This requires machine learning expertise and extensive testing. Not recommended unless you understand neural network tuning.

### Method 5: Bypass Panda Safety Limits (UNSAFE)

**STRONGLY DISCOURAGED**: You can compile custom panda firmware with modified safety limits, but this:
- Removes critical safety protections
- Could cause loss of control
- Voids all warranties
- May be illegal in your jurisdiction

**If you must**: Edit panda safety hooks in board firmware (source not included in this repo) and recompile/flash.

### Testing Procedure

After any torque limit modifications:

1. **Bench test**: Run catpilot in simulation mode, verify limits in logs
2. **Parking lot test**: Test at <10 mph on closed course
3. **Low-speed test**: Drive 10-30 mph, gentle maneuvers
4. **Highway test**: 40-60 mph, verify stability
5. **Emergency maneuver**: Test maximum steering input, verify no faults

**Monitor for**:
- EPS fault codes
- Steering wheel kickback or oscillation
- Loss of power steering
- Unusual EPS noises (whining, clicking)

**Log analysis**:
```python
# Check applied vs requested torque
import pandas as pd
log = pd.read_csv('steering_log.csv')
print(f"Max applied: {log['steer_applied'].max()}")
print(f"Max requested: {log['steer_requested'].max()}")
print(f"Saturation %: {(log['steer_applied'] == 300).mean() * 100}%")
```

High saturation percentage indicates you're hitting limits frequently.

---

## How to Pass CAN Traffic for Interior Accessories

### Understanding CAN Message Filtering

The panda's safety mode controls which CAN messages are allowed through:

1. **TX (Transmit)**: catpilot → vehicle
   - Safety mode validates each message before transmission
   - Only whitelisted messages in safety hooks are allowed

2. **RX (Receive)**: vehicle → catpilot
   - All messages received (no filtering on input)
   - Used for monitoring vehicle state

3. **Forwarding**: bus-to-bus forwarding
   - Some safety modes allow forwarding between buses
   - Example: Forward camera messages from bus 2 to bus 0

### Current GM Safety Mode Behavior

**Default GM mode** (`SAFETY_GM`):
- Allows: Steering, gas/regen, brake, button presses
- Blocks: All other messages (including most accessory messages)

**Accessory messages typically blocked**:
- Climate control commands
- Seat heaters/coolers
- Infotainment controls
- Window/mirror controls
- Door lock commands

### Method 1: Use SAFETY_ALLOUTPUT Mode (Testing Only)

**WARNING**: This disables ALL safety checks. Use ONLY for testing/development, NEVER for driving.

```python
from panda import Panda
p = Panda()

# Enable all output (requires debug firmware)
p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

# Now you can send any CAN message
p.can_send(0x250, b"\x01\x02\x03", bus=0)  # Climate control example
```

**Limitations**:
- Requires dev/debug panda firmware
- Disabled in production firmware
- No safety protections active

### Method 2: Modify Safety Hooks (Firmware Modification)

To permanently allow specific accessory messages, you must modify the panda firmware safety hooks.

**Process** (high-level, firmware source not in this repo):

1. Locate GM safety hook file (board/safety/safety_gm.h or similar)
2. Add message IDs to TX whitelist
3. Recompile panda firmware
4. Flash to panda device

**Example pseudo-code**:
```c
// In safety_gm.h TX hook
static int gm_tx_hook(CANPacket_t *to_send) {
    int addr = GET_ADDR(to_send);
    
    // Existing allowed messages
    if (addr == 0x180) return 1;  // Steering
    if (addr == 0x2CB) return 1;  // Gas/regen
    
    // Add your accessory messages here
    if (addr == 0x250) return 1;  // Climate control (example)
    if (addr == 0x251) return 1;  // Seat heater (example)
    
    return 0;  // Block all others
}
```

**CAUTION**: 
- Requires C programming and embedded systems knowledge
- Must understand CAN message formats for each accessory
- Risk of accidentally allowing dangerous messages
- Extensive testing required

### Method 3: Use a Second Panda (Recommended Approach)

For accessory control without modifying safety code:

**Setup**:
1. **Panda 1**: Main catpilot control (steering, brakes, gas)
   - Use standard `SAFETY_GM` mode
   - Handles all vehicle control

2. **Panda 2**: Accessory control only
   - Use `SAFETY_ALLOUTPUT` mode (debug firmware)
   - OR use `SAFETY_NOOUTPUT` + custom relay hardware
   - Isolated from vehicle control systems

**Wiring**:
- Panda 1: Connected to main OBD-II port
- Panda 2: Connected via separate CAN tap to accessory bus (typically bus 3/chassis)

**Software**:
```python
from panda import Panda

# Main control panda
panda_main = Panda(serial='main_serial_here')
panda_main.set_safety_mode(Panda.SAFETY_GM)

# Accessory control panda
panda_accessory = Panda(serial='accessory_serial_here')
panda_accessory.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

# Now send accessory commands through second panda
panda_accessory.can_send(0x250, b"\x01\x02\x03", bus=0)  # Climate
panda_accessory.can_send(0x251, b"\x05", bus=0)          # Seat heater
```

**Pros**:
- Complete isolation from safety-critical systems
- No firmware modifications needed
- Easy to add/remove

**Cons**:
- Requires second panda device (~$100)
- More complex wiring
- Two USB connections needed

### Method 4: User Space Relay (Software-Only)

**Concept**: Use catpilot's "bridge mode" to relay specific messages.

**Implementation** (pseudo-code):
```python
# In catpilot custom process
from panda import Panda
p = Panda()

# List of allowed accessory message IDs
ACCESSORY_WHITELIST = [0x250, 0x251, 0x252]  # Your specific messages

while True:
    # Receive all messages
    messages = p.can_recv()
    
    # Filter and forward accessory messages
    for addr, _, data, bus in messages:
        if addr in ACCESSORY_WHITELIST:
            # Forward to appropriate bus
            p.can_send(addr, data, target_bus)
    
    time.sleep(0.01)
```

**Pros**:
- No firmware changes
- Easy to modify whitelist
- Can add conditional logic

**Cons**:
- Higher latency (user-space processing)
- Still limited by panda's safety mode TX restrictions
- CPU overhead

### Reverse Engineering Accessory CAN Messages

To control accessories, you must first identify their CAN messages:

**Tools**:
- `can_logger.py` (in panda/examples/)
- Commercial CAN analyzers (Vector CANalyzer, etc.)
- Wireshark with SocketCAN

**Process**:
1. **Capture baseline**: Record CAN traffic with accessory off
2. **Activate accessory**: Press button/turn knob
3. **Capture active**: Record CAN traffic with accessory on
4. **Diff the logs**: Identify messages that changed
5. **Isolate control message**: Send candidate messages, verify effect

**Example - Climate Control**:
```bash
# Start logging
python panda/examples/can_logger.py > log_baseline.txt

# User: turn on AC
python panda/examples/can_logger.py > log_ac_on.txt

# Diff the files
diff log_baseline.txt log_ac_on.txt

# Output might show:
# + 0x250: 01 00 00 00 00 00 00 00
```

**Testing**:
```python
# Try sending the identified message
from panda import Panda
p = Panda()
p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)  # Testing only!
p.can_send(0x250, b"\x01\x00\x00\x00\x00\x00\x00\x00", bus=0)

# Observe: Does AC turn on?
```

### GM-Specific Accessory Buses

**Typical GM bus layout**:
- **Bus 0 (Powertrain)**: Engine, transmission, EPS
- **Bus 1 (GMLAN)**: Body control, accessories, infotainment
- **Bus 2 (Camera)**: ADAS camera
- **Bus 3 (Chassis)**: Brakes, suspension, some accessories

**For Bolt**, most interior accessories are on:
- **Bus 0** or **Bus 3** (varies by year/trim)

**Common accessory message addresses** (approximate, verify for your vehicle):
- `0x1E1`: HVAC control
- `0x1E5`: Seat heaters
- `0x3D1`: Infotainment
- `0x4E1`: Door locks
- `0x4E5`: Window controls

**IMPORTANT**: These are examples only. You MUST reverse engineer your specific vehicle's messages.

---

## Safety Output Controls

### The "SAFETY_ALLOUTPUT" Problem

The issue states: "*we want to pass can bus traffic to control interior accessories and to increase the amount of steering torque that can be requested or re-enable SAFETY_ALL_OUTPUT*"

**Understanding SAFETY_ALLOUTPUT**:
- **Purpose**: Debug/development mode
- **Behavior**: Allows ANY CAN message to be transmitted
- **Safety**: NONE - bypasses all safety checks
- **Availability**: Disabled in production firmware

### Why SAFETY_ALLOUTPUT Is Disabled

**From `/panda/README.md` lines 20-22**:
> "Some of safety modes (for example `SAFETY_ALLOUTPUT`) are disabled in release firmwares. In order to use them, compile and flash your own build."

**Reason**: Allowing unrestricted CAN message transmission is extremely dangerous:
- Could send unintended steering/brake commands
- No rate limiting or sanity checks
- Could override safety systems (ABS, stability control)
- Risk of loss of control

**Safety philosophy**: panda should be the "last line of defense" against catpilot software bugs or malicious code.

### Re-enabling SAFETY_ALLOUTPUT (Not Recommended)

**Process**:

1. **Clone panda repository**:
   ```bash
   git clone https://github.com/commaai/panda.git
   cd panda
   ```

2. **Modify firmware build config** (location varies, typically in board/Makefile or board/config.h):
   ```c
   // Enable SAFETY_ALLOUTPUT in release builds
   #define ALLOW_DEBUG 1
   ```

3. **Compile firmware**:
   ```bash
   cd board
   make clean
   make  # or: make all
   ```

4. **Flash to panda**:
   ```bash
   python flash.py
   # Or via DFU mode:
   # python recover.py
   ```

5. **Verify**:
   ```python
   from panda import Panda
   p = Panda()
   p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
   # Should succeed without error
   ```

**WARNINGS**:
- This removes critical safety protections
- Responsibility for safe operation is entirely on you
- Extensive testing required before any on-road use
- May violate local laws/regulations
- Could cause serious injury or death if misused

### Alternative: Expand GM Safety Hook Whitelist (Safer Approach)

Instead of enabling SAFETY_ALLOUTPUT, expand the GM safety mode to allow specific additional messages:

**Firmware modification** (pseudo-code, actual source not in this repo):

```c
// In board/safety/safety_gm.h

// Add accessory message IDs
#define GM_CLIMATE_CONTROL_ADDR 0x250
#define GM_SEAT_HEATER_ADDR 0x251

static int gm_tx_hook(CANPacket_t *to_send) {
    int addr = GET_ADDR(to_send);
    int bus = GET_BUS(to_send);
    
    // Existing safety checks for steering/brakes/gas
    // ...
    
    // Add accessory message whitelist
    if (bus == 0 || bus == 3) {  // Powertrain or chassis bus
        if (addr == GM_CLIMATE_CONTROL_ADDR) {
            // Optional: add value range checks here
            return 1;  // Allow
        }
        if (addr == GM_SEAT_HEATER_ADDR) {
            // Optional: add value range checks here
            return 1;  // Allow
        }
    }
    
    return 0;  // Block all others
}
```

**Pros**:
- Maintains safety checks for steering/brakes
- Allows specific accessory control
- Can add value validation (e.g., limit climate temp range)

**Cons**:
- Still requires firmware modification
- Need to identify exact message IDs for your vehicle
- Requires C programming knowledge

### Safety Output Monitoring

**Panda provides health monitoring** to track message transmission:

```python
from panda import Panda
p = Panda()

# Get panda health status
health = p.health()

print(f"Safety TX blocked count: {health['safety_tx_blocked']}")
print(f"Safety RX invalid count: {health['safety_rx_invalid']}")
print(f"CAN send errors: {health['can_send_errs']}")
print(f"CAN forward errors: {health['can_fwd_errs']}")
```

**Interpretation**:
- `safety_tx_blocked`: Messages catpilot tried to send but were blocked by safety mode
- `safety_rx_invalid`: Malformed messages received (checksum/length errors)
- High counts indicate safety mode is actively blocking messages (expected behavior)

**Per-bus CAN health**:
```python
for bus in range(4):
    health = p.can_health(bus)
    print(f"Bus {bus}:")
    print(f"  TX errors: {health['can_tx_errs']}")
    print(f"  RX errors: {health['can_rx_errs']}")
    print(f"  Bus off: {health['bus_off']}")
    print(f"  Bus off cnt: {health['bus_off_cnt']}")
```

**Use this to detect**:
- CAN bus hardware issues
- Message overflow/congestion
- Transceiver faults

### Gradual Approach to Custom Safety Modes

**Recommended development process**:

1. **Phase 1 - Research**:
   - Reverse engineer accessory CAN messages
   - Document message IDs, data formats, rates
   - Test with SAFETY_ALLOUTPUT on private property only

2. **Phase 2 - Safety Design**:
   - Define whitelist of safe accessory messages
   - Design value range checks (e.g., valid temp range)
   - Design rate limits for accessory messages
   - Document failure modes

3. **Phase 3 - Implementation**:
   - Modify panda firmware with expanded whitelist
   - Add value validation logic
   - Compile and flash firmware

4. **Phase 4 - Testing**:
   - Bench test: verify whitelisted messages pass, others block
   - Parking lot: test accessory control at standstill
   - Low-speed: verify no interference with steering/brakes
   - Highway: stress test with concurrent steering and accessory use

5. **Phase 5 - Validation**:
   - Log all safety_tx_blocked events
   - Verify no unintended messages are allowed
   - Test emergency scenarios (hard brake + accessory use)

**Only proceed to next phase after passing all tests in current phase.**

---

## Conclusion & Summary

### Critical Safety Reminders

1. **Never disable safety checks for on-road driving**
2. **Understand that modifying panda firmware or safety modes removes critical protections**
3. **Test exhaustively in controlled environments before any real-world use**
4. **You are solely responsible for safe operation after any modifications**

### Key Takeaways

**Panda Architecture**:
- STM32 microcontroller running safety-critical firmware
- Enforces safety at hardware level before messages reach CAN bus
- Heartbeat mechanism prevents runaway control

**CAN Communication**:
- 6-byte header + data, checksummed
- Multiple buses (powertrain, chassis, camera, radar)
- Rate-limited to prevent bus congestion

**Steering Control**:
- Torque-based (not angle-based)
- Max 3Nm (300 units) for GM
- Rate-limited for safety (10 units up, 15 units down per step)
- Driver override protection

**2021 Bolt Configuration**:
- Camera-based ACC (bus 2)
- Neural network torque conversion
- Supports gas interceptor pedal for full longitudinal control
- Stop-and-go capable with pedal

**Increasing Torque**:
- Safest: Modify rate limits (STEER_DELTA_UP/DOWN)
- Moderate: Adjust STEER_MAX (do not exceed 350)
- Advanced: Tune lateral acceleration parameters

**Accessory Control**:
- Safest: Use second panda for accessories
- Moderate: Expand GM safety whitelist in firmware
- Dangerous: Enable SAFETY_ALLOUTPUT (testing only!)

### Next Steps

**For Understanding**:
- Read panda README: `/panda/README.md`
- Study GM DBC files for CAN message definitions
- Review catpilot safety documentation

**For Development**:
- Set up development environment with panda simulator
- Use `can_logger.py` to reverse engineer vehicle messages
- Test modifications in simulation before hardware

**For Deployment**:
- Follow gradual testing approach outlined above
- Maintain detailed logs of all modifications
- Have rollback plan (keep stock firmware)

### Support Resources

**Documentation**:
- Panda GitHub: https://github.com/commaai/panda
- catpilot Documentation: https://github.com/commaai/catpilot/tree/master/docs
- DBC File Browser: https://github.com/commaai/opendbc

**Community**:
- comma.ai Discord: https://discord.comma.ai
- catpilot/panda GitHub Issues
- Vehicle-specific forums (Bolt EV forums, etc.)

**Tools**:
- CANalyzer / Wireshark for CAN analysis
- Vector hardware for professional CAN testing
- PandaJ (jungle) for multi-panda setups

---

## Appendix: File Reference Quick Guide

### Key Files for Steering/Torque

| File | Purpose | Key Lines |
|------|---------|-----------|
| `/panda/board/main.c` | Panda firmware main | 1-404 (all) |
| `/panda/python/__init__.py` | Python panda interface | 119-144 (safety modes), 769-770 (set safety), 813-842 (CAN send/recv) |
| `/selfdrive/car/gm/values.py` | GM vehicle parameters | 13-24 (steering params), 160-194 (Bolt config) |
| `/selfdrive/car/gm/carcontroller.py` | GM steering control | 108-117 (torque application) |
| `/selfdrive/car/gm/gmcan.py` | GM CAN messages | 44-52 (steering msg) |
| `/selfdrive/car/gm/interface.py` | GM car interface | 88-94 (torque conversion), 204-210 (Bolt tuning) |
| `/selfdrive/controls/lib/latcontrol_torque.py` | Lateral torque controller | 1-100+ (PID control) |

### Key Files for Gas Pedal Interceptor

| File | Purpose | Key Lines |
|------|---------|-----------|
| `/selfdrive/car/gm/interface.py` | Pedal detection/config | 102-104 (detect), 158-160 (safety), 263-274 (tuning) |
| `/selfdrive/car/gm/carcontroller.py` | Pedal command calc | 59-71 (calc), 161-178 (integration) |
| `/selfdrive/car/__init__.py` | CAN message creation | create_gas_interceptor_command() |

### Key Files for Safety Modes

| File | Purpose | Key Lines |
|------|---------|-----------|
| `/panda/python/__init__.py` | Safety mode constants | 119-144 |
| `/panda/board/main.c` | Safety mode enforcement | 60-122 (set_safety_mode) |
| `/panda/README.md` | Safety documentation | 18-26 |

### Configuration Files

| File | Purpose |
|------|---------|
| `/selfdrive/car/torque_data/override.toml` | Vehicle-specific torque overrides |
| `/selfdrive/car/torque_data/params.toml` | Default torque parameters |
| `/selfdrive/car/torque_data/neural_ff_weights.json` | Neural network weights (Bolt) |

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-14  
**Target Vehicle**: 2021 Chevrolet Bolt EV with Gas Interceptor Pedal  
**Author**: AI Analysis of Catpilot/Panda Codebase

