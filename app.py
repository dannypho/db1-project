from flask import Flask, request, jsonify, render_template
from mysql.connector import Error
import mysql.connector


app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'arlingtonorganicmarket database'
}


@app.route("/")
def index():
    return render_template("index.html", items=None, Scounts=None, zip=zip)

@app.route("/view-inventory")
def view_inventory():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM item")
    items = cursor.fetchall()

    cursor.execute("SELECT Scount FROM store_item")
    Scounts = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template("index.html", items=items, Scounts=Scounts, zip=zip)

@app.route("/add-vendor", methods=["POST"])
def add_vendor():
    vendor_name = request.form.get("vendorName")
    vendor_id = request.form.get("vendorID")
    vendor_street = request.form.get("vendorStreet")
    vendor_city = request.form.get("vendorCity")
    vendor_state_ab = request.form.get("vendorStateAb")
    vendor_zip_code = request.form.get("vendorZipCode")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO vendor (vId, Vname, Street, City, StateAb, ZipCode)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try: 
        cursor.execute(insert_query, (
            vendor_id,
            vendor_name,
            vendor_street,
            vendor_city,
            vendor_state_ab,
            vendor_zip_code
        ))
        conn.commit()
        message = "Vendor Added Successfully!"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=True, fail=False, zip=zip)
    except Error as err:
        message = f"Failed to add vendor: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)

@app.route("/add-item", methods=["POST"])
def add_item():
    item_vendor = request.form.get("itemVendor")
    item_name = request.form.get("itemName")
    item_id = request.form.get("itemID")
    item_price = request.form.get("itemPrice")
    item_category = request.form.get("itemCategory")
    item_amount= request.form.get("itemAmount")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_item_query = """
        INSERT INTO item (iId, Iname, Sprice, Category)
        VALUES (%s, %s, %s, %s)
    """
    select_vId_query = """SELECT vId FROM vendor WHERE Vname = %s"""
    insert_link_query = """
        INSERT INTO vendor_item (vId, iId)
        VALUES (%s, %s)
    """
    insert_stock_query = """
        INSERT INTO store_item (sId, iId, Scount)
        VALUES (%s, %s, %s)
    """

    try:
        cursor.execute(insert_item_query, (
            item_id,
            item_name,
            item_price,
            item_category,
        ))
        conn.commit()
    except Error as err:
            message = f"Failed to add item: {err}"
            cursor.close()
            conn.close()
            return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)

    try:
        cursor.execute(select_vId_query, ([item_vendor]))
        vId = cursor.fetchall()[0][0]
    except Error as err:
        message = f"Failed to select vId: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)

    try:
        cursor.execute(insert_link_query, (vId, item_id))
        conn.commit()
    except Error as err:
        message = f"Failed to link vendor to item: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)

    try:
        cursor.execute(insert_stock_query, (1, item_id, item_amount))
        conn.commit()
        cursor.close()
        conn.close()
        message = "Item added successfully!"
        return render_template("index.html", items=None, Scounts=None, message=message, success=True, fail=False, zip=zip)

    except Error as err:
        message = f"Failed to link item to store and add amount: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
    
@app.route("/update-item", methods=["POST"])
def update_item():
    updated_item_name = request.form.get("updatedItemName")
    updated_item_price = request.form.get("updatedItemPrice")

    update_query = """
        UPDATE item 
        SET Sprice = %s
        WHERE Iname = %s
    """
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute(update_query, (updated_item_price, updated_item_name))
        conn.commit()
        cursor.close()
        conn.close()
        message = "Item updated successfully!"
        return render_template("index.html", items=None, Scounts=None, message=message, success=True, fail=False, zip=zip)
    except Error as err:
        message = f"Failed to update item: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)

@app.route("/delete-item", methods=["POST"])
def delete_item():
    deleted_item_name = request.form.get("deletedItemName")

    select_iId_query = """
    SELECT iId
    FROM item
    WHERE Iname = %s
    """

    delete_from_store_query = """
    DELETE FROM store_item
    WHERE iId = %s
    """

    delete_from_vendor_query = """
    DELETE FROM vendor_item
    WHERE iId = %s
    """

    delete_from_item_query = """
    DELETE FROM item
    WHERE iId = %s
    """
    select_vId_query= """
    SELECT vId
    FROM vendor_item
    WHERE iId = %s
    """
    select_count_query = """
    SELECT COUNT(*) 
    FROM vendor_item 
    WHERE vId = %s;
    """
    delete_vendor_query = """
    DELETE FROM vendor
    WHERE vId = %s
    """

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Get iId
    try:
        cursor.execute(select_iId_query, ((deleted_item_name,)))
        iId = cursor.fetchall()[0][0]
    except Error as err:
        message = f"Failed to select iId: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)

    # Get vId
    try:
        cursor.execute(select_vId_query, ((iId,)))
        vId = cursor.fetchall()[0][0]
    except Error as err:
        message = f"Failed to select vId: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
    
    # Delete item from inventory
    try:
        cursor.execute(delete_from_store_query, ((iId,)))
        conn.commit()
    except Error as err:
        message = f"Failed to delete item from store: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
    
    # Delete vendor-item relationship
    try:
        cursor.execute(delete_from_vendor_query, ((iId,)))
        conn.commit()
    except Error as err:
        message = f"Failed to delete vendor-item relationship: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
    
    # Delete item from item table
    try:
        cursor.execute(delete_from_item_query, ((iId,)))
        conn.commit()
    except Error as err:
        message = f"Failed to delete item from item table: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
    
    # Check count of vId
    try:
        cursor.execute(select_count_query, ((vId,)))
        count = cursor.fetchall()[0][0]
    except:
        message = f"Failed to select count of vId: {err}"
        cursor.close()
        conn.close()
        return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
    
    # Delete vendor if count == 0
    if count == 0:
        try:
            cursor.execute(delete_vendor_query, ((vId,)))
            conn.commit()
            cursor.close()
            conn.close()
            message = "Item and Store deleted successfully!"
            return render_template("index.html", items=None, Scounts=None, message=message, success=True, fail=False, zip=zip)
        except Error as err:
            message = f"Failed to delete vendor: {err}"
            cursor.close()
            conn.close()
            return render_template("index.html", items=None, Scounts=None, message=message, success=False, fail=True, zip=zip)
        
    cursor.close()
    conn.close()
    message = "Item deleted successfully!"
    return render_template("index.html", items=None, Scounts=None, message=message, success=True, fail=False, zip=zip)

@app.route("/view-statistics")
def view_statistics():
    select_top_3_items_query = """
    SELECT Iname, TotalRevenue
    FROM ItemSalesSummary
    ORDER BY TotalRevenue DESC
    LIMIT 3;
    """
    select_50_units_query = """
    SELECT Iname, TotalQuantitySold
    FROM ItemSalesSummary
    WHERE TotalQuantitySold > 50;
    """
    select_total_revenue_query = """
    SELECT SUM(TotalRevenue) AS OverallRevenue
    FROM ItemSalesSummary;
    """

    select_best_customer_query = """
    SELECT Cname, LoyaltyScore
    FROM TopLoyalCustomers
    ORDER BY LoyaltyScore DESC
    LIMIT 1;
    """

    select_top_customers_query = """
    SELECT Cname, LoyaltyScore
    FROM TopLoyalCustomers
    WHERE LoyaltyScore BETWEEN 4 AND 5;
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute(select_top_3_items_query)
    top_3_items = cursor.fetchall()

    cursor.execute(select_50_units_query)
    top_units = cursor.fetchall()

    cursor.execute(select_total_revenue_query)
    total_revenue = cursor.fetchall()

    cursor.execute(select_best_customer_query)
    top_customer = cursor.fetchall()

    cursor.execute(select_top_customers_query)
    top_customers = cursor.fetchall()

    # print(top_units)
    # print(total_revenue)
    # print(top_customer)
    # print(top_customers)



    return render_template("statistics.html", top_items = top_3_items, top_units = top_units, top_customer=top_customer, top_customers=top_customers, total_revenue=total_revenue)

if __name__ == "__main__":
    app.run(debug=True)


