# MiniMax Token Remain Dashboard - Specification

## Project Overview
- **Project name**: MiniMax Token Remain
- **Type**: Single-page web dashboard
- **Core functionality**: Display MiniMax API token remaining usage and reset times from the API
- **Target users**: Developers using MiniMax API services

## API Details
- **Endpoint**: `https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains`
- **Method**: GET
- **Auth**: Bearer token (hardcoded for demo)
- **Response**: JSON with model_remains array and base_resp

## Visual & UI Specification

### Layout
- Full-page dashboard with centered content
- Dark theme with gradient background
- Card-based model display grid
- Header with title and last refresh time

### Color Palette
- Background: Deep charcoal gradient (#1a1a2e → #16213e)
- Card background: Semi-transparent dark (#0f0f23 with opacity)
- Primary accent: Electric cyan (#00d4ff)
- Secondary accent: Soft purple (#7b68ee)
- Warning (low usage): Amber (#ffb347)
- Danger (exhausted): Coral red (#ff6b6b)
- Success (available): Mint green (#4ecdc4)
- Text primary: White (#ffffff)
- Text secondary: Light gray (#a0a0a0)

### Typography
- Font: "JetBrains Mono" for data, "Inter" for labels
- Title: 2.5rem bold
- Card title (model name): 1.2rem semibold
- Data values: 1.5rem monospace

### Components
1. **Header**
   - Title: "MiniMax Token Dashboard"
   - Last refresh timestamp
   - Refresh button

2. **Model Cards**
   - Model name (prominent)
   - Usage bar showing consumed vs total
   - Stats grid: Total, Used, Remaining
   - Interval end time (reset time)
   - Weekly stats (if applicable)

3. **Status Indicators**
   - Green glow: Available tokens
   - Amber glow: Low tokens (<20%)
   - Red glow: Exhausted (100% used)

## Functionality Specification

### Core Features
- Auto-fetch API data on page load
- Manual refresh button
- Auto-refresh every 60 seconds
- Display all models from API response
- Show usage percentage with visual progress bar
- Display reset countdown timers

### Data Fields to Display per Model
- Model name
- Current interval: total count, usage count, remains
- Weekly total, weekly usage, weekly remains (if > 0)
- Interval start/end time
- Weekly start/end time (if applicable)

### Error Handling
- Show error message if API fails
- Retry button on failure
- Loading state while fetching

## Technical Stack
- Python with Flask
- HTML5 + CSS3 (inline for single-file simplicity)
- Vanilla JavaScript for API calls
- No external JS frameworks needed

## Acceptance Criteria
1. Page loads on port 3780
2. Shows all 6 models from the API response
3. Usage bars accurately reflect consumption percentage
4. Refresh button works
5. Auto-refresh every 60 seconds
6. Timestamps displayed in human-readable format
7. Responsive layout works on different screen sizes
8. No console errors
