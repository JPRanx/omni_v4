/**
 * Dashboard V3 - Auto Clockout Table Component
 *
 * Renders employee auto-clockout warnings table
 * Uses engines for styling and thresholds
 */

export function renderAutoClockoutTable(engines, { employees }) {
  const { themeEngine, businessEngine, layoutEngine } = engines;

  // Get colors and styling from ThemeEngine (V3.0 Semantic)
  const textPrimary = themeEngine.getSemanticTextColor('primary');
  const textSecondary = themeEngine.getSemanticTextColor('secondary');
  const textMuted = themeEngine.getSemanticTextColor('muted');
  const borderColor = themeEngine.getSemanticBorderColor('default');
  const accentPrimary = themeEngine.getSemanticAccentColor('primary');
  const successText = themeEngine.getSemanticStatusColor('success', 'text');
  const successBg = themeEngine.getSemanticStatusColor('success', 'bg');
  const warningText = themeEngine.getSemanticStatusColor('warning', 'text');
  const warningBg = themeEngine.getSemanticStatusColor('warning', 'bg');
  const criticalText = themeEngine.getSemanticStatusColor('critical', 'text');
  const criticalBg = themeEngine.getSemanticStatusColor('critical', 'bg');

  // Get threshold from business config
  const autoClockoutThreshold = 10; // 10 hours

  // Get styling from ThemeEngine
  const borderRadius = themeEngine.getBorder('radius', 'lg');
  const tableShadow = themeEngine.getComponentShadow('table', 'container');

  // If no employees, show empty state
  if (!employees || employees.length === 0) {
    const emptyHTML = `
      <div class="mb-8">
        <h2 class="card-title mb-6" style="font-size: 1.5rem; font-weight: 600; color: ${textPrimary};">
          ⏰ Auto Clock-Out Alerts
        </h2>
        <div class="card" style="border-radius: ${borderRadius}; padding: 3rem; text-align: center;">
          <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
          <div style="font-size: 1.25rem; font-weight: 600; color: ${textPrimary}; margin-bottom: 0.5rem;">
            No Auto Clock-Out Alerts
          </div>
          <div style="color: ${textMuted};">
            All employees clocked out properly this week
          </div>
        </div>
      </div>
    `;

    const autoClockoutElement = document.getElementById('auto-clockout');
    if (autoClockoutElement) {
      autoClockoutElement.innerHTML = emptyHTML;
    }
    return;
  }

  // Create table rows
  const rowsHTML = employees.map((employee, index) => {
    // Get data fields from autoClockoutAlerts structure
    const restaurant = employee.restaurant || 'Unknown';
    const employeeName = employee.employee || 'Unknown';
    const position = employee.jobTitle || 'N/A';
    const positionType = employee.positionType || 'N/A';
    const date = employee.date || 'N/A';
    const clockIn = employee.clockIn || 'N/A';
    const clockInDay = employee.clockInDay || '';
    const shiftType = employee.shiftType || 'N/A';
    const recordedHours = employee.recordedHours || 0;
    const suggestedHours = employee.suggestedHours || 0;
    const hoursDifference = employee.hoursDifference || 0;
    const costImpact = employee.costImpact || 0;

    // Format currency
    const formattedCost = businessEngine.formatCurrency(Math.abs(costImpact));

    // Determine severity color based on hours difference
    const severityColor = Math.abs(hoursDifference) > 10 ? criticalText : Math.abs(hoursDifference) > 5 ? warningText : textPrimary;

    return `
      <tr style="background: ${index % 2 === 0 ? 'white' : 'rgba(250, 246, 240, 0.5)'};">
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${textPrimary};">
          ${restaurant}
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${textPrimary};">
          ${employeeName}
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${textPrimary};">
          ${position}
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${textPrimary};">
          ${date}
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${textPrimary};">
          ${clockIn} (${clockInDay})
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${textPrimary};">
          ${shiftType} / ${positionType}
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${criticalText}; font-weight: 600;">
          ${recordedHours.toFixed(1)}h
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${successText}; font-weight: 600;">
          ${suggestedHours.toFixed(1)}h
        </td>
        <td style="padding: 1rem; border-top: 1px solid ${borderColor}; color: ${severityColor}; font-weight: bold;">
          ${formattedCost}
        </td>
      </tr>
    `;
  }).join('');

  // Table HTML
  const tableHTML = `
    <div class="mb-8">
      <h2 class="card-title mb-6" style="font-size: 1.5rem; font-weight: 600; color: ${textPrimary};">
        ⏰ Auto Clock-Out Alerts
        <span style="
          background: ${warningBg};
          color: ${warningText};
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          font-weight: 600;
          margin-left: 0.75rem;
        ">
          ${employees.length} ${employees.length === 1 ? 'Alert' : 'Alerts'}
        </span>
      </h2>

      <div class="table-container" style="border-radius: ${borderRadius}; box-shadow: ${tableShadow};">
        <table class="table">
          <thead>
            <tr>
              <th style="padding: 1rem;">Restaurant</th>
              <th style="padding: 1rem;">Employee</th>
              <th style="padding: 1rem;">Position</th>
              <th style="padding: 1rem;">Date</th>
              <th style="padding: 1rem;">Clock In</th>
              <th style="padding: 1rem;">Shift / Type</th>
              <th style="padding: 1rem;">Recorded Hours</th>
              <th style="padding: 1rem;">Suggested Hours</th>
              <th style="padding: 1rem;">Cost Impact</th>
            </tr>
          </thead>
          <tbody>
            ${rowsHTML}
          </tbody>
        </table>
      </div>

      <!-- Info Footer -->
      <div style="
        margin-top: 1rem;
        padding: 1rem;
        background: ${themeEngine.getSemanticBackgroundColor('hover')};
        border-radius: ${borderRadius};
        border-left: 4px solid ${accentPrimary};
      ">
        <div style="font-size: 0.875rem; color: ${textSecondary};">
          <strong>ℹ️ Auto Clock-Out Policy:</strong>
          Employees who forgot to clock out manually are automatically clocked out at 4:00 AM. Suggested hours are based on typical shift schedules. Cost impact shows estimated overage at $15/hr.
        </div>
      </div>
    </div>
  `;

  // Render to DOM
  const autoClockoutElement = document.getElementById('auto-clockout');
  if (autoClockoutElement) {
    autoClockoutElement.innerHTML = tableHTML;
  }
}
