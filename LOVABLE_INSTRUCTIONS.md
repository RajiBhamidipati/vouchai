# Lovable Instructions for VouchAI Frontend

Copy and paste the text below into Lovable.dev to generate your frontend:

---

Build a modern research platform web application with the following specifications:

## Core Functionality

### 1. Main Research Interface
- Large, centered search bar on the home page with placeholder: "Ask any research question..."
- Search input should be a textarea that expands as user types (min 2 lines, max 6 lines)
- "Research" button with loading state (shows "Analyzing..." with animated dots during API call)
- Display 4 agent avatars below search bar showing the research pipeline:
  * Scout (magnifying glass icon) - "Finding Sources"
  * Adjudicator (scales icon) - "Analyzing Facts vs Opinions"
  * Synthesizer (document icon) - "Creating Report"
  * Professor (graduation cap icon) - "Quality Audit"
- When research is running, animate each agent avatar to show progress

### 2. Results Display Page
After submitting a query, show a comprehensive results page with these sections:

#### Executive Summary Card (Top)
- Large card at top with the research summary (2-3 paragraphs)
- Include a "Quality Score" badge showing the Professor's grade (1-10) with color coding:
  * 8-10: Green badge
  * 5-7: Yellow badge
  * 1-4: Red badge

#### Facts Table (Collapsible Section)
- Display facts in a clean table with columns:
  * Claim (main text, left-aligned)
  * Confidence Level (badge: High/Medium/Low with colors)
  * Sources (clickable links as blue chips/pills)
- Make table sortable by confidence level
- Add search/filter box above table

#### Opinions Table (Collapsible Section)
- Display opinions in a card grid layout (not table)
- Each opinion card shows:
  * The claim/opinion text
  * Perspective type (e.g., "Expert Opinion", "Industry View")
  * Source links as blue underlined links
  * Different colored left border per perspective type

#### Conflicting Data Section (Only if present)
- Show as warning cards with yellow/orange borders
- Display topic and list of conflicting claims
- Show all related sources

#### Citations List
- Numbered list of all sources at bottom
- Each citation is a clickable link
- Include a "Copy All Citations" button (APA format)

#### Professor Evaluation Card
- Prominent card showing:
  * Overall score (large number with /10)
  * Feedback text
  * Hallucination check status (green checkmark if passed)
  * Recommendations as a bullet list
- Use a purple/academic color scheme for this card

### 3. Statistics Dashboard
Create a separate "/stats" page showing:
- Total queries processed (large number)
- Average quality score (with trend indicator)
- Highest and lowest scores
- Success rate percentage
- Simple line chart showing scores over time (if you can implement it)

### 4. History Sidebar (Optional Enhancement)
- Collapsible sidebar showing recent queries
- Click a query to reload its results
- Store in browser localStorage

## Design System

### Colors
- Primary: Deep blue (#1E40AF)
- Secondary: Purple (#7C3AED)
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Background: Light gray (#F9FAFB)
- Cards: White with subtle shadow

### Typography
- Headers: Bold, sans-serif (Inter or similar)
- Body: Regular sans-serif
- Code/Citations: Monospace font

### Layout
- Max width: 1200px centered
- Generous padding and spacing
- Cards with rounded corners (8px)
- Subtle shadows for depth

## API Integration

### Backend URL
- Set API base URL as environment variable: `http://localhost:8000`
- All API calls should show loading states and handle errors gracefully

### Endpoints

#### POST /research
Request:
```json
{
  "query": "string"
}
```

Response:
```json
{
  "success": boolean,
  "data": {
    "summary": "string",
    "facts_table": [
      {
        "claim": "string",
        "sources": ["string"],
        "confidence": "High|Medium|Low"
      }
    ],
    "opinions_table": [
      {
        "claim": "string",
        "sources": ["string"],
        "perspective": "string"
      }
    ],
    "conflicting_data": [
      {
        "topic": "string",
        "conflicting_claims": ["string"],
        "sources": ["string"]
      }
    ],
    "citations_list": ["string"],
    "professor_eval_score": {
      "score": 1-10,
      "feedback": "string",
      "hallucination_check": "string",
      "recommendations": ["string"]
    }
  },
  "error": "string|null"
}
```

#### GET /stats
Response:
```json
{
  "total_queries": number,
  "successful_queries": number,
  "average_score": number,
  "highest_score": number,
  "lowest_score": number
}
```

### Error Handling
- Show toast notifications for errors
- Display user-friendly error messages
- Include retry button on failed queries
- Handle network timeouts gracefully (90 second timeout)

## User Experience Features

### Loading States
- Skeleton loaders for results page
- Progress indicator showing which agent is working
- Disable submit button while processing
- Show elapsed time during research

### Responsive Design
- Mobile-first approach
- Tables should scroll horizontally on mobile
- Stack cards vertically on small screens
- Collapsible sections on mobile to reduce scroll

### Accessibility
- Proper ARIA labels
- Keyboard navigation support
- High contrast mode support
- Screen reader friendly

### Animations (Subtle)
- Fade in results sections sequentially
- Smooth scrolling between sections
- Agent avatars pulse during their active phase
- Subtle hover effects on interactive elements

## Additional Features

### Export Options
- Add "Export as PDF" button on results page
- Add "Share Link" button (copy current URL with query params)
- Add "Download JSON" for raw data

### Sample Queries
- Show 3-4 example queries on home page:
  * "What is the current state of quantum computing?"
  * "What are the health benefits and risks of intermittent fasting?"
  * "How does climate change affect biodiversity?"
  * "What is the status of renewable energy adoption globally?"

### Dark Mode
- Toggle in top-right corner
- Persist preference in localStorage
- Smooth transition between modes

## Technical Requirements
- Use React with TypeScript
- Use Tailwind CSS for styling
- Use React Query or SWR for API calls
- Use React Router for navigation
- Implement proper TypeScript types for API responses
- Use Zustand or Context for state management
- Add loading skeletons (not just spinners)

## Pages Structure
1. `/` - Home page with search interface
2. `/research?q=query` - Results page showing research output
3. `/stats` - Statistics dashboard
4. `/about` - About page explaining the 4-agent system

## Navigation
- Simple header with logo "VouchAI" and links to Home, Stats, About
- No login/auth needed for MVP

## Copy & Messaging
- Home page hero text: "AI-Powered Research with Built-in Fact-Checking"
- Subtext: "Our 4-agent system searches, analyzes, synthesizes, and audits research to give you trustworthy insights"
- CTA button: "Start Researching"

Make it feel premium, trustworthy, and academic but still modern and approachable. Think Perplexity.ai meets Google Scholar.
