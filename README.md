# Microservice Discovery Demo

This project demonstrates a simple microservice system with service discovery.

## Services

- **Service Registry**: keeps track of active services
- **Inventory Service**: two running instances
- **Order Service**: discovers inventory instances and calls one at random

## Requirements covered

- Run 2 service instances
- Register with registry
- Client discovers service
- Client calls random instance

---

## Prerequisites

- Python 3
- Flask installed
- requests installed
- PowerShell (Windows)

Install dependencies if needed:

```powershell
pip install flask requests
```

## 1. Start the registry

```powershell
python service_registry_improved.py
```

## 2. Start inventory service instance 1

```powershell
python inventory_service.py 8002
```

## 3. Start inventory service instance 2

```powershell
python inventory_service.py 8003
```

## 4. Start Order Service

```powershell
python order_service.py
```

### Place an order

```powershell
$body = @{
    customer = "Alice"
    item     = "laptop"
    qty      = 1
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8004/orders" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Placing multiple orders

```powershell
1..5 | ForEach-Object {
    $body = @{
        customer = "DemoUser$_"
        item     = "laptop"
        qty      = 1
    } | ConvertTo-Json

    Invoke-RestMethod `
        -Uri "http://localhost:8004/orders" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
}
```

### Test out of stock item

```powershell
$body = @{
    customer = "Charlie"
    item     = "keyboard"
    qty      = 1
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8004/orders" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```
