from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Dummy database
deposits = []

# Property listings database
properties = [
    {
        "id": 1,
        "name": "Skyline Apartments",
        "location": "BKC, Mumbai",
        "rent": 45000,
        "deposit_months": 4,
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=80",
        "description": "Modern apartment in the heart of BKC with city views, gym, and 24/7 security.",
        "available": True
    },
    {
        "id": 2,
        "name": "Green Grove Villa",
        "location": "Whitefield, Bengaluru",
        "rent": 60000,
        "deposit_months": 3,
        "image": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&q=80",
        "description": "Spacious villa with private pool, lush garden, and modern interiors in Whitefield.",
        "available": True
    },
    {
        "id": 3,
        "name": "Pearl Heights",
        "location": "Banjara Hills, Hyderabad",
        "rent": 35000,
        "deposit_months": 2,
        "image": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80",
        "description": "Premium 2BHK in Banjara Hills with covered parking, club house, and lake view.",
        "available": True
    },
    {
        "id": 4,
        "name": "The Urban Nest",
        "location": "Connaught Place, Delhi",
        "rent": 55000,
        "deposit_months": 3,
        "image": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80",
        "description": "Stylish studio in CP with metro access, furnished interiors, and co-working space.",
        "available": True
    }
]


# ──────────────────────────────────────────────
#  HOME
# ──────────────────────────────────────────────
@app.route('/')
def home():
    return "Rental Deposit API Running"


# ──────────────────────────────────────────────
#  DEPOSIT ROUTES
# ──────────────────────────────────────────────
@app.route('/add_deposit', methods=['POST'])
def add_deposit():
    data = request.json
    deposit = {
        "tenant":   data['tenant'],
        "landlord": data['landlord'],
        "amount":   data['amount'],
        "rate":     data['rate'],
        "time":     data['time'],
        "date":     str(datetime.datetime.now())
    }
    deposits.append(deposit)
    return jsonify({"message": "Deposit added successfully"})


@app.route('/get_deposits', methods=['GET'])
def get_deposits():
    return jsonify(deposits)


@app.route('/calculate/<int:index>', methods=['GET'])
def calculate(index):
    if index >= len(deposits):
        return jsonify({"error": "Deposit not found"}), 404
    deposit = deposits[index]
    P  = deposit['amount']
    R  = deposit['rate']
    T  = deposit['time']
    SI = (P * R * T) / 100
    return jsonify({"principal": P, "interest": SI, "total": P + SI})


# ──────────────────────────────────────────────
#  PROPERTY ROUTES
# ──────────────────────────────────────────────

# Get all properties (supports ?available=true/false filter)
@app.route('/get_properties', methods=['GET'])
def get_properties():
    available_filter = request.args.get('available')
    if available_filter is not None:
        filtered = [p for p in properties if str(p['available']).lower() == available_filter.lower()]
        return jsonify(filtered)
    return jsonify(properties)


# Search properties by name or location
@app.route('/search_properties', methods=['GET'])
def search_properties():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify(properties)
    results = [
        p for p in properties
        if query in p['name'].lower() or query in p['location'].lower()
    ]
    return jsonify(results)


# Get single property detail
@app.route('/get_property/<int:property_id>', methods=['GET'])
def get_property(property_id):
    prop = next((p for p in properties if p["id"] == property_id), None)
    if prop is None:
        return jsonify({"error": "Property not found"}), 404
    return jsonify(prop)


# Add a new property
@app.route('/add_property', methods=['POST'])
def add_property():
    data = request.json

    # Validate required fields
    required_fields = ['name', 'location', 'rent', 'deposit_months']
    for field in required_fields:
        if field not in data or data[field] in [None, '']:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate numeric fields
    try:
        rent = float(data['rent'])
        deposit_months = int(data['deposit_months'])
    except (ValueError, TypeError):
        return jsonify({"error": "rent and deposit_months must be valid numbers"}), 400

    if rent <= 0 or deposit_months <= 0:
        return jsonify({"error": "rent and deposit_months must be positive"}), 400

    new_id = max(p["id"] for p in properties) + 1 if properties else 1
    prop = {
        "id":             new_id,
        "name":           data['name'].strip(),
        "location":       data['location'].strip(),
        "rent":           rent,
        "deposit_months": deposit_months,
        "image":          data.get('image') or 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80',
        "description":    data.get('description', '').strip(),
        "available":      data.get('available', True),
        "date_added":     str(datetime.datetime.now())
    }
    properties.append(prop)
    return jsonify({"message": "Property added successfully", "property": prop}), 201


# Update an existing property
@app.route('/update_property/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    prop = next((p for p in properties if p["id"] == property_id), None)
    if prop is None:
        return jsonify({"error": "Property not found"}), 404

    data = request.json
    updatable_fields = ['name', 'location', 'rent', 'deposit_months', 'image', 'description', 'available']
    for field in updatable_fields:
        if field in data:
            prop[field] = data[field]

    return jsonify({"message": "Property updated successfully", "property": prop})


# Delete a property
@app.route('/delete_property/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    global properties
    prop = next((p for p in properties if p["id"] == property_id), None)
    if prop is None:
        return jsonify({"error": "Property not found"}), 404
    properties = [p for p in properties if p["id"] != property_id]
    return jsonify({"message": "Property deleted successfully"})


# Calculate deposit amount for a property
@app.route('/property_deposit/<int:property_id>', methods=['GET'])
def property_deposit(property_id):
    prop = next((p for p in properties if p["id"] == property_id), None)
    if prop is None:
        return jsonify({"error": "Property not found"}), 404
    deposit_amount = prop['rent'] * prop['deposit_months']
    return jsonify({
        "property":       prop['name'],
        "rent":           prop['rent'],
        "deposit_months": prop['deposit_months'],
        "deposit_amount": deposit_amount
    })


# Toggle property availability
@app.route('/toggle_availability/<int:property_id>', methods=['PATCH'])
def toggle_availability(property_id):
    prop = next((p for p in properties if p["id"] == property_id), None)
    if prop is None:
        return jsonify({"error": "Property not found"}), 404
    prop['available'] = not prop['available']
    return jsonify({"message": "Availability updated", "available": prop['available']})


# ──────────────────────────────────────────────
#  STATS / DASHBOARD ROUTE  (for Growth page)
# ──────────────────────────────────────────────

@app.route('/get_stats', methods=['GET'])
def get_stats():
    total_properties   = len(properties)
    available_count    = sum(1 for p in properties if p['available'])
    unavailable_count  = total_properties - available_count
    total_deposit_pool = sum(p['rent'] * p['deposit_months'] for p in properties)
    avg_rent           = (sum(p['rent'] for p in properties) / total_properties) if total_properties else 0

    total_deposits     = len(deposits)
    total_principal    = sum(d['amount'] for d in deposits)
    total_interest     = sum((d['amount'] * d['rate'] * d['time']) / 100 for d in deposits)

    return jsonify({
        "properties": {
            "total":             total_properties,
            "available":         available_count,
            "unavailable":       unavailable_count,
            "total_deposit_pool": total_deposit_pool,
            "avg_rent":          round(avg_rent, 2)
        },
        "deposits": {
            "total":          total_deposits,
            "total_principal": total_principal,
            "total_interest":  round(total_interest, 2),
            "total_value":     round(total_principal + total_interest, 2)
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
