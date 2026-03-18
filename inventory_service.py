# inventory_service.py
from flask import Flask, jsonify, request
from registry_client import RegistryClient
import sys
import signal

app = Flask(__name__)

# simple in-memory stock
STOCK = {
    "laptop": 5,
    "mouse": 10,
    "keyboard": 0,
    "phone": 3
}

registry_client = None
instance_port = None

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "inventory-service", "port": instance_port})

@app.route("/inventory/<item_id>", methods=["GET"])
def check_inventory(item_id):
    qty = int(request.args.get("qty", 1))
    available = STOCK.get(item_id, 0)

    return jsonify({
        "service": "inventory-service",
        "instance_port": instance_port,
        "item": item_id,
        "requested_qty": qty,
        "available_qty": available,
        "in_stock": available >= qty
    })

def shutdown_handler(sig, frame):
    if registry_client:
        registry_client.stop()
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inventory_service.py <port>")
        sys.exit(1)

    instance_port = int(sys.argv[1])
    service_address = f"http://localhost:{instance_port}"

    registry_client = RegistryClient(
        service_name="inventory-service",
        service_address=service_address
    )
    registry_client.start()

    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host="0.0.0.0", port=instance_port, debug=True)