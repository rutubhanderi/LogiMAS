"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Define the shape of the data the chart expects
interface ChartData {
  ship_date: string;
  on_time_percentage: number;
}

interface DailyPerformanceChartProps {
  data: ChartData[];
}

export function DailyPerformanceChart({ data }: DailyPerformanceChartProps) {
  // Format the data for the chart. Recharts works best with simple keys.
  const formattedData = data
    .map((item) => ({
      // Format the date to be more readable on the X-axis
      date: new Date(item.ship_date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      "On-Time %": item.on_time_percentage,
    }))
    .reverse(); // Reverse to show oldest to newest

  return (
    // ResponsiveContainer makes the chart fill its parent container
    <ResponsiveContainer width="100%" height={400}>
      <BarChart
        data={formattedData}
        margin={{
          top: 5,
          right: 30,
          left: 20,
          bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
        <XAxis dataKey="date" stroke="#6b7280" />
        <YAxis unit="%" stroke="#6b7280" />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937", // Dark background for tooltip
            borderColor: "#374151",
            color: "#ffffff",
          }}
        />
        <Legend />
        <Bar dataKey="On-Time %" fill="#4f46e5" />
      </BarChart>
    </ResponsiveContainer>
  );
}
