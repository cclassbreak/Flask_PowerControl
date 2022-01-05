# Mannual for Power Control Web App

## Config
In `config.ini` file, there are several config parameters that can be modifed per requirement.
### PowerSupply
The following are parameters in `PowerSupply` section.
#### - MODEL
Here states the model of the Power Supply. The value can be either `APC` or `Ainuo`.
#### - COM_PORT
Here states the COM port using in this webserver that connects to the power supply. The value can be `COM1`, `COM2`, `COM11`...etc.

### Website
The following are parameters in `Website` section.
#### - ACCOUNT
Here states the account info when logging to the website. The value is a string.
#### - PASSWORD
Here states the password info when logging to the website. The value is a string.

### Info
The following are parameters in `Info` section.
#### - VERSION
Here states the version info. The value is like `1.0.0`, `1.0.1`, `1.1.0` etc.
***
## test_step.yaml
In the `test_step.yaml` file, all test steps are configued.
The format is like the following. 

NOTE: a `#` represents a `space` key.
```
SITE
#Product
##Model
###-
####phase: str ABC,ACB,BAC.....SFC-A,SFC-B,SFC-C
####voltage: int
####frequency: int
```

Here is an example:
```
CN9A:
 CT:
  US-Product:
   -
    phase: ABC
    voltage: 418 
    frequency: 60
  SY-Product:
   -
    phase: ABC
    voltage: 418
    frequency: 60
   -
    phase: ACB
    voltage: 418
    frequency: 60
   -
    phase: BAC
    voltage: 418
    frequency: 60
   -
    phase: CBA
    voltage: 418
    frequency: 60
   -
    phase: SFC-A
    voltage: 418
    frequency: 60
   -
    phase: SFC-B
    voltage: 418
    frequency: 60
   -
    phase: SFC-C
    voltage: 418
    frequency: 60
 DXR:
  DXR-Product-1:
   -
    phase: ABC
    voltage: 418 
    frequency: 60
  DXR-Product-2:
   -
    phase: ABC
    voltage: 418
    frequency: 60
   -
    phase: ACB
    voltage: 418
    frequency: 60
   -
    phase: BAC
    voltage: 418
    frequency: 60
   -
    phase: CBA
    voltage: 418
    frequency: 60
   -
    phase: SFC-A
    voltage: 418
    frequency: 60
   -
    phase: SFC-B
    voltage: 418
    frequency: 60
   -
    phase: SFC-C
    voltage: 418
    frequency: 60


CN9B:
 CT:
  US-Product:
   -
    phase: ABC
    voltage: 418 
    frequency: 50
   -
    phase: ACB
    voltage: 418
    frequency: 50
   -
    phase: BAC
    voltage: 418 
    frequency: 50
   -
    phase: CBA
    voltage: 418 
    frequency: 50
   -
    phase: SFC-A
    voltage: 380 
    frequency: 50
   -
    phase: SFC-B
    voltage: 380
    frequency: 50
   -
    phase: SFC-C
    voltage: 380
    frequency: 50
  SY-Product:
   -
    phase: ABC
    voltage: 418
    frequency: 50
   -
    phase: ACB
    voltage: 418
    frequency: 50
   -
    phase: BAC
    voltage: 418
    frequency: 50
   -
    phase: CBA
    voltage: 418
    frequency: 50
   -
    phase: SFC-A
    voltage: 418
    frequency: 50
   -
    phase: SFC-B
    voltage: 418
    frequency: 50
   -
    phase: SFC-C
    voltage: 418
    frequency: 50
 DXR:
  DXR-Product-1:
   -
    phase: ABC
    voltage: 418 
    frequency: 50
   -
    phase: ACB
    voltage: 418
    frequency: 50
   -
    phase: BAC
    voltage: 418 
    frequency: 50
   -
    phase: CBA
    voltage: 418 
    frequency: 50
   -
    phase: SFC-A
    voltage: 380 
    frequency: 50
   -
    phase: AC
    voltage: 380
    frequency: 50
   -
    phase: SFC-A
    voltage: 380
    frequency: 50
  DXR-Product-2:
   -
    phase: ABC
    voltage: 418
    frequency: 50
   -
    phase: ACB
    voltage: 418
    frequency: 50
   -
    phase: BAC
    voltage: 418
    frequency: 50
   -
    phase: CBA
    voltage: 418
    frequency: 50
   -
    phase: SFC-A
    voltage: 418
    frequency: 50
   -
    phase: AC
    voltage: 418
    frequency: 50
   -
    phase: AB
    voltage: 418
    frequency: 50
```