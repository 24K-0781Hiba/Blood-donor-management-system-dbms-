# BLOOD DONOR MANAGEMENT

# SYSTEM

### Sehla Razzak(24k-0575), Hiba Faiq(24k-0781), Tania(24k-0713)

## OVERVIEW

### 1. Introduction

The **Blood Donor Management System** is a comprehensive database-driven web application designed
to streamline the operations of a blood bank. The system facilitates the management of donors, blood
inventory, hospital requests, donation camps, and system logs. It aims to bridge the gap between blood
donors and recipients by providing an efficient, real-time platform for tracking blood stock and processing
requests, ultimately helping save lives by ensuring timely blood availability.

### 2. Objectives

- To create a centralized database for managing donor information, blood inventory, and hospital
    requests.
- To provide an intuitive web-based interface for administrators and hospital staff.
- To automate the tracking of blood stock, including expiry dates and safety status.
- To enable hospitals to create blood requests and administrators to fulfill them efficiently.
- To provide real-time statistics and reports for operational decision-making.

### 3. Technologies Used

- **Backend:**  Python with Flask framework
- **Database:**   Oracle Database (using oracle dB connector)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS for dynamic UI)
- **Database Features:**  Tables, Sequences, Triggers, Foreign Keys, Check Constraints, Joins

### 4. Database Schema

(^) The database consists of the following main tables organized into categories:

### 4.1 Users & Roles (User-based Inheritance)
Users - Parent table storing common fields: userID, name, email, passwordHash, phone, address, userType, registrationDate; 
Donor - Inherits from Users; adds bloodGroup, dateOfBirth, gender, weight, medicalHistory, isEligible; 
Hospital - Inherits from Users; adds licenseNo, hospitalType, emergencyContact; 
Employee - Inherits from Users; adds jobTitle, department, hireDate; 
Admin - Inherits from Users; adds securityLevel; 
LabTech - Inherits from Users; adds certificationNo; 
`
### 4.2 Inventory & Donation Camps
blood_inventory - Stores blood units with bloodGroup, quantityML, expiryDate, status, isSafe;
donationCamp - Manages donation camp details including campName, location, startDate, endDate, organizerID;
`

### 4.3 Records, Appointments & Requests
DonationRecord - Logs each donation with donor info, blood group, quantity, test results, and approval status;
Appointment - Schedules donor appointments at camps;
BloodRequest - Tracks hospital requests for blood with urgency and status (Pending, Approved, Fulfilled, Rejected);
`
### 4.4 Support Systems
Notification - Stores user notifications (SMS, Email, InApp); 
System_log - Logs admin actions (login, user creation, request approval, inventory updates); 
Blood_report - Stores generated administrative reports; 
``

### 4.5 Sequences & Triggers

`
Auto-increment triggers are implemented for all primary keys using sequences (e.g., user_seq, inv_seq,
req_seq, don_rec_seq, etc
`
### VISUALIZATION OF ENTITY RELATIONSHIP DIAGRAM

### 5. System Features and Functionality

### 5.1 Dashboard

- Displays key metrics:
    o Total Donors
    o Total Blood Bags Available (calculated as total ml / 450)
    o Pending Blood Requests
    o Upcoming Donation Camps

### 5.2 Donor Management

- View list of all registered donors with details (name, email, phone, blood group, gender, eligibility)
- Register new donors through a web form
- Automatic generation of userID via sequence


### 5.3 Blood Inventory Management

- View blood stock with details:
    o Blood group, quantity, expiry date, status, safety flag
- Color-coded status indicators:
    o Green: Available
    o Yellow: Quarantined
    o Red: Expired

### 5.4 Blood Request Management

- Hospitals can submit new blood requests (blood group, quantity, urgency)
- View all requests with hospital name, urgency, date, and status
- Fulfill pending requests with one click (updates status to "Fulfilled")

### 5.5 Donation Camp Management

- View upcoming and past donation camps with location, dates, and organizer information

### 6. API Endpoints (Backend)


### 7. User Interface Preview

```
The frontend is a responsive single-page application with:
```
- **Navigation Bar:** Buttons to switch between Dashboard, Donors, Blood Stock, Requests, Donation
    Camps, Register Donor, and New Request.
- **Dashboard Cards:** Four statistic cards with real-time data.
- **Data Tables:** Sortable, hover-enabled tables with color-coded status badges.
- **Forms:** Clean, validated forms for donor registration and blood requests.
- **Action Buttons:** "Fulfill" buttons on pending requests for quick processing.

### 8. Testing and Validation

```
The system has been tested with:
```
- ✅ Sample data insertion (10 users, 5 donors, 10 inventory items, 5 requests, 5 camp records, 5
    system logs)
- ✅ Donor registration flow (sequential ID generation)
- ✅ Blood request creation and status update
- ✅ Inventory view with expiry and safety status
- ✅ All joins between Users and role-specific tables (Donor, Hospital)

### 9. Challenges And Solutions

Managing inherited user types → Implemented a parent Users table with foreign keys from role-specific tables
Ensuring unique email addresses → Added UNIQUE constraint on email in Users table
Handling sequential IDs across sessions → Used Oracle sequences with BEFORE INSERT triggers
Connecting Oracle with Python Flask → Used oracledb library with Instant Client
Calculating total blood bags → Used SQL SUM(quantityML)/450 to convert ml to standard bags

## 10. Conclusion

The **Blood Donor Management System** successfully demonstrates a fully functional database-driven web
application for blood bank management. It effectively handles donor registration, inventory tracking, and hospital
request processing. The system is scalable, maintainable, and provides a user-friendly interface for administrators
and hospital staff. The use of Oracle databases with proper normalization, constraints, and triggers ensures data
integrity, while the Flask backend provides a robust API layer. This project serves as a solid foundation for a real-
world blood bank management solution that can potentially help save lives by optimizing blood donation and
distribution processes.
