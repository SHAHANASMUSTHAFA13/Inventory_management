from flask import Flask, render_template, url_for, request, redirect, flash, send_file
from flask_mysqldb import MySQL
import MySQLdb
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.secret_key = "inventory_secret_2025"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "flaskuser"
app.config["MYSQL_PASSWORD"] = "mypassword123"
app.config["MYSQL_DB"] = "inventory"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


def validate_numeric(value, field_name, min_value=0):
    try:
        num = int(value) if isinstance(value, str) else value
        if num < min_value:
            return False, f"{field_name} must be at least {min_value}."
        return True, num
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number."


@app.route("/debug_tables")
def debug_tables():
    try:
        with mysql.connection.cursor() as con:
            con.execute("SHOW TABLES")
            tables = con.fetchall()
        return "<pre>" + "\n".join([str(table['Tables_in_inventory']) for table in tables]) + "</pre>"
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/debug_templates")
def debug_templates():
    import os
    template_dir = app.jinja_loader.searchpath[0]
    templates = os.listdir(template_dir)
    return "<pre>" + "\n".join(templates) + "</pre>"


@app.route("/")
def home():
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT * FROM Product")
            products = con.fetchall()
            con.execute("SELECT * FROM Location")
            locations = con.fetchall()
            con.execute("SELECT movement_id, timestamp, from_location, to_location, product_id, qty FROM ProductMovement ORDER BY timestamp DESC LIMIT 5")
            movements = con.fetchall()
        return render_template("home.html", products=products, locations=locations, movements=movements)
    except Exception as e:
        flash(f"Failed to load dashboard: {str(e)}", "error")
        return render_template("home.html", products=[], locations=[], movements=[])


@app.route("/products")
def view_products():
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT * FROM Product")
            products = con.fetchall()
        return render_template("products.html", products=products)
    except Exception as e:
        flash(f"Failed to load products: {str(e)}", "error")
        return render_template("products.html", products=[])


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        try:
            product_id = request.form["product_id"].strip()
            name = request.form["name"].strip()
            sku = request.form["sku"].strip()
            category = request.form.get("category", "").strip()
            supplier = request.form.get("supplier", "").strip()
            price = request.form["price"]

            if not product_id or not name or not sku:
                flash("Product ID, name, and SKU are required.", "error")
                return redirect(url_for("add_product"))

            valid_price, price_result = validate_numeric(price, "Price", min_value=0.01)
            if not valid_price:
                flash(price_result, "error")
                return redirect(url_for("add_product"))
            price = float(price_result)

            with mysql.connection.cursor() as con:
                sql = """
                    INSERT INTO Product (product_id, name, sku, category, supplier, price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                con.execute(sql, (product_id, name, sku, category, supplier, price))
                mysql.connection.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for("view_products"))
        except MySQLdb.IntegrityError as e:
            if "Duplicate entry" in str(e):
                flash("Product ID or SKU already exists.", "error")
            else:
                flash(f"Database error: {str(e)}", "error")
            return redirect(url_for("add_product"))
        except Exception as e:
            flash(f"Error adding product: {str(e)}", "error")
            return redirect(url_for("add_product"))
    return render_template("add_product.html")


@app.route("/edit_product/<string:id>", methods=["GET", "POST"])
def edit_product(id):
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT * FROM Product WHERE product_id=%s", [id])
            product = con.fetchone()
            if not product:
                flash("Product not found.", "error")
                return redirect(url_for("view_products"))
    except Exception as e:
        flash(f"Error loading product: {str(e)}", "error")
        return redirect(url_for("view_products"))

    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            sku = request.form["sku"].strip()
            category = request.form.get("category", "").strip()
            supplier = request.form.get("supplier", "").strip()
            price = request.form["price"]

            if not name or not sku:
                flash("Name and SKU are required.", "error")
                return redirect(url_for("edit_product", id=id))

            valid_price, price_result = validate_numeric(price, "Price", min_value=0.01)
            if not valid_price:
                flash(price_result, "error")
                return redirect(url_for("edit_product", id=id))
            price = float(price_result)

            with mysql.connection.cursor() as con:
                sql = """
                    UPDATE Product 
                    SET name=%s, sku=%s, category=%s, supplier=%s, price=%s 
                    WHERE product_id=%s
                """
                con.execute(sql, (name, sku, category, supplier, price, id))
                mysql.connection.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for("view_products"))
        except MySQLdb.IntegrityError as e:
            if "Duplicate entry" in str(e):
                flash("SKU already exists.", "error")
            else:
                flash(f"Database error: {str(e)}", "error")
            return redirect(url_for("edit_product", id=id))
        except Exception as e:
            flash(f"Error updating product: {str(e)}", "error")
            return redirect(url_for("edit_product", id=id))
    return render_template("edit_product.html", product=product)


@app.route("/delete_product/<string:id>")
def delete_product(id):
    try:
        with mysql.connection.cursor() as con:
            con.execute("DELETE FROM Product WHERE product_id=%s", [id])
            mysql.connection.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting product: {str(e)}", "error")
    return redirect(url_for("view_products"))


@app.route("/locations")
def view_locations():
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT * FROM Location")
            locations = con.fetchall()
        return render_template("locations.html", locations=locations)
    except Exception as e:
        flash(f"Failed to load locations: {str(e)}", "error")
        return render_template("locations.html", locations=[])


@app.route("/add_location", methods=["GET", "POST"])
def add_location():
    if request.method == "POST":
        try:
            location_id = request.form["location_id"].strip()
            city = request.form.get("city", "").strip()

            if not location_id:
                flash("Location ID is required.", "error")
                return redirect(url_for("add_location"))

            with mysql.connection.cursor() as con:
                sql = "INSERT INTO Location (location_id, city) VALUES (%s, %s)"
                con.execute(sql, (location_id, city))
                mysql.connection.commit()
            flash("Location added successfully!", "success")
            return redirect(url_for("view_locations"))
        except MySQLdb.IntegrityError as e:
            flash("Location ID already exists.", "error")
            return redirect(url_for("add_location"))
        except Exception as e:
            flash(f"Error adding location: {str(e)}", "error")
            return redirect(url_for("add_location"))
    return render_template("add_location.html")


@app.route("/edit_location/<string:id>", methods=["GET", "POST"])
def edit_location(id):
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT * FROM Location WHERE location_id=%s", [id])
            location = con.fetchone()
            if not location:
                flash("Location not found.", "error")
                return redirect(url_for("view_locations"))
    except Exception as e:
        flash(f"Error loading location: {str(e)}", "error")
        return redirect(url_for("view_locations"))

    if request.method == "POST":
        try:
            city = request.form.get("city", "").strip()
            with mysql.connection.cursor() as con:
                sql = "UPDATE Location SET city=%s WHERE location_id=%s"
                con.execute(sql, (city, id))
                mysql.connection.commit()
            flash("Location updated successfully!", "success")
            return redirect(url_for("view_locations"))
        except Exception as e:
            flash(f"Error updating location: {str(e)}", "error")
            return redirect(url_for("edit_location", id=id))
    return render_template("edit_location.html", location=location)


@app.route("/delete_location/<string:id>")
def delete_location(id):
    try:
        with mysql.connection.cursor() as con:
            con.execute("DELETE FROM Location WHERE location_id=%s", [id])
            mysql.connection.commit()
        flash("Location deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting location: {str(e)}", "error")
    return redirect(url_for("view_locations"))


@app.route("/movements")
def view_movements():
    try:
        with mysql.connection.cursor() as con:
            sql = """
                SELECT 
                    pm.movement_id, pm.timestamp, pm.from_location, pm.to_location, 
                    pm.product_id, pm.qty,
                    p.name AS product_name,
                    l1.city AS from_location_name,
                    l2.city AS to_location_name
                FROM ProductMovement pm
                JOIN Product p ON pm.product_id = p.product_id
                LEFT JOIN Location l1 ON pm.from_location = l1.location_id
                LEFT JOIN Location l2 ON pm.to_location = l2.location_id
                ORDER BY pm.timestamp DESC
            """
            con.execute(sql)
            movements = con.fetchall()
        return render_template("movements.html", movements=movements)
    except Exception as e:
        flash(f"Failed to load movements: {str(e)}", "error")
        return render_template("movements.html", movements=[])


@app.route("/add_movement", methods=["GET", "POST"])
def add_movement():
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT product_id, name FROM Product")
            products = con.fetchall()
            con.execute("SELECT location_id, city FROM Location")
            locations = con.fetchall()
    except Exception as e:
        flash(f"Error loading form data: {str(e)}", "error")
        return render_template("add_movement.html", products=[], locations=[])

    if request.method == "POST":
        try:
            movement_id = request.form["movement_id"].strip()
            product_id = request.form["product_id"]
            from_location = request.form.get("from_location") or None
            to_location = request.form.get("to_location") or None
            qty = request.form["qty"]

            if not movement_id:
                flash("Movement ID is required.", "error")
                return redirect(url_for("add_movement"))
            if not product_id:
                flash("Product is required.", "error")
                return redirect(url_for("add_movement"))
            if not from_location and not to_location:
                flash("At least one of 'From Location' or 'To Location' must be specified.", "error")
                return redirect(url_for("add_movement"))

            valid_qty, qty_result = validate_numeric(qty, "Quantity", min_value=1)
            if not valid_qty:
                flash(qty_result, "error")
                return redirect(url_for("add_movement"))
            qty = qty_result

            with mysql.connection.cursor() as con:
                sql = """
                    INSERT INTO ProductMovement 
                    (movement_id, from_location, to_location, product_id, qty) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                con.execute(sql, (movement_id, from_location, to_location, product_id, qty))
                mysql.connection.commit()
            flash("Movement recorded successfully!", "success")
            return redirect(url_for("view_movements"))
        except MySQLdb.IntegrityError as e:
            flash("Movement ID already exists.", "error")
            return redirect(url_for("add_movement"))
        except Exception as e:
            flash(f"Error recording movement: {str(e)}", "error")
            return redirect(url_for("add_movement"))
    return render_template("add_movement.html", products=products, locations=locations)


@app.route("/edit_movement/<string:id>", methods=["GET", "POST"])
def edit_movement(id):
    try:
        with mysql.connection.cursor() as con:
            con.execute("SELECT movement_id, timestamp, from_location, to_location, product_id, qty FROM ProductMovement WHERE movement_id=%s", [id])
            movement = con.fetchone()
            if not movement:
                flash("Movement not found.", "error")
                return redirect(url_for("view_movements"))
            con.execute("SELECT product_id, name FROM Product")
            products = con.fetchall()
            con.execute("SELECT location_id, city FROM Location")
            locations = con.fetchall()
    except Exception as e:
        flash(f"Error loading movement: {str(e)}", "error")
        return redirect(url_for("view_movements"))

    if request.method == "POST":
        try:
            product_id = request.form["product_id"]
            from_location = request.form.get("from_location") or None
            to_location = request.form.get("to_location") or None
            qty = request.form["qty"]

            if not product_id:
                flash("Product is required.", "error")
                return redirect(url_for("edit_movement", id=id))
            if not from_location and not to_location:
                flash("At least one of 'From Location' or 'To Location' must be specified.", "error")
                return redirect(url_for("edit_movement", id=id))

            valid_qty, qty_result = validate_numeric(qty, "Quantity", min_value=1)
            if not valid_qty:
                flash(qty_result, "error")
                return redirect(url_for("edit_movement", id=id))
            qty = qty_result

            with mysql.connection.cursor() as con:
                sql = """
                    UPDATE ProductMovement 
                    SET from_location=%s, to_location=%s, product_id=%s, qty=%s 
                    WHERE movement_id=%s
                """
                con.execute(sql, (from_location, to_location, product_id, qty, id))
                mysql.connection.commit()
            flash("Movement updated successfully!", "success")
            return redirect(url_for("view_movements"))
        except Exception as e:
            flash(f"Error updating movement: {str(e)}", "error")
            return redirect(url_for("edit_movement", id=id))
    return render_template("edit_movement.html", movement=movement, products=products, locations=locations)


@app.route("/delete_movement/<string:id>")
def delete_movement(id):
    try:
        with mysql.connection.cursor() as con:
            con.execute("DELETE FROM ProductMovement WHERE movement_id=%s", [id])
            mysql.connection.commit()
        flash("Movement deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting movement: {str(e)}", "error")
    return redirect(url_for("view_movements"))


@app.route("/product_movement_report")
def product_movement_report():
    try:
        with mysql.connection.cursor() as con:
            sql = """
                SELECT 
                    pm.movement_id, pm.timestamp, pm.from_location, pm.to_location, 
                    pm.product_id, pm.qty,
                    p.name AS product_name,
                    l1.city AS from_location_name,
                    l2.city AS to_location_name
                FROM ProductMovement pm
                JOIN Product p ON pm.product_id = p.product_id
                LEFT JOIN Location l1 ON pm.from_location = l1.location_id
                LEFT JOIN Location l2 ON pm.to_location = l2.location_id
                ORDER BY pm.timestamp DESC
            """
            con.execute(sql)
            movements = con.fetchall()
        return render_template("product_movement_report.html", movements=movements)
    except Exception as e:
        flash(f"Failed to load product movement report: {str(e)}", "error")
        return render_template("product_movement_report.html", movements=[])


@app.route("/download_product_movement_report")
def download_product_movement_report():
    try:
        with mysql.connection.cursor() as con:
            sql = """
                SELECT 
                    pm.movement_id, pm.timestamp, pm.from_location, pm.to_location, 
                    pm.product_id, pm.qty,
                    p.name AS product_name,
                    l1.city AS from_location_name,
                    l2.city AS to_location_name
                FROM ProductMovement pm
                JOIN Product p ON pm.product_id = p.product_id
                LEFT JOIN Location l1 ON pm.from_location = l1.location_id
                LEFT JOIN Location l2 ON pm.to_location = l2.location_id
                ORDER BY pm.timestamp DESC
            """
            con.execute(sql)
            movements = con.fetchall()

        report = BytesIO()
        report.write("Product Movement Report\n".encode('utf-8'))
        report.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n".encode('utf-8'))
        report.write("Movement ID | Product      | From Location  | To Location   | Qty | Timestamp\n".encode('utf-8'))
        report.write(("-" * 75 + "\n").encode('utf-8'))
        for movement in movements:
            from_loc = movement['from_location_name'] or 'None'
            to_loc = movement['to_location_name'] or 'None'
            line = f"{movement['movement_id']:<11} | {movement['product_name']:<12} | {from_loc:<14} | {to_loc:<13} | {movement['qty']:<3} | {movement['timestamp']}\n"
            report.write(line.encode('utf-8'))

        report.seek(0)
        return send_file(
            report,
            mimetype='text/plain',
            as_attachment=True,
            download_name="product_movement_report.txt"
        )
    except Exception as e:
        flash(f"Failed to generate report: {str(e)}", "error")
        return redirect(url_for("product_movement_report"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)