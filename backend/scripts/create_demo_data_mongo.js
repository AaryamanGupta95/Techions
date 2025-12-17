// MongoDB script to create demo data directly in MongoDB
// Run this in MongoDB Compass or mongosh
// Usage: In MongoDB Compass, click "Open MongoDB shell" and paste this script

// Switch to the database (will be created automatically)
use automotive_aftermarket;

// Create users collection with demo users
db.users.insertMany([
  {
    username: "customer",
    email: "customer@demo.com",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5H5qN4xqO", // password123
    role: "customer",
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    username: "service_center",
    email: "service@demo.com",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5H5qN4xqO", // password123
    role: "service_center",
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    username: "manufacturing",
    email: "manufacturing@demo.com",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5H5qN4xqO", // password123
    role: "manufacturing",
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    username: "admin",
    email: "admin@demo.com",
    hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5H5qN4xqO", // password123
    role: "admin",
    is_active: true,
    created_at: new Date(),
    updated_at: new Date()
  }
]);

// Create demo customer
db.customers.insertOne({
  customer_id: "CUST_001",
  name: "John Doe",
  email: "john.doe@example.com",
  phone: "+1234567890",
  address: "123 Main St, City, State",
  vehicles: ["DEMO_VIN_001"],
  created_at: new Date(),
  updated_at: new Date()
});

// Create demo vehicle
db.vehicles.insertOne({
  vin: "DEMO_VIN_001",
  model: "Hero Splendor",
  manufacturer: "Hero",
  year: 2023,
  customer_id: "CUST_001",
  registration_date: new Date(),
  status: "active",
  created_at: new Date()
});

// Create demo service center
db.service_centers.insertOne({
  center_id: "SC_001",
  name: "Hero Service Center Downtown",
  address: "456 Service Ave, City, State",
  phone: "+1234567891",
  email: "service@hero.com",
  capacity: 10,
  current_load: 0,
  status: "active",
  operating_hours: {
    monday: { open: "09:00", close: "18:00" },
    tuesday: { open: "09:00", close: "18:00" },
    wednesday: { open: "09:00", close: "18:00" },
    thursday: { open: "09:00", close: "18:00" },
    friday: { open: "09:00", close: "18:00" },
    saturday: { open: "09:00", close: "14:00" },
    sunday: { open: "closed", close: "closed" }
  },
  created_at: new Date()
});

// Create demo technician
db.technicians.insertOne({
  technician_id: "TECH_001",
  name: "Mike Johnson",
  service_center_id: "SC_001",
  specialization: ["Engine", "Electrical"],
  current_assignments: 0,
  max_capacity: 3,
  status: "available",
  created_at: new Date()
});

print("✓ Demo data created successfully!");
print("You can now login with:");
print("  - customer / password123");
print("  - service_center / password123");
print("  - manufacturing / password123");
print("  - admin / password123");

