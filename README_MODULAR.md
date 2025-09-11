# TBM GUI - Modular Structure

This is a modular version of the Tunnel Boring Machine Operator GUI, split into logical components for better maintainability and extensibility.

## Project Structure

```
gui_server/
├── tbm_gui.py                    # Original monolithic GUI
├── tbm_gui_modular.py            # New modular main GUI
├── widgets/                      # Reusable UI components
│   ├── __init__.py
│   ├── linear_gauge.py          # Linear gauge widget
│   ├── system_status.py         # System status and power controls
│   └── terminal.py              # Terminal/logging widget
├── tabs/                        # Tab-specific components
│   ├── __init__.py
│   ├── main_tab.py             # Main overview tab
│   ├── engine_tab.py           # Engine/cutterhead tab
│   └── pump_tab.py             # Pump monitoring tab
└── simulation/                  # Data simulation
    ├── __init__.py
    └── data_simulator.py       # Realistic data simulation
```

## Components

### Widgets (`widgets/`)

#### LinearGauge (`widgets/linear_gauge.py`)
- Custom linear gauge with safe zones and danger markers
- Color-coded warnings (green/yellow/red)
- Configurable ranges and thresholds
- Triangle markers for current values

#### SystemStatusWidget (`widgets/system_status.py`)
- System status indicators (Power, Warning, Running)
- Power control buttons (POWER ON, POWER OFF, STOP MACHINE)
- Mode selection buttons (Main, Engine/Cutterhead, Pump)
- State management with proper button enabling/disabling

#### TerminalWidget (`widgets/terminal.py`)
- Logging terminal for system messages
- Color-coded message levels (INFO, WARNING, ERROR)
- Timestamped entries
- Auto-scroll functionality

### Tabs (`tabs/`)

#### MainTab (`tabs/main_tab.py`)
- High-level system overview
- Motor temperature gauge
- Cutter head RPM gauge
- Pump temperature gauge
- Explosive gas level gauge

#### EngineTab (`tabs/engine_tab.py`)
- Detailed engine and cutterhead monitoring
- Motor temperature gauge
- Cutter head RPM gauge
- Cutter head voltage gauge

#### PumpTab (`tabs/pump_tab.py`)
- Pump and flow monitoring
- Pump temperature gauge
- Coolant flow gauge
- Soil treatment flow gauge

### Simulation (`simulation/`)

#### DataSimulator (`simulation/data_simulator.py`)
- Realistic sensor data simulation
- Configurable update intervals
- Warning detection and logging
- Spam prevention for repeated warnings

## Usage

### Running the Modular Version
```bash
python tbm_gui_modular.py
```

### Running the Original Version
```bash
python tbm_gui.py
```

## Benefits of Modular Structure

1. **Maintainability**: Each component is self-contained and easier to modify
2. **Reusability**: Widgets can be reused across different parts of the application
3. **Testability**: Individual components can be tested in isolation
4. **Extensibility**: New tabs or widgets can be added without modifying existing code
5. **Separation of Concerns**: UI, logic, and simulation are clearly separated
6. **Code Organization**: Related functionality is grouped together

## Adding New Components

### Adding a New Widget
1. Create a new file in `widgets/`
2. Inherit from appropriate Qt widget
3. Add to `widgets/__init__.py`

### Adding a New Tab
1. Create a new file in `tabs/`
2. Inherit from QWidget
3. Add to `tabs/__init__.py`
4. Import and add to main GUI

### Adding New Simulation Features
1. Extend `DataSimulator` class
2. Add new sensor data generation
3. Implement new warning conditions

## Dependencies

- PyQt5
- Python 3.6+

## Features

- **System Status Monitoring**: Real-time status indicators
- **Power Control**: Safe power on/off sequences
- **Linear Gauges**: Professional industrial-style gauges
- **Tabbed Interface**: Organized information display
- **Terminal Logging**: Comprehensive system logging
- **Realistic Simulation**: Dynamic sensor data
- **Warning System**: Color-coded alerts and notifications
- **Full-Screen Mode**: Optimized for operator use 