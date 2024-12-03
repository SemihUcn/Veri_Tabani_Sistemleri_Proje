from flask import Flask, jsonify, render_template, request
import pymysql
import time
app = Flask(__name__)

# Veritabanı bağlantısı fonksiyonu
def connect_to_db():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="your_app_db",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def index():
    return render_template("index.html")

# Şehirlerin listesi
@app.route("/cities")
def cities():
    connection = connect_to_db()
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT Location FROM Mall")
            rows = cursor.fetchall()
            end_time = time.time()
            query_time = end_time - start_time
            return jsonify([row["Location"] for row in rows])
    finally:
        connection.close()

# Seçili şehirdeki AVM'lerin listesi
@app.route("/malls")
def malls():
    city = request.args.get("city")
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MallID, Name FROM Mall WHERE Location = %s", (city,))
            rows = cursor.fetchall()
            return jsonify(rows)
    finally:
        connection.close()

# Etkinlik bilgileri için rota
@app.route("/mall_details/events/<int:mall_id>")
def mall_events(mall_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # Etkinlikleri getir
            cursor.execute("SELECT * FROM Events WHERE MallID = %s", (mall_id,))
            events = cursor.fetchall()
            return render_template("events.html", events=events, mall_id=mall_id)
    finally:
        connection.close()

# Mağaza bilgileri ve promosyonları için rota
@app.route("/mall_details/stores/<int:mall_id>")
def mall_stores(mall_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # Mağazaları getir
            cursor.execute("SELECT * FROM Stores WHERE MallID = %s", (mall_id,))
            stores = cursor.fetchall()
            
            # Her mağaza için müşteri sayısını hesapla
            for store in stores:
                cursor.execute("""
                    SELECT COUNT(DISTINCT CustomerID) as CustomerCount
                    FROM Visits
                    WHERE StoreID = %s
                """, (store["StoreID"],))
                customer_count = cursor.fetchone()["CustomerCount"]
                store["CustomerCount"] = customer_count
            
                # Promosyonları getir
                cursor.execute("SELECT * FROM Promotions WHERE StoreID = %s", (store["StoreID"],))
                promotions = cursor.fetchall()
                store["promotions"] = promotions
                # AVM'deki toplam müşteri sayısını hesapla
            cursor.execute("""
                SELECT COUNT(DISTINCT CustomerID) as TotalCustomers
                FROM Visits
                WHERE StoreID IN (SELECT StoreID FROM Stores WHERE MallID = %s)
            """, (mall_id,))
            total_customers = cursor.fetchone()["TotalCustomers"]
            return render_template("stores.html", stores=stores, mall_id=mall_id ,total_customers=total_customers)
    finally:
        connection.close()

# Otopark bilgileri için rota
@app.route("/mall_details/parkings/<int:mall_id>")
def mall_parkings(mall_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # Otopark bilgilerini getir
            cursor.execute("SELECT * FROM ParkingSpots WHERE MallID = %s", (mall_id,))
            parking_spots = cursor.fetchall()
            
            total_spots = len(parking_spots)
            occupied_spots = sum(1 for spot in parking_spots if spot['AvailabilityStatus'] == 0)
            # Doluluk oranını hesapla
            occupancy_rate = (occupied_spots / total_spots) * 100 if total_spots > 0 else 0
            return render_template("parking.html", parking_spots=parking_spots, mall_id=mall_id,occupancy_rate= occupancy_rate)
    finally:
        connection.close()

# Kayıp eşyalar için rota
@app.route("/mall_details/lost_items/<int:mall_id>")
def mall_lost_items(mall_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # Kayıp eşyaları getir
            cursor.execute("""
                SELECT 
                    ItemID, Description, DateFound, LocationFound, ClaimedStatus, ClaimedBy 
                FROM LostAndFound 
                WHERE MallID = %s
            """, (mall_id,))
            lost_items = cursor.fetchall()
            return render_template("lost_items.html", lost_items=lost_items, mall_id=mall_id)
    finally:
        connection.close()


# AVM detaylarını JSON olarak döndüren rota
@app.route("/mall_details")
def mall_details():
    mall_id = request.args.get("mall_id")
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # AVM bilgilerini al
            cursor.execute("SELECT * FROM Mall WHERE MallID = %s", (mall_id,))
            mall_info = cursor.fetchone()

            # İlgili etkinlikleri al
            cursor.execute("SELECT * FROM Events WHERE MallID = %s", (mall_id,))
            events = cursor.fetchall()

            # İlgili mağazaları al
            cursor.execute("SELECT * FROM Stores WHERE MallID = %s", (mall_id,))
            stores = cursor.fetchall()

            # Otopark bilgilerini al
            cursor.execute("SELECT * FROM ParkingSpots WHERE MallID = %s", (mall_id,))
            parking_spots = cursor.fetchall()

            # Kayıp eşyaları al
            cursor.execute("SELECT * FROM LostItems WHERE MallID = %s", (mall_id,))
            lost_items = cursor.fetchall()

            return jsonify({
                "mall_info": mall_info,
                "events": events,
                "stores": stores,
                "parking_spots": parking_spots,
                "lost_items": lost_items
            })
    finally:
        connection.close()

# Belirli bir etkinliğin detaylarını döndüren rota
@app.route("/event_details")
def event_details():
    event_id = request.args.get("event_id")
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # Etkinlik detaylarını çek
            cursor.execute("SELECT * FROM Events WHERE EventID = %s", (event_id,))
            event_data = cursor.fetchone()
            return jsonify(event_data)
    finally:
        connection.close()
        
@app.route("/mall_details/stores/search/<int:mall_id>")
def search_store(mall_id):
    query = request.args.get("query", "").lower()
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM Stores 
                WHERE MallID = %s AND LOWER(Name) LIKE %s
                """,
                (mall_id, f"%{query}%"),
            )
            stores = cursor.fetchall()
            

            return jsonify(stores)
    finally:
        connection.close()




        
@app.route("/store_details/<int:store_id>")
def store_details(store_id):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # Mağaza detaylarını al
            cursor.execute("SELECT * FROM Stores WHERE StoreID = %s", (store_id,))
            store = cursor.fetchone()
            
            # Mağazanın promosyonlarını al
            cursor.execute("SELECT * FROM Promotions WHERE StoreID = %s", (store_id,))
            promotions = cursor.fetchall()
            store["promotions"] = promotions
            
            # Mağazanın yorumlarını al
            cursor.execute("SELECT * FROM Customer_Review WHERE StoreID = %s", (store_id,))
            reviews = cursor.fetchall()
            store["reviews"] = reviews

            return render_template("reviews.html", store=store, reviews=reviews)
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
