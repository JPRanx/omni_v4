/**
 * Dashboard V3 - Week Tabs Component
 *
 * Renders week navigation tabs using engines
 * Shows date ranges for each week (most recent 8 weeks only)
 */

/**
 * Format date range for week tab label
 * @param {string} startDate - Start date (YYYY-MM-DD)
 * @param {string} endDate - End date (YYYY-MM-DD)
 * @returns {string} - Formatted label (e.g., "Aug 4-10" or "8/25-31")
 */
function formatWeekLabel(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  const startMonth = monthNames[start.getMonth()];
  const endMonth = monthNames[end.getMonth()];
  const startDay = start.getDate();
  const endDay = end.getDate();

  // If same month: "Aug 4-10"
  if (startMonth === endMonth) {
    return `${startMonth} ${startDay}-${endDay}`;
  }

  // If different months: "Aug 28 - Sep 3"
  return `${startMonth} ${startDay} - ${endMonth} ${endDay}`;
}

/**
 * Extract date range from week data
 * @param {Object} weekData - Week data object
 * @returns {Object} - {startDate, endDate}
 */
function getWeekDateRange(weekData) {
  // Get all dates from restaurants' dailyBreakdown
  const allDates = [];

  if (weekData.restaurants) {
    weekData.restaurants.forEach(restaurant => {
      if (restaurant.dailyBreakdown) {
        restaurant.dailyBreakdown.forEach(day => {
          if (day.date) {
            allDates.push(day.date);
          }
        });
      }
    });
  }

  if (allDates.length === 0) {
    return { startDate: 'Unknown', endDate: 'Unknown' };
  }

  // Sort dates and remove duplicates
  const uniqueDates = [...new Set(allDates)].sort();

  return {
    startDate: uniqueDates[0],
    endDate: uniqueDates[uniqueDates.length - 1]
  };
}

export function renderWeekTabs(engines, data) {
  const { themeEngine, layoutEngine } = engines;

  // Get styling from ThemeEngine
  const borderRadius = themeEngine.getBorder('radius', 'lg');
  const shadow = themeEngine.getShadow('sm');
  const activeShadow = themeEngine.getShadow('md');

  // Get all weeks sorted by week number (descending - newest first)
  const allWeeks = data.weeks.sort((a, b) => {
    const numA = parseInt(a.replace('week', ''));
    const numB = parseInt(b.replace('week', ''));
    return numB - numA; // Descending order
  });

  // Take only the most recent 8 weeks
  const recentWeeks = allWeeks.slice(0, 8);

  // Reverse to show oldest to newest (left to right)
  const displayWeeks = recentWeeks.reverse();

  // Create tabs HTML with date ranges
  const tabsHTML = displayWeeks.map(week => {
    const isActive = week === data.currentWeek;

    // Get week data to extract date range
    const weekData = data.weekData?.[week];
    let label = week.replace('week', 'Week '); // Fallback

    if (weekData) {
      const { startDate, endDate } = getWeekDateRange(weekData);
      if (startDate !== 'Unknown') {
        label = formatWeekLabel(startDate, endDate);
      }
    }

    return `
      <button
        class="week-tab ${isActive ? 'active' : ''}"
        data-week="${week}"
        style="
          border-radius: ${borderRadius};
          box-shadow: ${isActive ? activeShadow : shadow};
        "
      >
        ${label}
      </button>
    `;
  }).join('');

  const containerHTML = `
    <div class="week-tabs-wrapper">
      <div class="week-tabs-container">
        ${tabsHTML}
      </div>
    </div>
  `;

  // Render to DOM
  const weekTabsElement = document.getElementById('week-tabs');
  if (weekTabsElement) {
    weekTabsElement.innerHTML = containerHTML;

    // Add click handlers
    weekTabsElement.querySelectorAll('.week-tab').forEach(button => {
      button.addEventListener('click', (e) => {
        const week = e.target.getAttribute('data-week');
        if (data.onWeekChange) {
          data.onWeekChange(week);
        }
      });
    });
  }
}
