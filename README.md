# AI-Based Side Hustle Planner

An intelligent platform that helps you discover and manage gig opportunities using Google's Gemini AI.

## Features

- Personalized gig recommendations based on your skills and preferences
- AI-powered market analysis for optimal pricing
- Skill gap analysis and learning recommendations
- Automated opportunity matching
- Income potential predictions
- Schedule optimization

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Usage

1. Access the web interface at `http://localhost:8000`
2. Complete your profile with skills and preferences
3. View personalized gig recommendations
4. Track opportunities and manage your side hustles

## Technologies Used

- FastAPI
- Google Gemini AI API
- Machine Learning (scikit-learn)
- Web Scraping (BeautifulSoup)
- Data Analysis (Pandas)

## Getting a Google API Key

1. Go to the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click on "Get API key"
4. Create a new API key or use an existing one
5. Copy the API key and paste it in your `.env` file 