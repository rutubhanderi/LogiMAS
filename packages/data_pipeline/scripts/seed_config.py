"""
Configuration file for database seeding
Adjust these numbers based on your needs
"""

# ========================================
# SEEDING CONFIGURATION
# ========================================

# Customer profiles (users who place orders)
NUM_CUSTOMERS = 100

# Orders (can be much higher than customers - customers place multiple orders)
NUM_ORDERS = 5000  # Each customer will have ~50 orders on average

# Warehouses and Vehicles (infrastructure)
NUM_WAREHOUSES = 10
NUM_VEHICLES = 50

# Date range for historical data
DAYS_OF_HISTORY = 180  # 6 months of historical data

# Order status distribution (must sum to 1.0)
ORDER_STATUS_WEIGHTS = {
    'delivered': 0.70,   # 70% delivered
    'shipped': 0.20,     # 20% currently shipping
    'processing': 0.10   # 10% still processing
}

# Product catalog size
NUM_PRODUCTS = 200

# Items per order range
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 8

# Price range for products
MIN_PRODUCT_PRICE = 10.0
MAX_PRODUCT_PRICE = 500.0

# Loyalty tier distribution
LOYALTY_TIERS = ['Bronze', 'Silver', 'Gold', 'Platinum']
LOYALTY_WEIGHTS = [0.5, 0.3, 0.15, 0.05]  # Most are Bronze, few are Platinum

# Shipment parameters
MIN_DISTANCE_KM = 5
MAX_DISTANCE_KM = 1000
AVG_SPEED_KMH = 60  # Average delivery speed

# Vehicle telemetry (optional - can be very large)
GENERATE_TELEMETRY = True
TELEMETRY_POINTS_PER_SHIPMENT = 10  # GPS points per shipment

# Batch size for database inserts
BATCH_SIZE = 500

# ========================================
# CALCULATED VALUES
# ========================================

TOTAL_SHIPMENTS = int(NUM_ORDERS * (ORDER_STATUS_WEIGHTS['delivered'] + ORDER_STATUS_WEIGHTS['shipped']))
TOTAL_TELEMETRY_POINTS = TOTAL_SHIPMENTS * TELEMETRY_POINTS_PER_SHIPMENT if GENERATE_TELEMETRY else 0

# ========================================
# SUMMARY
# ========================================

def print_config_summary():
    """Print a summary of what will be generated"""
    print("\n" + "="*60)
    print("DATABASE SEEDING CONFIGURATION")
    print("="*60)
    print(f"Customers:           {NUM_CUSTOMERS:,}")
    print(f"Orders:              {NUM_ORDERS:,}")
    print(f"Shipments:           ~{TOTAL_SHIPMENTS:,}")
    print(f"Warehouses:          {NUM_WAREHOUSES}")
    print(f"Vehicles:            {NUM_VEHICLES}")
    print(f"Products:            {NUM_PRODUCTS}")
    print(f"Telemetry Points:    {TOTAL_TELEMETRY_POINTS:,}" if GENERATE_TELEMETRY else "Telemetry:           Disabled")
    print(f"Date Range:          Last {DAYS_OF_HISTORY} days")
    print("="*60)
    print(f"\nEstimated database size: ~{estimate_size_mb():.1f} MB")
    print("="*60 + "\n")

def estimate_size_mb():
    """Rough estimate of database size"""
    customer_size = NUM_CUSTOMERS * 0.001  # ~1KB per customer
    order_size = NUM_ORDERS * 0.002  # ~2KB per order
    shipment_size = TOTAL_SHIPMENTS * 0.001  # ~1KB per shipment
    telemetry_size = TOTAL_TELEMETRY_POINTS * 0.0005 if GENERATE_TELEMETRY else 0  # ~0.5KB per point
    
    return customer_size + order_size + shipment_size + telemetry_size

if __name__ == "__main__":
    print_config_summary()
