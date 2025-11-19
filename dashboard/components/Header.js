/**
 * Dashboard V3 - Header Component
 *
 * Renders the main dashboard header using engines
 * NO hardcoded values - all from ThemeEngine
 */

export function renderHeader(engines, data) {
  const { themeEngine, layoutEngine } = engines;

  // Get styling from ThemeEngine
  const headerShadow = themeEngine.getComponentShadow('header', 'default');
  const headerH1Size = themeEngine.getTypography('componentSizes', 'headerH1');
  const borderRadius = themeEngine.getBorder('radius', 'lg');

  // Get layout classes from LayoutEngine
  const containerClasses = layoutEngine.getContainerClasses('dashboard');

  // Create header HTML
  const headerHTML = `
    <div class="dashboard-header" style="box-shadow: ${headerShadow}; border-radius: ${borderRadius};">
      <div style="text-align: center;">
        <h1 class="header-title" style="font-size: ${headerH1Size};">
          ${data.title}
        </h1>
        <p class="header-subtitle">
          ${data.subtitle} ${data.weekNumber}
        </p>
      </div>
    </div>
  `;

  // Render to DOM
  const headerElement = document.getElementById('header');
  if (headerElement) {
    headerElement.innerHTML = headerHTML;
  }
}
