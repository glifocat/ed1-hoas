# SmartIR Integration Guide for ED1

Esta guía explica cómo integrar la placa ED1 con [SmartIR](https://github.com/smartHomeHub/SmartIR) para controlar dispositivos IR desde Home Assistant.

## ¿Qué es SmartIR?

SmartIR es una integración de Home Assistant que permite controlar dispositivos de climatización, ventiladores y reproductores multimedia mediante infrarrojos. Utiliza una base de datos con miles de códigos IR predefinidos.

## Arquitectura

```
┌─────────────┐     IR      ┌─────────┐     WiFi      ┌──────────────┐
│ Mando a     │────────────→│   ED1   │──────────────→│  Home        │
│ distancia   │             │ SmartIR │               │  Assistant   │
└─────────────┘             │ Bridge  │               │  + SmartIR   │
                            │         │←──────────────│              │
                            │         │   Servicios   │              │
                            └────┬────┘               └──────────────┘
                                 │
                                 │ IR
                                 ↓
                            ┌─────────┐
                            │ TV/Aire │
                            │ etc.    │
                            └─────────┘
```

## Hardware Requerido

### ED1 Rev 1.0 (Recomendado)

- **IR Receiver**: GPIO33
- **IR Transmitter**: GPIO32 (LED IR integrado)
- **Capacidad**: RX + TX completo

### ED1 Rev 2.3

- **IR Receiver**: GPIO35
- **IR Transmitter**: No disponible (necesita módulo externo)
- **Capacidad**: Solo recepción

## Configuración

### 1. Instalar el firmware

Copia [`ed1-smartir-bridge.yaml`](../ed1-smartir-bridge.yaml) a tu directorio de ESPHome y compila:

```bash
esphome run ed1-smartir-bridge.yaml
```

### 2. Configurar pines según revisión

Para **Rev 1.0** (edita el archivo YAML):

```yaml
substitutions:
  ir_receiver_pin: "GPIO33"
  # Descomenta la siguiente línea:
  ir_transmitter_pin: "GPIO32"

packages:
  # ... otros paquetes ...
  ir_tx: !include packages/ir-transmitter.yaml # Descomenta esta línea
```

Para **Rev 2.3**:

```yaml
substitutions:
  ir_receiver_pin: "GPIO35"
  # No hay transmisor disponible
```

### 3. Instalar SmartIR en Home Assistant

#### Opción A: HACS (Recomendado)

1. Instala [HACS](https://hacs.xyz/)
2. Ve a HACS → Integrations
3. Busca "SmartIR" e instálalo
4. Reinicia Home Assistant

#### Opción B: Manual

```bash
cd config/custom_components
git clone https://github.com/smartHomeHub/SmartIR.git
```

### 4. Configurar SmartIR

Añade a tu `configuration.yaml`:

```yaml
smartir:

climate:
  - platform: smartir
    name: Aire Acondicionado Sala
    unique_id: ac_sala
    device_code: 1060 # Código de tu modelo
    controller_data:
      service: esphome.ed1_smartir_bridge_send_ir_nec
      address: 0x4004
    temperature_sensor: sensor.temperatura_sala
    humidity_sensor: sensor.humedad_sala

fan:
  - platform: smartir
    name: Ventilador Dormitorio
    unique_id: fan_dorm
    device_code: 1020
    controller_data:
      service: esphome.ed1_smartir_bridge_send_ir_nec
      address: 0x0707

media_player:
  - platform: smartir
    name: TV Salón
    unique_id: tv_salon
    device_code: 1060
    controller_data:
      service: esphome.ed1_smartir_bridge_send_ir_nec
      address: 0x0400
```

## Uso del Bridge

### Capturar Códigos IR

#### Método 1: Modo Aprender (en el dispositivo)

1. Pulsa el botón "IR Learn Mode" en Home Assistant
2. Selecciona un slot (0-9)
3. Apunta tu mando a la ED1 y pulsa un botón
4. El código se guarda automáticamente

#### Método 2: Eventos en Home Assistant

1. Abre **Developer Tools → Events**
2. Escucha el evento `esphome.ed1_ir_received`
3. Pulsa cualquier botón del mando
4. Verás los datos del código recibido

### Enviar Códigos IR

#### Desde Servicios de HA

```yaml
service: esphome.ed1_smartir_bridge_send_ir_nec
data:
  address: 16388 # 0x4004 en decimal
  command: 2295 # 0x08F7 en decimal
```

```yaml
service: esphome.ed1_smartir_bridge_send_ir_lg
data:
  data: 551489775 # Código LG en decimal
```

#### Desde Slots Aprendidos

Usa los botones "IR Send Slot X" para emitir códigos previamente guardados.

## Entidades Disponibles

| Entidad                                       | Tipo   | Descripción                   |
| --------------------------------------------- | ------ | ----------------------------- |
| `text.ed1_smartir_bridge_last_ir_protocol`    | Texto  | Último protocolo detectado    |
| `text.ed1_smartir_bridge_last_ir_code`        | Texto  | Último código recibido        |
| `sensor.ed1_smartir_bridge_ir_activity_count` | Sensor | Contador de códigos recibidos |
| `button.ed1_smartir_bridge_ir_learn_mode`     | Botón  | Activar modo aprender         |
| `button.ed1_smartir_bridge_ir_learn_stop`     | Botón  | Detener modo aprender         |
| `button.ed1_smartir_bridge_ir_send_slot_0`    | Botón  | Emitir código del slot 0      |

## Servicios Disponibles

| Servicio                                      | Descripción           | Parámetros           |
| --------------------------------------------- | --------------------- | -------------------- |
| `esphome.ed1_smartir_bridge_send_ir_nec`      | Enviar código NEC     | `address`, `command` |
| `esphome.ed1_smartir_bridge_send_ir_lg`       | Enviar código LG      | `data`               |
| `esphome.ed1_smartir_bridge_send_ir_samsung`  | Enviar código Samsung | `data`               |
| `esphome.ed1_smartir_bridge_send_ir_sony`     | Enviar código Sony    | `data`, `nbits`      |
| `esphome.ed1_smartir_bridge_send_ir_rc5`      | Enviar código RC5     | `address`, `command` |
| `esphome.ed1_smartir_bridge_start_learn_mode` | Iniciar modo aprender | `slot` (0-9)         |
| `esphome.ed1_smartir_bridge_stop_learn_mode`  | Detener modo aprender | -                    |

## Encontrar Códigos de Dispositivos

### Base de datos SmartIR

Visita [smartir.readthedocs.io](https://smartir.readthedocs.io) para ver la lista completa de códigos soportados.

### Códigos comunes

| Dispositivo | Marca   | Código SmartIR | Protocolo |
| ----------- | ------- | -------------- | --------- |
| TV          | LG      | 1060           | NEC/LG    |
| TV          | Samsung | 1020, 1040     | Samsung   |
| TV          | Sony    | 1010           | Sony      |
| A/C         | LG      | 1060           | NEC       |
| A/C         | Samsung | 1200           | NEC       |

### Capturar códigos personalizados

Si tu dispositivo no está en la base de datos:

1. Usa el modo aprender de la ED1
2. Captura cada botón del mando
3. Anota los valores `address` y `command`
4. Crea un archivo JSON de configuración para SmartIR

## Solución de Problemas

### No recibe códigos IR

- Verifica que el pin RX esté correctamente configurado
- Asegúrate de que el receptor IR no esté obstruido
- Comprueba que el mando tenga batería

### No emite códigos IR (Rev 1.0)

- Verifica que el transmisor IR esté descomentado en el YAML
- Usa la cámara de tu móvil para ver si el LED IR parpadea
- Asegúrate de que la ED1
