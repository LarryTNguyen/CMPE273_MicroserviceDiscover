# order_service.py
from flask import Flask, request, jsonify
from registry_client import RegistryClient
import requests
import random
import signal
import sys

app = Flask(__name__)

registry_client = None
instance_port = 8004
orders = []

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "order-service", "port": instance_port})

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json or {}
    item = data.get("item")
    qty = int(data.get("qty", 1))
    customer = data.get("customer", "anonymous")

    if not item:
        return jsonify({"error": "item is required"}), 400

    # discover inventory-service instances
    instances = registry_client.discover("inventory-service")
    if not instances:
        return jsonify({"error": "No inventory-service instances available"}), 503

    # choose random instance
    chosen = random.choice(instances)
    inventory_url = chosen["address"]

    try:
        response = requests.get(
            f"{inventory_url}/inventory/{item}",
            params={"qty": qty},
            timeout=5
        )
        response.raise_for_status()
        inventory_result = response.json()
    except Exception as e:
        return jsonify({
            "error": "Failed to contact inventory service",
            "details": str(e),
            "called_instance": inventory_url
        }), 502

    if not inventory_result["in_stock"]:
        return jsonify({
            "status": "failed",
            "message": f"{item} is out of stock",
            "checked_instance": inventory_url,
            "inventory_response": inventory_result
        }), 409

    order = {
        "order_id": len(orders) + 1,
        "customer": customer,
        "item": item,
        "qty": qty,
        "status": "placed",
        "checked_instance": inventory_url
    }
    orders.append(order)

    return jsonify(order), 201

@app.route("/orders", methods=["GET"])
def list_orders():
    return jsonify({"orders": orders, "count": len(orders)})

def shutdown_handler(sig, frame):
    if registry_client:
        registry_client.stop()
    sys.exit(0)

if __name__ == "__main__":
    service_address = f"http://localhost:{instance_port}"

    registry_client = RegistryClient(
        service_name="order-service",
        service_address=service_address
    )
    registry_client.start()

    signal.signal(signal.SIGINT, shutdown_handler)
    app.run(host="0.0.0.0", port=instance_port, debug=True)