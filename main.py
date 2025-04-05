from fastapi import FastAPI, HTTPException, Depends, Request, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import json
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Side Hustle Planner")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Check if API key exists
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Initialize Gemini API
genai.configure(api_key=api_key)

# Initialize the model with the correct name
model = genai.GenerativeModel('gemini-2.0-flash')

# Data models
class UserProfile(BaseModel):
    skills: List[str] = Field(..., min_items=1, description="List of user skills")
    interests: List[str] = Field(..., min_items=1, description="List of user interests")
    experience_level: str = Field(..., description="User experience level")
    preferred_income: float = Field(..., gt=0, description="Desired monthly income")

class GigOpportunity(BaseModel):
    title: str
    platform: str
    description: str
    required_skills: List[str]
    estimated_income: float
    time_commitment: str
    difficulty_level: str

class MarketAnalysisRequest(BaseModel):
    skills: List[str] = Field(..., min_items=1, description="Skills to analyze")

class GigCommitment(BaseModel):
    gig_name: str
    hours_per_week: int = Field(..., ge=0)
    deadline_flexibility: str = Field(..., pattern="^(high|medium|low)$")

class ScheduleOptimization(BaseModel):
    main_job_hours: int = Field(..., ge=0, le=24, description="Hours spent on main job per day")
    available_hours: int = Field(..., ge=0, le=24, description="Available hours for side hustles per day")
    preferred_work_times: List[str] = Field(..., description="Preferred times to work (e.g., ['morning', 'evening'])")
    gig_commitments: List[GigCommitment] = Field(..., description="List of gig commitments with time requirements")

# In-memory storage (replace with database in production)
user_profiles = {}
gig_opportunities = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/profile")
async def create_profile(profile: UserProfile):
    try:
        prompt = f"""
        Based on the following user profile, suggest relevant side gigs:
        Skills: {', '.join(profile.skills)}
        Interests: {', '.join(profile.interests)}
        Experience: {profile.experience_level}
        Desired Income: ${profile.preferred_income}
        
        Provide specific gig recommendations with platforms and estimated income.
        Format your response in a clear, structured way with bullet points.
        """
        
        response = model.generate_content([{ "parts": [{"text": prompt}] }])
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate recommendations")
            
        recommendations = response.text
        
        return {
            "status": "success",
            "profile": profile.dict(),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities")
async def get_opportunities(skills: Optional[List[str]] = None):
    if not skills:
        return gig_opportunities
    
    filtered_opportunities = [
        opp for opp in gig_opportunities
        if any(skill in opp.required_skills for skill in skills)
    ]
    return filtered_opportunities

@app.post("/api/analyze-market")
async def analyze_market(request: MarketAnalysisRequest):
    try:
        prompt = f"""
        Analyze the current market conditions and opportunities for the following skills:
        {', '.join(request.skills)}
        
        Provide detailed insights on:
        1. Current demand
        2. Average rates
        3. Growth potential
        4. Competition level
        
        Format your response in a clear, structured way with sections and bullet points.
        """
        
        response = model.generate_content([{ "parts": [{"text": prompt}] }])
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate market analysis")
            
        analysis = response.text
        
        return {
            "status": "success",
            "market_analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize-schedule")
async def optimize_schedule(request: ScheduleOptimization):
    try:
        # Convert GigCommitment objects to dictionaries for JSON serialization
        gig_commitments_dict = [gig.dict() for gig in request.gig_commitments]
        
        prompt = f"""
        Based on the following schedule parameters, provide an optimized schedule for side hustles:
        Main Job Hours: {request.main_job_hours} hours/day
        Available Hours: {request.available_hours} hours/day
        Preferred Work Times: {', '.join(request.preferred_work_times)}
        Gig Commitments: {json.dumps(gig_commitments_dict, indent=2)}
        
        Provide a detailed schedule optimization that includes:
        1. Optimal time allocation for each gig
        2. Work-life balance recommendations
        3. Productivity tips for the given schedule
        4. Potential schedule conflicts and how to resolve them
        
        Format your response in a clear, structured way with sections and bullet points.
        """
        
        response = model.generate_content([{ "parts": [{"text": prompt}] }])
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate schedule optimization")
            
        optimization = response.text
        
        return {
            "status": "success",
            "schedule_optimization": optimization
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
