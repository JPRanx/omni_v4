/**
 * Dashboard V4 Data
 *
 * Generated from V4 batch processing results
 * Date Range: 2025-08-20 to 2025-08-31
 * Generated: 2025-11-12 08:09 AM
 *
 * ✅ ACCURATE V4 DATA
 * - Labor costs from actual PayrollExport CSV
 * - No inflation or multipliers
 * - Verified against source data
 */

export const v4Data = {
  week1: {
  "overview": {
    "totalSales": 188611.26,
    "avgDailySales": 15718.0,
    "totalLabor": 46706.98000000001,
    "laborPercent": 24.8,
    "totalCogs": 0,
    "cogsPercent": 0.0,
    "netProfit": 141904.28,
    "profitMargin": 75.2,
    "overtimeHours": 0,
    "totalCash": 26278.79,
    "cashFlow": {
      "total_cash": 26278.79,
      "total_tips": -199.01,
      "total_vendor_payouts": 0,
      "net_cash": 26477.800000000003,
      "vendor_payouts": [],
      "restaurants": {
        "SDR": {
          "total_cash": 2077.94,
          "total_tips": -66.0,
          "total_vendor_payouts": 0,
          "net_cash": 2143.94,
          "shifts": {
            "Morning": {
              "cash": 1246.76,
              "tips": -39.6,
              "payouts": 0,
              "net": 1286.36,
              "drawers": []
            },
            "Evening": {
              "cash": 831.18,
              "tips": -26.4,
              "payouts": 0,
              "net": 857.58,
              "drawers": []
            }
          }
        },
        "T12": {
          "total_cash": 11574.2,
          "total_tips": -133.01,
          "total_vendor_payouts": 0,
          "net_cash": 11707.210000000001,
          "shifts": {
            "Morning": {
              "cash": 6944.52,
              "tips": -79.81,
              "payouts": 0,
              "net": 7024.33,
              "drawers": []
            },
            "Evening": {
              "cash": 4629.68,
              "tips": -53.2,
              "payouts": 0,
              "net": 4682.88,
              "drawers": []
            }
          }
        },
        "TK9": {
          "total_cash": 12626.650000000001,
          "total_tips": 0.0,
          "total_vendor_payouts": 0,
          "net_cash": 12626.650000000001,
          "shifts": {
            "Morning": {
              "cash": 7575.99,
              "tips": 0.0,
              "payouts": 0,
              "net": 7575.99,
              "drawers": []
            },
            "Evening": {
              "cash": 5050.66,
              "tips": 0.0,
              "payouts": 0,
              "net": 5050.66,
              "drawers": []
            }
          }
        }
      }
    },
    "patterns": null
  },
  "metrics": [
    {
      "id": "total-sales",
      "label": "Total Sales",
      "value": 188611.26,
      "type": "currency",
      "color": "blue",
      "icon": "\ud83d\udcb0",
      "status": "excellent"
    },
    {
      "id": "avg-daily",
      "label": "Avg Daily Sales",
      "value": 15718.0,
      "type": "currency",
      "color": "green",
      "icon": "\ud83d\udcca",
      "status": "excellent"
    },
    {
      "id": "labor-cost",
      "label": "Labor Cost",
      "value": 46706.98000000001,
      "type": "currency",
      "color": "yellow",
      "icon": "\ud83d\udc65",
      "status": "excellent"
    },
    {
      "id": "labor-percent",
      "label": "Labor %",
      "value": 24.8,
      "type": "percentage",
      "color": "green",
      "icon": "\ud83d\udcc8",
      "status": "excellent"
    },
    {
      "id": "net-profit",
      "label": "Net Profit",
      "value": 141904.28,
      "type": "currency",
      "color": "green",
      "icon": "\ud83d\udcb5",
      "status": "excellent"
    },
    {
      "id": "profit-margin",
      "label": "Profit Margin",
      "value": 75.2,
      "type": "percentage",
      "color": "green",
      "icon": "\ud83d\udcc8",
      "status": "excellent"
    }
  ],
  "restaurants": [
    {
      "id": "rest-sdr",
      "name": "Sandra's Mexican Cuisine",
      "code": "SDR",
      "sales": 61036.39000000001,
      "laborCost": 16229.410000000002,
      "laborPercent": 26.6,
      "cogs": 0,
      "cogsPercent": 0.0,
      "netProfit": 44806.98,
      "profitMargin": 73.4,
      "status": "good",
      "grade": "C+",
      "dailyBreakdown": [
        {
          "day": "Wednesday",
          "date": "2025-08-20",
          "sales": 3903.31,
          "laborCost": 1436.2599999999998,
          "cogs": 0
        },
        {
          "day": "Thursday",
          "date": "2025-08-21",
          "sales": 4303.81,
          "laborCost": 1208.8200000000002,
          "cogs": 0
        },
        {
          "day": "Friday",
          "date": "2025-08-22",
          "sales": 5893.16,
          "laborCost": 1285.3600000000001,
          "cogs": 0
        },
        {
          "day": "Saturday",
          "date": "2025-08-23",
          "sales": 7593.4,
          "laborCost": 1749.73,
          "cogs": 0
        },
        {
          "day": "Sunday",
          "date": "2025-08-24",
          "sales": 5779.7,
          "laborCost": 1619.98,
          "cogs": 0
        },
        {
          "day": "Monday",
          "date": "2025-08-25",
          "sales": 2340.95,
          "laborCost": 964.19,
          "cogs": 0
        },
        {
          "day": "Tuesday",
          "date": "2025-08-26",
          "sales": 3192.07,
          "laborCost": 938.58,
          "cogs": 0
        },
        {
          "day": "Wednesday",
          "date": "2025-08-27",
          "sales": 3345.55,
          "laborCost": 999.66,
          "cogs": 0
        },
        {
          "day": "Thursday",
          "date": "2025-08-28",
          "sales": 4379.94,
          "laborCost": 1269.4,
          "cogs": 0
        },
        {
          "day": "Friday",
          "date": "2025-08-29",
          "sales": 6091.76,
          "laborCost": 1262.54,
          "cogs": 0
        },
        {
          "day": "Saturday",
          "date": "2025-08-30",
          "sales": 7656.75,
          "laborCost": 1912.28,
          "cogs": 0
        },
        {
          "day": "Sunday",
          "date": "2025-08-31",
          "sales": 6555.99,
          "laborCost": 1582.6100000000001,
          "cogs": 0
        }
      ],
      "cashFlow": {
        "total_cash": 2077.94,
        "total_tips": -66.0,
        "total_vendor_payouts": 0,
        "net_cash": 2143.94,
        "vendor_payouts": [],
        "shifts": {
          "Morning": {
            "cash": 1246.76,
            "tips": -39.6,
            "payouts": 0,
            "net": 1286.36,
            "drawers": []
          },
          "Evening": {
            "cash": 831.18,
            "tips": -26.4,
            "payouts": 0,
            "net": 857.58,
            "drawers": []
          }
        }
      }
    },
    {
      "id": "rest-t12",
      "name": "Tink-A-Tako #12",
      "code": "T12",
      "sales": 85361.41,
      "laborCost": 20596.550000000003,
      "laborPercent": 24.1,
      "cogs": 0,
      "cogsPercent": 0.0,
      "netProfit": 64764.86,
      "profitMargin": 75.9,
      "status": "excellent",
      "grade": "B",
      "dailyBreakdown": [
        {
          "day": "Wednesday",
          "date": "2025-08-20",
          "sales": 5637.68,
          "laborCost": 1537.18,
          "cogs": 0
        },
        {
          "day": "Thursday",
          "date": "2025-08-21",
          "sales": 6361.13,
          "laborCost": 1787.78,
          "cogs": 0
        },
        {
          "day": "Friday",
          "date": "2025-08-22",
          "sales": 8407.16,
          "laborCost": 1627.6100000000001,
          "cogs": 0
        },
        {
          "day": "Saturday",
          "date": "2025-08-23",
          "sales": 9165.22,
          "laborCost": 2261.42,
          "cogs": 0
        },
        {
          "day": "Sunday",
          "date": "2025-08-24",
          "sales": 7406.07,
          "laborCost": 1411.2,
          "cogs": 0
        },
        {
          "day": "Monday",
          "date": "2025-08-25",
          "sales": 5659.62,
          "laborCost": 1397.2,
          "cogs": 0
        },
        {
          "day": "Tuesday",
          "date": "2025-08-26",
          "sales": 5014.89,
          "laborCost": 1324.8300000000002,
          "cogs": 0
        },
        {
          "day": "Wednesday",
          "date": "2025-08-27",
          "sales": 5684.5,
          "laborCost": 1625.5799999999997,
          "cogs": 0
        },
        {
          "day": "Thursday",
          "date": "2025-08-28",
          "sales": 6675.79,
          "laborCost": 1579.1,
          "cogs": 0
        },
        {
          "day": "Friday",
          "date": "2025-08-29",
          "sales": 8155.45,
          "laborCost": 1720.57,
          "cogs": 0
        },
        {
          "day": "Saturday",
          "date": "2025-08-30",
          "sales": 9573.5,
          "laborCost": 2630.2200000000003,
          "cogs": 0
        },
        {
          "day": "Sunday",
          "date": "2025-08-31",
          "sales": 7620.4,
          "laborCost": 1693.86,
          "cogs": 0
        }
      ],
      "cashFlow": {
        "total_cash": 11574.2,
        "total_tips": -133.01,
        "total_vendor_payouts": 0,
        "net_cash": 11707.210000000001,
        "vendor_payouts": [],
        "shifts": {
          "Morning": {
            "cash": 6944.52,
            "tips": -79.81,
            "payouts": 0,
            "net": 7024.33,
            "drawers": []
          },
          "Evening": {
            "cash": 4629.68,
            "tips": -53.2,
            "payouts": 0,
            "net": 4682.88,
            "drawers": []
          }
        }
      }
    },
    {
      "id": "rest-tk9",
      "name": "Tink-A-Tako #9",
      "code": "TK9",
      "sales": 42213.46,
      "laborCost": 9881.020000000002,
      "laborPercent": 23.4,
      "cogs": 0,
      "cogsPercent": 0.0,
      "netProfit": 32332.44,
      "profitMargin": 76.6,
      "status": "excellent",
      "grade": "B",
      "dailyBreakdown": [
        {
          "day": "Wednesday",
          "date": "2025-08-20",
          "sales": 2749.7,
          "laborCost": 852.72,
          "cogs": 0
        },
        {
          "day": "Thursday",
          "date": "2025-08-21",
          "sales": 3261.18,
          "laborCost": 705.76,
          "cogs": 0
        },
        {
          "day": "Friday",
          "date": "2025-08-22",
          "sales": 3625.48,
          "laborCost": 906.56,
          "cogs": 0
        },
        {
          "day": "Saturday",
          "date": "2025-08-23",
          "sales": 3932.92,
          "laborCost": 1097.75,
          "cogs": 0
        },
        {
          "day": "Sunday",
          "date": "2025-08-24",
          "sales": 3707.99,
          "laborCost": 854.5000000000001,
          "cogs": 0
        },
        {
          "day": "Monday",
          "date": "2025-08-25",
          "sales": 3135.87,
          "laborCost": 825.81,
          "cogs": 0
        },
        {
          "day": "Tuesday",
          "date": "2025-08-26",
          "sales": 3219.72,
          "laborCost": 628.0200000000001,
          "cogs": 0
        },
        {
          "day": "Wednesday",
          "date": "2025-08-27",
          "sales": 3317.26,
          "laborCost": 654.75,
          "cogs": 0
        },
        {
          "day": "Thursday",
          "date": "2025-08-28",
          "sales": 3614.93,
          "laborCost": 705.0500000000001,
          "cogs": 0
        },
        {
          "day": "Friday",
          "date": "2025-08-29",
          "sales": 4282.35,
          "laborCost": 984.25,
          "cogs": 0
        },
        {
          "day": "Saturday",
          "date": "2025-08-30",
          "sales": 4203.77,
          "laborCost": 872.1800000000001,
          "cogs": 0
        },
        {
          "day": "Sunday",
          "date": "2025-08-31",
          "sales": 3162.29,
          "laborCost": 793.6700000000001,
          "cogs": 0
        }
      ],
      "cashFlow": {
        "total_cash": 12626.650000000001,
        "total_tips": 0.0,
        "total_vendor_payouts": 0,
        "net_cash": 12626.650000000001,
        "vendor_payouts": [],
        "shifts": {
          "Morning": {
            "cash": 7575.99,
            "tips": 0.0,
            "payouts": 0,
            "net": 7575.99,
            "drawers": []
          },
          "Evening": {
            "cash": 5050.66,
            "tips": 0.0,
            "payouts": 0,
            "net": 5050.66,
            "drawers": []
          }
        }
      }
    }
  ],
  "autoClockout": []
}
};

// Metadata
export const metadata = {
  dateRange: {
    start: '2025-08-20',
    end: '2025-08-31',
    days: 12
  },
  restaurants: ["SDR", "T12", "TK9"],
  generated: '2025-11-12T08:09:09.482800',
  version: 'V4.0',
  source: 'OMNI V4 Pipeline - Accurate PayrollExport Data',
};

// Default export
export default v4Data;
