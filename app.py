import os
import csv
import io
from datetime import datetime, date
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from models import db, Product, Transaction, CATEGORIES

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kiosk.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def dashboard():
    products = Product.query.all()
    total_products = len(products)
    low_stock_items = [p for p in products if p.is_low_stock]
    total_value = sum(p.total_value for p in products)
    return render_template("dashboard.html", products=products, low_stock_items=low_stock_items,
                           total_products=total_products, total_value=total_value,
                           low_stock_count=len(low_stock_items), categories=CATEGORIES)


@app.route("/products")
def products_page():
    products = Product.query.all()
    return render_template("products.html", products=products, categories=CATEGORIES)


@app.route("/transactions")
def transactions_page():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    products = Product.query.all()
    return render_template("transactions.html", transactions=transactions, products=products, categories=CATEGORIES)


@app.route("/reports")
def reports_page():
    return render_template("reports.html", categories=CATEGORIES)


# API: Products
@app.route("/api/products", methods=["GET"])
def api_get_products():
    search = request.args.get("search", "").strip().lower()
    category = request.args.get("category", "").strip()
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category == category)
    products = query.order_by(Product.name).all()
    return jsonify([p.to_dict() for p in products])


@app.route("/api/products", methods=["POST"])
def api_create_product():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Product name is required"}), 400
    if not data.get("category") or data["category"] not in CATEGORIES:
        return jsonify({"error": f"Category must be one of: {', '.join(CATEGORIES)}"}), 400
    if data.get("unit_price") is None or data["unit_price"] < 0:
        return jsonify({"error": "Valid unit price is required"}), 400
    product = Product(
        name=data["name"].strip(),
        category=data["category"],
        quantity=int(data.get("quantity", 0)),
        unit_price=float(data["unit_price"]),
        reorder_level=int(data.get("reorder_level", 5)),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@app.route("/api/products/<int:product_id>", methods=["GET"])
def api_get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def api_update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "name" in data:
        product.name = data["name"].strip()
    if "category" in data:
        if data["category"] not in CATEGORIES:
            return jsonify({"error": f"Category must be one of: {', '.join(CATEGORIES)}"}), 400
        product.category = data["category"]
    if "quantity" in data:
        product.quantity = int(data["quantity"])
    if "unit_price" in data:
        product.unit_price = float(data["unit_price"])
    if "reorder_level" in data:
        product.reorder_level = int(data["reorder_level"])
    db.session.commit()
    return jsonify(product.to_dict())


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})


# API: Transactions
@app.route("/api/transactions", methods=["POST"])
def api_create_transaction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    product_id = data.get("product_id")
    trans_type = data.get("type")
    quantity = data.get("quantity")
    if not product_id or not trans_type or quantity is None:
        return jsonify({"error": "product_id, type, and quantity are required"}), 400
    if trans_type not in ("sale", "restock"):
        return jsonify({"error": "Type must be 'sale' or 'restock'"}), 400
    if quantity <= 0:
        return jsonify({"error": "Quantity must be positive"}), 400
    product = Product.query.get_or_404(product_id)
    if trans_type == "sale":
        if product.quantity < quantity:
            return jsonify({"error": f"Insufficient stock. Available: {product.quantity}"}), 400
        product.quantity -= quantity
    else:
        product.quantity += quantity
    transaction = Transaction(product_id=product_id, type=trans_type, quantity=quantity)
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction.to_dict()), 201


@app.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    product_id = request.args.get("product_id", type=int)
    trans_type = request.args.get("type", "").strip()
    date_filter = request.args.get("date", "").strip()
    query = Transaction.query
    if product_id:
        query = query.filter(Transaction.product_id == product_id)
    if trans_type:
        query = query.filter(Transaction.type == trans_type)
    if date_filter:
        try:
            target = datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Transaction.date) == target)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])


# API: Reports
@app.route("/api/reports/low-stock", methods=["GET"])
def api_low_stock_report():
    products = Product.query.filter(Product.quantity <= Product.reorder_level).all()
    return jsonify([p.to_dict() for p in products])


@app.route("/api/reports/daily", methods=["GET"])
def api_daily_report():
    report_date = request.args.get("date", date.today().isoformat())
    try:
        target = datetime.strptime(report_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    transactions = Transaction.query.filter(db.func.date(Transaction.date) == target).all()
    sales = [t for t in transactions if t.type == "sale"]
    restocks = [t for t in transactions if t.type == "restock"]
    return jsonify({
        "date": report_date,
        "total_sales": len(sales),
        "total_restocks": len(restocks),
        "units_sold": sum(t.quantity for t in sales),
        "units_restocked": sum(t.quantity for t in restocks),
        "transactions": [t.to_dict() for t in transactions],
    })


@app.route("/api/reports/export/csv", methods=["GET"])
def api_export_csv():
    report_type = request.args.get("type", "products")
    si = io.StringIO()
    writer = csv.writer(si)
    if report_type == "products":
        writer.writerow(["ID", "Name", "Category", "Quantity", "Unit Price", "Reorder Level", "Total Value", "Low Stock"])
        for p in Product.query.all():
            writer.writerow([p.id, p.name, p.category, p.quantity, p.unit_price, p.reorder_level, p.total_value, "Yes" if p.is_low_stock else "No"])
    elif report_type == "transactions":
        writer.writerow(["ID", "Product", "Type", "Quantity", "Date"])
        for t in Transaction.query.order_by(Transaction.date.desc()).all():
            writer.writerow([t.id, t.product.name if t.product else "Unknown", t.type, t.quantity, t.date.isoformat()])
    elif report_type == "low-stock":
        writer.writerow(["ID", "Name", "Category", "Quantity", "Reorder Level", "Unit Price"])
        for p in Product.query.filter(Product.quantity <= Product.reorder_level).all():
            writer.writerow([p.id, p.name, p.category, p.quantity, p.reorder_level, p.unit_price])
    else:
        return jsonify({"error": "Invalid report type"}), 400
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={report_type}_report.csv"})


# API: Dashboard summary
@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    products = Product.query.all()
    low_stock = [p for p in products if p.is_low_stock]
    return jsonify({
        "total_products": len(products),
        "low_stock_count": len(low_stock),
        "total_value": round(sum(p.total_value for p in products), 2),
        "low_stock_items": [p.to_dict() for p in low_stock],
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
