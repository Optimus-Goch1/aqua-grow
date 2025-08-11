# Farm Sensor Monitoring API

This API allows for secure monitoring of farm sensors with proper authentication mechanisms to ensure data integrity and security.

## Authentication Mechanism

The system uses a multi-layered authentication approach:

1. **User Authentication**: JWT-based authentication for farm owners
2. **Device Authentication**: Each ESP32 device is registered with its MAC address and assigned a unique API key
3. **Farm Ownership Verification**: Ensures users can only access data from farms they own

## Setup Process

### 1. Register an ESP32 Device

Before an ESP32 device can send data, it must be registered:

```bash
curl -X POST "http://your-server/sensors/register-device" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"farm_id": "your-farm-id", "mac_address": "xx:xx:xx:xx:xx:xx"}'
```

This will return an API key that must be used for all subsequent requests from that device.

### 2. Send Sensor Data from ESP32

The ESP32 device must include its API key and MAC address in the headers when sending data:

```bash
curl -X POST "http://your-server/sensors/data" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "X-Device-MAC: xx:xx:xx:xx:xx:xx" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "your-farm-id", 
    "moisture": 450.0, 
    "temperature": 25.5, 
    "humidity": 65.0
  }'
```

### 3. Retrieve Farm Data

Farm owners can retrieve data from their farms using their JWT token:

```bash
curl -X GET "http://your-server/sensors/your-farm-id" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Considerations

- Use HTTPS in production to encrypt all communications
- Store API keys securely on the ESP32 devices
- Consider implementing rate limiting to prevent abuse
- Regularly audit device registrations and revoke access for compromised devices

## ESP32 Implementation

See the `src/utils.py` file for example code demonstrating how to send authenticated requests from an ESP32 device.

## Simulating Sensor Data

For testing purposes, you can simulate sensor data using the `/sensors/simulate` endpoint:

```bash
curl -X POST "http://your-server/sensors/simulate" \
  -H "Content-Type: application/json" \
  -d '{"farm_id": "test-farm"}'
```
