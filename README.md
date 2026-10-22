# Amazon One — AI-Powered Unified Amazon Ecosystem Super App

**Amazon One** is an independent hackathon prototype that consolidates multiple Amazon services into one convenient, personalized, and AI-assisted super app.

Instead of navigating disconnected websites and applications, users can discover services, manage smart devices, explore Prime entertainment, read Kindle books, interact with AWS Cloud and Bedrock AI, track orders, and shop or sell products through a single interface.

---

## 🌟 Key Architecture & Features

### 1. Centralized Dashboard (`/`)
- **Ecosystem Pillars**: Quick jump tiles for Shopping, Amazon Pay, Prime Entertainment, and AWS Cloud.
- **Search Amazon Services**: Instant search across 18 Amazon services and tools.
- **Personalized Recommendations**: Dynamic service ranking tailored to user-selected interests (*Shopping, Entertainment, Cloud, Devices, Reading, Payments, Business*).
- **Interactive Telemetry & Analytics**: Simulated weekly usage chart built with Recharts, recently visited services, and Prime savings counter.

### 2. Complete 18-Service Directory (`/services` & `/services/:serviceId`)
Comprehensive coverage across the 7 major Amazon pillars:
1. **Shopping & Commerce**: Amazon Shopping, Amazon Fresh, Amazon Business, Amazon Renewed.
2. **Payments**: Amazon Pay (1-click checkout, buyer protections, zero fraud liability).
3. **Entertainment**: Prime Video (4K HDR originals), Amazon Music (Ultra HD lossless), Audible (audiobooks).
4. **Reading**: Kindle (e-books, Whispersync), Goodreads (reading challenge and book reviews).
5. **Smart Devices**: Alexa & Echo devices, Fire TV 4K Max, Amazon Photos cloud backup.
6. **Cloud & AI**: Amazon Web Services (AWS), Amazon Bedrock (generative AI foundation models), EC2, S3.
7. **Business & Creators**: Amazon Seller Central (FBA), Kindle Direct Publishing (KDP), Twitch Interactive.

### 3. Dedicated Functional Service Modules
- **Shopping (`/shopping`)**: Search, filter by category/price, compare specifications, add to cart, and customer selling.
- **Selling & Marketplace (`/sell`)**: Customers can list their own products with full technical specifications (RAM, GPU, storage, battery, condition).
- **Payments (`/payments`)**: Simulated wallet status, merchant transaction history, spending distribution pie chart, and an interactive FAQ assistant.
- **Entertainment (`/entertainment`)**: Unified media catalogue across Prime Video, Amazon Music, and Audible with simulated streaming playback preview.
- **Reading (`/reading`)**: Kindle digital bookshelf, Goodreads reading challenge tracker, progress increments, and add-book form.
- **Smart Devices (`/devices`)**: Interactive smart-home dashboard with live power toggles, simulated Alexa voice command assistant, and Echo Show photo gallery sync.
- **Cloud & AI (`/cloud`)**: AWS service overviews, interactive **Amazon Bedrock AI playground** to test foundation models (*Claude 3.5 Sonnet, Llama 3, Titan*), and compute telemetry charts.
- **Business & Creators (`/business`)**: Seller Central sales velocity charts, FBA shipment tracking, and KDP/Twitch portals.
- **Cart (`/cart`)**: Complete demo shopping cart with tax calculation, Prime free shipping guarantee, and checkout flow.
- **Favorites (`/favorites`)**: Bookmarked services with 1-click access.
- **Personalization Settings (`/settings`)**: Customizable user interests dynamically influencing dashboard recommendations.

### 4. AI-Powered Service Discovery Concierge (`/assistant`)
- Natural language conversational assistant answering queries such as:
  - *"Which Amazon service can help me buy groceries?"* -> Recommends Amazon Fresh
  - *"Where can I listen to audiobooks?"* -> Recommends Audible
  - *"Which service is useful for hosting my website?"* -> Recommends AWS
  - *"How can I publish my own book?"* -> Recommends KDP
  - *"I want to listen to Kannada songs."* -> Recommends Amazon Music
- Pre-populated quick inquiries, typing indicator, and direct in-app navigation buttons.

### 5. Backend Architecture (Python FastAPI)
Located in `backend/`:
- `GET /api/services` — directory with search and category filtering.
- `GET /api/services/{id}` — individual service metadata.
- `POST /api/assistant` — natural language service discovery endpoint.
- `POST /api/recommendations` — interest-based service ranking.
- `GET /api/dashboard` — ecosystem metrics and simulated activities.
- Automatic fallback: The React frontend operates offline with sample data if the backend is not running.

---

## 🛠️ Technology Stack

- **Frontend**: React 19, JavaScript (ES Modules), Vite 8, React Router DOM v7, Lucide React, Recharts.
- **Backend**: Python 3.14 / 3.11+, FastAPI, Uvicorn, Pydantic.
- **Storage**: Browser LocalStorage for demo cart, favorites, and interest settings.

---

## 🚀 Installation & Running Guide

### Step 1: Run the Frontend

```powershell
# Navigate to the project root
cd "c:\Users\Ganesh\OneDrive\Desktop\Amazon hack"

# Dependencies are already installed!
# Start the Vite development server:
npm run dev
```
Open **`http://localhost:5173/`** in your browser.

### Step 2: (Optional) Run the FastAPI Backend

```powershell
# In a separate terminal:
cd "c:\Users\Ganesh\OneDrive\Desktop\Amazon hack\backend"

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: **`http://localhost:8000/docs`**

---

## 📁 Project Directory Structure

```
Amazon hack/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application with REST endpoints
│   │   └── services_data.py      # Structured directory of 18 Amazon services
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Environment variables template
├── public/
├── src/
│   ├── components/
│   │   ├── OneNavbar.jsx         # Header with global search, notifications, cart & favorites
│   │   ├── OneSidebar.jsx        # Collapsible navigation across all 7 pillars
│   │   ├── ServiceCard.jsx       # Card with favorite toggle, specs, and external links
│   │   ├── Footer.jsx            # Project footer & hackathon disclaimers
│   │   └── ...                   # Reusable components
│   ├── context/
│   │   ├── OneContext.jsx        # Cart, favorites, interests, recents & toast state
│   │   └── ProductContext.jsx    # Multi-product catalog and customer selling storage
│   ├── pages/
│   │   ├── OneDashboard.jsx      # Central hub, charts, recommendations, search
│   │   ├── OneAllServices.jsx    # Complete 18-service directory
│   │   ├── ServiceDetails.jsx    # Individual service detail breakdown
│   │   ├── OneShopping.jsx       # Retail & groceries catalog with demo cart
│   │   ├── OnePayments.jsx       # Amazon Pay digital wallet & spending charts
│   │   ├── OneEntertainment.jsx  # Prime Video, Music & Audible with audio preview
│   │   ├── OneReading.jsx        # Kindle bookshelf & reading tracker
│   │   ├── OneDevices.jsx        # Smart home toggles & Alexa voice simulator
│   │   ├── OneCloud.jsx          # AWS & Amazon Bedrock foundation model playground
│   │   ├── OneBusiness.jsx       # Seller Central sales charts & KDP/Twitch portals
│   │   ├── OneAssistant.jsx      # Conversational AI service discovery concierge
│   │   ├── OneCart.jsx           # Demo shopping cart with Prime checkout
│   │   ├── OneFavorites.jsx      # Saved bookmarks
│   │   ├── OneSettings.jsx       # User interest preferences
│   │   └── SellProduct.jsx       # Community customer product listing form
│   ├── data/
│   │   ├── services.js           # 18 services metadata
│   │   └── products.js           # Sample product catalog
│   ├── App.jsx                   # Layout, router configuration & 404 fallback
│   ├── main.jsx                  # Root entry with React context providers
│   └── index.css                 # Navy & amber design tokens, responsive styles
├── package.json
└── README.md
```
