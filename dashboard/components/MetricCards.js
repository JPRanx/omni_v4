/**
 * Dashboard V3 - Metric Cards Component
 *
 * Renders 6 metric cards with colored left borders
 * Uses all engines for complete functionality
 */

export function renderMetricCards(engines, { metrics }) {
  const { themeEngine, businessEngine, layoutEngine } = engines;

  // Get grid layout from LayoutEngine
  const gridClasses = layoutEngine.getGridClasses('metrics');
  const gridColumns = layoutEngine.getGridColumns('metrics');

  // Get styling from ThemeEngine
  const borderRadius = themeEngine.getBorder('radius', 'lg');
  const cardShadow = themeEngine.getComponentShadow('metricCard', 'default');
  const hoverShadow = themeEngine.getComponentShadow('metricCard', 'hover');

  // Color mapping for metric cards
  const colorMap = {
    blue: '#3B82F6',
    green: '#10B981',
    yellow: '#F59E0B',
    red: '#EF4444',
    purple: '#8B5CF6',
    cyan: '#06B6D4',
  };

  // Create metric cards HTML
  const cardsHTML = metrics.map((metric, index) => {
    // Format value based on type using BusinessEngine
    let formattedValue;
    if (metric.type === 'currency') {
      formattedValue = businessEngine.formatCurrency(metric.value);
    } else if (metric.type === 'percentage') {
      formattedValue = businessEngine.formatPercentage(metric.value);
    } else {
      formattedValue = metric.value.toLocaleString();
    }

    // Get status classes from BusinessEngine
    const statusClasses = metric.status
      ? businessEngine.getStatusClasses(metric.status)
      : '';

    // Get color for left border
    const borderColor = colorMap[metric.color] || colorMap.blue;

    // Calculate stagger animation delay
    const delay = index * 0.05;

    return `
      <div
        class="metric-card"
        style="
          border-radius: ${borderRadius};
          box-shadow: ${cardShadow};
          color: ${borderColor};
          animation: metricFadeIn 0.5s ease ${delay}s backwards;
        "
      >
        <!-- Icon -->
        <div class="metric-icon" style="font-size: 48px;">
          ${metric.icon}
        </div>

        <!-- Value -->
        <div class="metric-value" style="color: ${borderColor};">
          ${formattedValue}
        </div>

        <!-- Label -->
        <div class="metric-label">
          ${metric.label}
        </div>

        <!-- Status Badge (if present) -->
        ${metric.status ? `
          <div style="margin-top: 0.75rem;">
            <span class="${statusClasses}" style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500;">
              ${metric.status}
            </span>
          </div>
        ` : ''}

        <!-- Variance (if present) -->
        ${metric.variance !== undefined ? `
          <div style="margin-top: 0.5rem; font-size: 0.875rem;">
            ${formatVariance(metric.variance, businessEngine)}
          </div>
        ` : ''}
      </div>
    `;
  }).join('');

  // Container HTML with responsive grid
  const containerHTML = `
    <div class="mb-8">
      <h2 class="card-title mb-6" style="font-size: 1.5rem; font-weight: 600; color: #3D3128;">
        📊 Key Metrics
      </h2>
      <div class="${gridClasses}" style="animation-delay: 0s;">
        ${cardsHTML}
      </div>
    </div>
  `;

  // Render to DOM
  const metricsElement = document.getElementById('metrics');
  if (metricsElement) {
    metricsElement.innerHTML = containerHTML;
  }
}

/**
 * Format variance with icon and color
 */
function formatVariance(variance, businessEngine) {
  const formatted = businessEngine.formatVariance(variance);

  const colorClass = formatted.color === 'success'
    ? 'text-green-600'
    : formatted.color === 'critical'
    ? 'text-red-600'
    : 'text-gray-600';

  return `
    <span class="${colorClass}" style="font-weight: 600;">
      ${formatted.icon} ${formatted.text}
    </span>
    <span style="color: #6E5D4B; font-size: 0.75rem; margin-left: 0.25rem;">
      vs last week
    </span>
  `;
}
