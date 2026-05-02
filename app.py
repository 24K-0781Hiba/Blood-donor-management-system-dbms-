import oracledb
oracledb.init_oracle_client(lib_dir=r"C:\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_0")

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ========== ORACLE DATABASE CONNECTION ==========
def get_db_connection():
    return oracledb.connect(
        user="blood_bank",
        password="password123",
        host="localhost",
        port=1521,
        service_name="XE"
    )

# ========== API ROUTES ==========

@app.route('/')
def home():
    return render_template('index.html')

# Get all donors
@app.route('/api/donors')
def get_donors():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT u.USERID, u.NAME, u.EMAIL, u.PHONE, d.BLOODGROUP, d.GENDER, d.ISELIGIBLE
        FROM Users u
        JOIN Donor d ON u.USERID = d.DONORID
    """)
    
    donors = []
    for row in cursor.fetchall():
        donors.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'bloodGroup': row[4],
            'gender': row[5],
            'eligible': row[6]
        })
    
    cursor.close()
    conn.close()
    return jsonify(donors)

# Get blood inventory
@app.route('/api/inventory')
def get_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT BLOODID, BLOODGROUP, QUANTITYML, EXPIRYDATE, STATUS, ISSAFE FROM blood_inventory")
    
    inventory = []
    for row in cursor.fetchall():
        inventory.append({
            'id': row[0],
            'bloodGroup': row[1],
            'quantity': row[2],
            'expiryDate': str(row[3]) if row[3] else 'N/A',
            'status': row[4],
            'isSafe': row[5]
        })
    
    cursor.close()
    conn.close()
    return jsonify(inventory)

# Get all blood requests
@app.route('/api/requests')
def get_all_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT br.REQUESTID, br.BLOODGROUP, br.QUANTITYML, br.URGENCY, 
               br.REQUESTDATE, br.STATUS, u.NAME
        FROM BloodRequest br
        JOIN Hospital h ON br.HOSPITALID = h.HOSPITALID
        JOIN Users u ON h.HOSPITALID = u.USERID
        ORDER BY br.REQUESTDATE DESC
    """)
    
    requests = []
    for row in cursor.fetchall():
        requests.append({
            'id': row[0],
            'bloodGroup': row[1],
            'quantity': row[2],
            'urgency': row[3],
            'date': str(row[4]) if row[4] else 'N/A',
            'status': row[5],
            'hospital': row[6]
        })
    
    cursor.close()
    conn.close()
    return jsonify(requests)

# Gett pending requests
@app.route('/api/requests/pending')
def get_pending_requests():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT br.REQUESTID, br.BLOODGROUP, br.QUANTITYML, br.URGENCY, 
               br.REQUESTDATE, br.STATUS, u.NAME
        FROM BloodRequest br
        JOIN Hospital h ON br.HOSPITALID = h.HOSPITALID
        JOIN Users u ON h.HOSPITALID = u.USERID
        WHERE br.STATUS = 'Pending'
    """)
    
    requests = []
    for row in cursor.fetchall():
        requests.append({
            'id': row[0],
            'bloodGroup': row[1],
            'quantity': row[2],
            'urgency': row[3],
            'date': str(row[4]) if row[4] else 'N/A',
            'status': row[5],
            'hospital': row[6]
        })
    
    cursor.close()
    conn.close()
    return jsonify(requests)

#Get donation camps
@app.route('/api/camps')
def get_camps():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.CAMPID, c.CAMPNAME, c.LOCATION, c.STARTDATE, c.ENDDATE, u.NAME
        FROM donationCamp c
        JOIN Users u ON c.ORGANIZERID = u.USERID
    """)
    
    camps = []
    for row in cursor.fetchall():
        camps.append({
            'id': row[0],
            'name': row[1],
            'location': row[2],
            'startDate': str(row[3]) if row[3] else 'N/A',
            'endDate': str(row[4]) if row[4] else 'N/A',
            'organizer': row[5]
        })
    
    cursor.close()
    conn.close()
    return jsonify(camps)

# Register new donor
@app.route('/api/register_donor', methods=['POST'])
def register_donor():
    conn = None
    cursor = None
    try:
        data = request.json
        print("Received donor data:", data)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if email already exists
        cursor.execute("SELECT COUNT(*) FROM Users WHERE EMAIL = :1", (data['email'],))
        email_count = cursor.fetchone()[0]
        
        if email_count > 0:
            return jsonify({
                'success': False, 
                'error': 'Email already registered. Please use a different email.'
            })
        
        #got next userID from sequence
        cursor.execute("SELECT user_seq.NEXTVAL FROM DUAL")
        user_id = cursor.fetchone()[0]
        print(f"Generated user_id: {user_id}")
        
        #insert into users first, then donorr
        cursor.execute("""
            INSERT INTO Users (USERID, NAME, EMAIL, PASSWORDHASH, PHONE, ADDRESS, USERTYPE, REGISTRATIONDATE)
            VALUES (:1, :2, :3, :4, :5, :6, 'Donor', SYSDATE)
        """, (user_id, data['name'], data['email'], data['password'], data['phone'], data.get('address', '')))
        print("Inserted into Users")
        
        cursor.execute("""
            INSERT INTO Donor (donorID, bloodGroup, gender, weight, isEligible)
            VALUES (:1, :2, :3, :4, 1)
        """, (user_id, data['bloodGroup'], data['gender'], data['weight']))
        print("Inserted into Donor")
        
        conn.commit()
        print(f"Successfully registered donor with ID: {user_id}")
        
        return jsonify({
            'success': True, 
            'message': 'Donor registered successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        print("ERROR:", str(e))
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Create new blood request
@app.route('/api/create_request', methods=['POST'])
def create_request():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT req_seq.NEXTVAL FROM DUAL")
        request_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO BloodRequest (REQUESTID, HOSPITALID, BLOODGROUP, QUANTITYML, URGENCY, STATUS, REQUESTDATE)
            VALUES (:1, :2, :3, :4, :5, 'Pending', SYSDATE)
        """, (request_id, data['hospitalID'], data['bloodGroup'], data['quantity'], data['urgency']))
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Blood request submitted"})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": str(e)})

#fulfill a blood request
@app.route('/api/fulfill_request/<int:request_id>', methods=['PUT'])
def fulfill_request(request_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE BloodRequest SET STATUS = 'Fulfilled' WHERE REQUESTID = :1", (request_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Request fulfilled"})
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": str(e)})

# Get hospitals for dropdown
@app.route('/api/hospitals')
def get_hospitals():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT h.HOSPITALID, u.NAME
        FROM Hospital h
        JOIN Users u ON h.HOSPITALID = u.USERID
    """)
    
    hospitals = []
    for row in cursor.fetchall():
        hospitals.append({'id': row[0], 'name': row[1]})
    
    cursor.close()
    conn.close()
    return jsonify(hospitals)

#get dashboard stats
@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Donor")
    total_donors = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(QUANTITYML)/450 FROM blood_inventory WHERE STATUS = 'Available' AND ISSAFE = 1")
    result = cursor.fetchone()[0]
    total_blood = int(result) if result else 0
    
    cursor.execute("SELECT COUNT(*) FROM BloodRequest WHERE STATUS = 'Pending'")
    pending_requests = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM donationCamp WHERE STARTDATE >= SYSDATE")
    upcoming_camps = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_donors': total_donors,
        'total_blood': total_blood,
        'pending_requests': pending_requests,
        'upcoming_camps': upcoming_camps
    })

if __name__ == '__main__':
    app.run(debug=True)