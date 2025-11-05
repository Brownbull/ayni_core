# AYNI Core - UX Vision & User Journey

## Core UX Philosophy
"Latin American, and specially Chilean people like compact, high-value, visual, obvious information. We are less patient than US or Europe market, and we are highly adverse to risk. Loading data and getting insights must feel like a superpower."

## Key UX Principles
1. **Instant Value**: Show insights within seconds of data upload
2. **Visual First**: Charts and graphics over tables and text
3. **Compact Information**: High information density, minimal scrolling
4. **Risk Clarity**: No financial advice, only data presentation
5. **Cultural Fit**: Designed for Chilean business context

## User Journey Map

### 1. Landing Page
**Purpose**: Communicate vision and value proposition
**Content**:
- Hero section: "Haz crecer tu PYME con el poder de los datos"
- Value props:
  - "Compara tu negocio con el mercado (anónimo)"
  - "Visualiza tu crecimiento en el tiempo"
  - "Decisiones respaldadas por datos, no intuición"
- Trust signals: "10+ PYMEs para garantizar anonimato"
- CTA: "Comienza Gratis" / "Ver Demo"

### 2. Authentication Flow
**Login Page**:
- Simple email/password
- Social login options (Google, Microsoft)
- "Recordar sesión" checkbox
- Link to register

**Register Page**:
- Minimal fields (email, password, company name)
- Terms acceptance
- Auto-create first company

### 3. Main Dashboard (Post-Login)
**Layout**:
```
┌─────────────────────────────────────┐
│  [Logo] [Company Selector ▼] [User] │
├─────────────────────────────────────┤
│  Quick Stats Bar                    │
│  Revenue ↑12% | Customers +45 | ... │
├──────────┬──────────────────────────┤
│          │                          │
│  Nav     │  Main Content Area       │
│  ----    │                          │
│  📊 Panel│  [Year ▼] [View Type ▼]  │
│  📤 Subir│                          │
│  📈 Hist │  [Jan][Feb][Mar] Q1      │
│  ⚡ Buff │  [Apr][May][Jun] Q2      │
│  🏆 Rank │  [Jul][Aug][Sep] Q3      │
│  ⚙️ Conf │  [Oct][Nov][Dec] Q4      │
│          │                          │
└──────────┴──────────────────────────┘
```

**Components**:
- **Company Selector**: Dropdown with company logos
- **Quick Stats Bar**: 4-5 key metrics with sparklines
- **Navigation**: Icon-based, collapsible
- **Month Selector**: Visual calendar grid
- **View Type**: Owner/Operations/Marketing dropdown

### 4. CSV Upload Flow
**Upload Interface**:
```
┌─────────────────────────────────────┐
│     🔮 Sube tu archivo CSV          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │                               │   │
│  │    Drop files here or        │   │
│  │    [Select File]              │   │
│  │                               │   │
│  └─────────────────────────────┘   │
│                                     │
│  ✓ Detectamos 12 columnas          │
│                                     │
│  Mapeo de Columnas:                │
│  Your Column → Our Column           │
│  [fecha_vta ▼] → [transaction_date] │
│  [cliente  ▼] → [customer_name]     │
│  [monto    ▼] → [amount]           │
│                                     │
│  [Procesar] [Guardar Mapeo]        │
└─────────────────────────────────────┘
```

**Processing Status**:
- Real-time progress bar
- Live row counter
- Intermediate file downloads available
- WebSocket updates

### 5. Analytics Views

#### Monthly View (Default)
```
┌─────────────────────────────────────┐
│  Octubre 2024 - Vista Dueño        │
├─────────────────────────────────────┤
│  KPIs Principales                   │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │$245K │ │ 156  │ │ 35%  │        │
│  │Revenue│ │Clients│ │Margin│        │
│  └──────┘ └──────┘ └──────┘        │
│                                     │
│  Tendencia Mensual                  │
│  [════ Line Chart ════]             │
│                                     │
│  Top Productos        Top Clientes  │
│  1. Prod A $45K      1. Cliente X   │
│  2. Prod B $38K      2. Cliente Y   │
│  3. Prod C $28K      3. Cliente Z   │
└─────────────────────────────────────┘
```

#### Buffs/Debuffs Section
```
┌─────────────────────────────────────┐
│  📊 Indicadores Económicos          │
├─────────────────────────────────────┤
│  BUFFS ⬆️                           │
│  • Dólar -2.3% (favorable import)   │
│  • IPC estable (costs controlled)   │
│                                     │
│  DEBUFFS ⬇️                         │
│  • Tasa interés +0.5% (credit $$)   │
│  • Desempleo +1.2% (less demand)    │
│                                     │
│  Tu Score: 7.2/10 (Sobre promedio)  │
└─────────────────────────────────────┘
```

### 6. Role-Based Views

#### Owner View
- Strategic KPIs (revenue, profit, growth)
- Market comparison
- Long-term trends
- Investment opportunities

#### Operations View
- Inventory metrics
- Efficiency ratios
- Supply chain indicators
- Process bottlenecks

#### Marketing View
- Customer acquisition
- Retention rates
- Campaign performance
- Customer segments

### 7. Historical Data Panel
```
┌─────────────────────────────────────┐
│  📈 Datos Históricos                │
├─────────────────────────────────────┤
│  [2024 ▼]                          │
│                                     │
│  ┌─────┬─────┬─────┬─────┐        │
│  │ Q1  │ Q2  │ Q3  │ Q4  │        │
│  ├─────┼─────┼─────┼─────┤        │
│  │$520K│$580K│$612K│ ... │        │
│  └─────┴─────┴─────┴─────┘        │
│                                     │
│  [Ver Detalle] [Exportar]          │
└─────────────────────────────────────┘
```

## Visual Design Guidelines

### Color Palette
- **Primary**: #2563EB (Trust blue)
- **Success**: #10B981 (Growth green)
- **Warning**: #F59E0B (Alert amber)
- **Danger**: #EF4444 (Risk red)
- **Neutral**: #6B7280 (Data gray)

### Typography
- **Headers**: Inter or Montserrat (clean, modern)
- **Body**: System fonts (fast loading)
- **Numbers**: Tabular nums (aligned data)

### Components (Using Tailwind Premium)
- Cards with subtle shadows
- Smooth transitions (300ms)
- Hover states on all interactive elements
- Loading skeletons for data fetching
- Toast notifications for actions

## Responsive Design

### Mobile (320-768px)
- Stack navigation → bottom tabs
- Swipeable month selector
- Collapsible sections
- Touch-optimized controls

### Tablet (768-1024px)
- Side navigation visible
- 2-column layouts
- Larger touch targets

### Desktop (1024px+)
- Full navigation
- Multi-column dashboards
- Keyboard shortcuts
- Advanced filters

## Performance Targets
- **Initial Load**: < 2 seconds
- **Time to Interactive**: < 3 seconds
- **Data Update**: < 500ms
- **Chart Render**: < 100ms

## Accessibility
- WCAG AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode
- Text scaling support

## Legal Disclaimers
Every analytics page must include:
```
"Esta información es solo para fines informativos.
No constituye asesoría financiera, legal o tributaria.
Consulte con profesionales antes de tomar decisiones."
```

## Success Metrics
- **Task Completion Rate**: > 90%
- **Error Rate**: < 2%
- **User Satisfaction**: > 4.5/5
- **Time to First Insight**: < 30 seconds
- **Daily Active Users**: > 60%

---

**Remember**: The platform should feel like giving PYMEs a superpower, not another complex tool to learn. Every interaction should provide immediate value and build confidence in data-driven decisions.