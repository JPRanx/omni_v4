/**
 * Dashboard V3 - Restaurant Cards Component
 *
 * Renders restaurant performance cards with evaluate functionality
 * Uses all engines for styling, layout, and business logic
 */

export function renderRestaurantCards(engines, { restaurants, cashFlow, onInvestigate }) {
  const { themeEngine, businessEngine, layoutEngine } = engines;

  // Get colors and styling from ThemeEngine (V3.0 Semantic)
  const textPrimary = themeEngine.getSemanticTextColor('primary');
  const textSecondary = themeEngine.getSemanticTextColor('secondary');
  const textMuted = themeEngine.getSemanticTextColor('muted');

  // Get grid layout from LayoutEngine
  const gridClasses = layoutEngine.getGridClasses('restaurants');

  // Get styling from ThemeEngine
  const borderRadius = themeEngine.getBorder('radius', 'lg');
  const cardShadow = themeEngine.getComponentShadow('restaurantCard', 'default');

  // Create restaurant cards HTML
  const cardsHTML = restaurants.map((restaurant, index) => {
    // Evaluate restaurant performance using BusinessEngine
    const evaluation = businessEngine.evaluateRestaurant({
      sales: restaurant.sales,
      laborCost: restaurant.laborCost,
      laborHours: 0, // Not provided in sample data
      cogs: restaurant.cogs,
    });

    // Get cash value from cashFlow data
    const restaurantCash = cashFlow?.restaurants?.[restaurant.code]?.total_cash || 0;

    // Format values using BusinessEngine
    const formattedSales = businessEngine.formatCurrency(restaurant.sales);
    const formattedLabor = businessEngine.formatCurrency(restaurant.laborCost);
    const formattedLaborPercent = businessEngine.formatPercentage(evaluation.metrics.laborPercent);
    const formattedCogs = businessEngine.formatCurrency(restaurant.cogs);
    const formattedCogsPercent = businessEngine.formatPercentage(evaluation.metrics.cogsPercent);
    const formattedCash = businessEngine.formatCurrency(restaurantCash);
    const formattedProfit = businessEngine.formatCurrency(evaluation.metrics.netProfit);
    const formattedProfitMargin = businessEngine.formatPercentage(evaluation.metrics.profitMargin);

    // Get status classes
    const overallStatusClasses = businessEngine.getStatusClasses(evaluation.statuses.overall);
    const laborStatusClasses = businessEngine.getStatusClasses(evaluation.statuses.labor);

    // Calculate stagger delay
    const delay = index * 0.1;

    return `
      <div
        class="restaurant-card"
        data-restaurant-id="${restaurant.id}"
        style="
          border-radius: ${borderRadius};
          box-shadow: ${cardShadow};
          animation: cardFadeIn 0.6s ease ${delay}s backwards;
          cursor: pointer;
          transition: all 0.3s ease;
        "
        onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 24px -6px rgba(0,0,0,0.15)'"
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='${cardShadow}'"
      >
        <!-- Restaurant Header -->
        <div class="restaurant-header">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
              <h3 class="restaurant-name">
                ${restaurant.name}
              </h3>
              <div class="restaurant-sales">
                ${formattedSales}
              </div>
            </div>
            <div>
              <div style="
                background: rgba(255, 255, 255, 0.2);
                padding: 0.5rem 1rem;
                border-radius: 9999px;
                font-size: 1.25rem;
                font-weight: 600;
              ">
                ${evaluation.grade.label} ${evaluation.grade.emoji || ''}
              </div>
            </div>
          </div>
        </div>

        <!-- Restaurant Metrics -->
        <div class="restaurant-metrics">
          <!-- Payroll -->
          <div class="restaurant-metric">
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${textMuted}; margin-bottom: 0.25rem;">
              Payroll
            </div>
            <div style="font-size: 1.25rem; font-weight: 300; margin-bottom: 0.25rem;">
              ${formattedLabor}
            </div>
            <div style="font-size: 0.875rem; color: ${textSecondary};">
              ${formattedLaborPercent}
            </div>
          </div>

          <!-- Vendors -->
          <div class="restaurant-metric">
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${textMuted}; margin-bottom: 0.25rem;">
              Vendors
            </div>
            <div style="font-size: 1.25rem; font-weight: 300; margin-bottom: 0.25rem;">
              ${formattedCogs}
            </div>
            <div style="font-size: 0.875rem; color: ${textSecondary};">
              ${formattedCogsPercent}
            </div>
          </div>

          <!-- Overhead -->
          <div class="restaurant-metric">
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${textMuted}; margin-bottom: 0.25rem;">
              Overhead
            </div>
            <div style="font-size: 1.25rem; font-weight: 300; margin-bottom: 0.25rem;">
              $0
            </div>
            <div style="font-size: 0.875rem; color: ${textSecondary};">
              0.0%
            </div>
          </div>

          <!-- Cash -->
          <div class="restaurant-metric">
            <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: ${textMuted}; margin-bottom: 0.25rem;">
              Cash
            </div>
            <div style="font-size: 1.25rem; font-weight: 300; margin-bottom: 0.25rem;">
              ${formattedCash}
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Container HTML
  const containerHTML = `
    <div class="mb-8">
      <h2 class="card-title mb-6" style="font-size: 1.5rem; font-weight: 600; color: ${textPrimary};">
        🏪 Restaurants
      </h2>
      <div class="${gridClasses}">
        ${cardsHTML}
      </div>
    </div>
  `;

  // Render to DOM
  const restaurantsElement = document.getElementById('restaurants');
  if (restaurantsElement) {
    restaurantsElement.innerHTML = containerHTML;

    // Add click handlers directly to restaurant cards
    restaurantsElement.querySelectorAll('.restaurant-card').forEach(card => {
      card.addEventListener('click', (e) => {
        const restaurantId = card.getAttribute('data-restaurant-id');
        const restaurant = restaurants.find(r => r.id === restaurantId);

        if (restaurant && onInvestigate) {
          onInvestigate(restaurant);
        }
      });
    });
  }
}
