-- Create materialized view for daily on-time performance KPIs
-- This view calculates daily shipment statistics

CREATE MATERIALIZED VIEW IF NOT EXISTS daily_on_time_rate AS
SELECT 
    DATE(shipped_at) as ship_date,
    COUNT(*) as total_shipments,
    COUNT(*) FILTER (WHERE status = 'delivered' AND 
        EXTRACT(EPOCH FROM (
            COALESCE(
                (SELECT actual_delivery_date FROM orders WHERE orders.order_id = shipments.order_id),
                NOW()
            ) - expected_arrival
        )) <= 0
    ) as on_time_shipments,
    ROUND(
        (COUNT(*) FILTER (WHERE status = 'delivered' AND 
            EXTRACT(EPOCH FROM (
                COALESCE(
                    (SELECT actual_delivery_date FROM orders WHERE orders.order_id = shipments.order_id),
                    NOW()
                ) - expected_arrival
            )) <= 0
        )::numeric / NULLIF(COUNT(*), 0) * 100), 2
    ) as on_time_percentage
FROM shipments
WHERE shipped_at IS NOT NULL
GROUP BY DATE(shipped_at)
ORDER BY ship_date DESC;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_daily_on_time_rate_ship_date 
ON daily_on_time_rate(ship_date DESC);

-- Refresh the view with current data
REFRESH MATERIALIZED VIEW daily_on_time_rate;

-- Verify the view was created
SELECT 'Materialized view created successfully!' as status;
SELECT COUNT(*) as total_days FROM daily_on_time_rate;
SELECT * FROM daily_on_time_rate LIMIT 5;
