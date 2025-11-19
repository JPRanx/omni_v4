/**
 * Dashboard V3 - Overview Card Component
 *
 * Renders the main overview metrics card using engines
 * Uses BusinessEngine for calculations and formatting
 */

export function renderOverviewCard(engines, { data }) {
  const { themeEngine, businessEngine, layoutEngine } = engines;

  // Get styling from ThemeEngine
  const borderRadius = themeEngine.getBorder('radius', 'lg');
  const shadow = themeEngine.getComponentShadow('overviewCard', 'default');

  // Get colors from ThemeEngine (V3.0 Semantic)
  const labelColor = themeEngine.getSemanticTextColor('secondary');
  const borderColor = themeEngine.getSemanticBorderColor('default');
  const hoverTransform = themeEngine.getTransform('hoverLift');
  const normalTransform = themeEngine.getTransform('none');
  const transitionDuration = themeEngine.getAnimationDuration('normal');
  const transitionEasing = themeEngine.getAnimationEasing('ease');

  // Format values using BusinessEngine (matching original dashboard)
  const formattedSales = businessEngine.formatCurrency(data.totalSales);
  const formattedLabor = businessEngine.formatCurrency(data.totalLabor);
  const formattedCash = businessEngine.formatCurrency(data.totalCash || 0);
  const overtimeHours = data.overtimeHours || 0;

  // Check validation status
  const validationReport = window.dashboardApp?.getValidationReport();
  const hasIssues = validationReport && !validationReport.valid;

  // Create validation badge if issues detected
  const validationBadge = hasIssues ? `
    <span style="
      background: ${themeEngine.getSemanticStatusColor('warning', 'bg')};
      color: ${themeEngine.getSemanticStatusColor('warning', 'text')};
      border: 1px solid ${themeEngine.getSemanticStatusColor('warning', 'border')};
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      margin-left: 0.5rem;
      cursor: help;
    " title="Data consistency issues detected. Check console for details or run window.checkDataConsistency()">
      ⚠️ ${validationReport.errors.length} Issue${validationReport.errors.length !== 1 ? 's' : ''}
    </span>
  ` : '';

  // Create overview HTML (matching original dashboard structure)
  const overviewHTML = `
    <div class="card mb-8" style="border-radius: ${borderRadius}; box-shadow: ${shadow};">
      <div class="card-header">
        <h2 class="card-title">📊 Week Overview${validationBadge}</h2>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
        <!-- Total Sales -->
        <div>
          <div style="font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; color: ${labelColor};">
            💰 Total Sales
          </div>
          <div style="font-size: 2rem; font-weight: 300; margin-bottom: 0.5rem;">
            ${formattedSales}
          </div>
        </div>

        <!-- Total Labor -->
        <div>
          <div style="font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; color: ${labelColor};">
            💸 Total Labor
          </div>
          <div style="font-size: 2rem; font-weight: 300; margin-bottom: 0.5rem;">
            ${formattedLabor}
          </div>
        </div>

        <!-- Total Cash (Clickable) -->
        <div
          onclick="window.showCashDetails && window.showCashDetails()"
          style="cursor: pointer; transition: all ${transitionDuration} ${transitionEasing}; border-radius: 0.5rem; padding: 0.5rem; margin: -0.5rem;"
          onmouseover="this.style.backgroundColor='${borderColor}'; this.style.transform='${hoverTransform}'"
          onmouseout="this.style.backgroundColor='transparent'; this.style.transform='${normalTransform}'"
        >
          <div style="font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; color: ${labelColor};">
            💵 Total Cash
          </div>
          <div style="font-size: 2rem; font-weight: 300; margin-bottom: 0.5rem;">
            ${formattedCash}
          </div>
        </div>

        <!-- Overtime Hours (Clickable) -->
        <div
          onclick="window.showOvertimeDetails && window.showOvertimeDetails()"
          style="cursor: pointer; transition: all ${transitionDuration} ${transitionEasing}; border-radius: 0.5rem; padding: 0.5rem; margin: -0.5rem;"
          onmouseover="this.style.backgroundColor='${borderColor}'; this.style.transform='${hoverTransform}'"
          onmouseout="this.style.backgroundColor='transparent'; this.style.transform='${normalTransform}'"
        >
          <div style="font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; color: ${labelColor};">
            ⏰ Overtime Hours
          </div>
          <div style="font-size: 2rem; font-weight: 300; margin-bottom: 0.5rem;">
            ${overtimeHours.toFixed(1)}
          </div>
        </div>
      </div>
    </div>
  `;

  // Render to DOM
  const overviewElement = document.getElementById('overview');
  if (overviewElement) {
    overviewElement.innerHTML = overviewHTML;
  }
}
