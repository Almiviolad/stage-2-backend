# helpers.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import httpx
import random
import os
#import matplotlib.pyplot as plt
from database import CountryDB
import asyncio


# Configuration for the summary image file path
IMAGE_PATH = "cache/summary.png"

async def fetch_external_data(http_client: httpx.AsyncClient):
    """Fetches country data and exchange rates concurrently with 503 error handling."""
    
    COUNTRIES_URL = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    RATES_URL = "https://open.er-api.com/v6/latest/USD"
    
    try:
        # To run the two network requests concurrently
        country_resp, rates_resp = await asyncio.gather(
            http_client.get(COUNTRIES_URL, timeout=15),
            http_client.get(RATES_URL, timeout=15)
        )

        # Check for HTTP errors
        country_resp.raise_for_status()
        rates_resp.raise_for_status()
        
        # Extract the necessary rates dictionary
        rates_data = rates_resp.json().get("rates", {})
        
        return country_resp.json(), rates_data

    except httpx.ConnectError as e:
        # Handle connection failures or timeouts
        api_name = "Exchange Rate API" if e.request.url.path == "/v6/latest/USD" else "Country API"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "External data source unavailable", "details": f"Could not connect to {api_name}."}
        )
        
    except httpx.HTTPStatusError as e:
        # Handle 4xx/5xx HTTP errors from external APIs
        api_name = "Exchange Rate API" if e.request.url.path == "/v6/latest/USD" else "Country API"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "External data source unavailable", "details": f"Could not fetch data from {api_name}."}
        )

def process_and_update(db: Session, countries_data: list, rates_data: dict) -> int:
    """
    Process data and perform UPSERT using session.merge(), resolving the 
    UNIQUE constraint error by relying on the existing ID.
    """
    
    processed_count = 0
    current_timestamp = datetime.utcnow()
    
    for country_raw in countries_data:
        # --- 1. Data Processing and Cleanup ---
        
        currencies = country_raw.get("currencies")
        currency_code = currencies[0].get("code") if currencies and isinstance(currencies, list) and len(currencies) > 0 else None

        exchange_rate = None
        estimated_gdp = None
        population = country_raw.get("population") or 0
        
        if currency_code and currency_code in rates_data:
            exchange_rate = rates_data[currency_code]
            random_multiplier = random.randint(1000, 2000)
            
            if exchange_rate and population > 0:
                estimated_gdp = (population * random_multiplier) / exchange_rate
            else:
                estimated_gdp = 0.0
        elif currency_code is None:
            estimated_gdp = 0.0
            
        # --- 2. Find Existing Record ID (Case-Insensitive Lookup) ---
        
        country_name_raw = country_raw.get("name")
        country_name_lower = country_name_raw.lower()
        
        # Query for the existing primary key (ID) based on the lower-cased name
        existing_id = db.query(CountryDB.id).filter(
            func.lower(CountryDB.name) == country_name_lower
        ).scalar()        
        # --- 3. Prepare Final Data for Merge ---
        
        data_for_merge = {
            # CRUCIAL: Add the 'id' key only if found. merge() uses this 'id' to determine action.
            "id": existing_id, 
            
            # CRUCIAL: Normalize the name case for consistent storage
            "name": country_name_raw.title(), 
            
            "capital": country_raw.get("capital"),
            "region": country_raw.get("region"),
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": country_raw.get("flag"),
            "last_refreshed_at": current_timestamp
        }

        # --- 4. Perform Merge and Commit ---
        
        db.merge(CountryDB(**data_for_merge))
        
        processed_count += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
        
    return processed_count



"""def generate_summary_image(db: Session, total_countries: int, last_refreshed_at: datetime):
    Generates and saves the summary image to disk
    
    # Query Top 5 GDP (sorted descending)
    top_countries = db.query(CountryDB.name, CountryDB.estimated_gdp)\
                      .filter(CountryDB.estimated_gdp > 0)\
                      .order_by(CountryDB.estimated_gdp.desc())\
                      .limit(5).all()
                      
    if not top_countries:
        # Create an empty  file if no data exists
        os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)
        with open(IMAGE_PATH, 'w') as f:
            f.write("No data available.")
        return 

    # Prepare Data for Plotting
    # Reverse lists so the highest value appears at the top of the bar chart
    names = [c.name for c in top_countries][::-1]
    gdps = [c.estimated_gdp for c in top_countries][::-1]
    
    # Create Figure and Axes
    fig, ax = plt.subplots(figsize=(10, 6))

    #  Draw Horizontal Bar Chart
    ax.barh(names, gdps, color='skyblue') 

    # Add GDP value labels on the bars (using ax.text)
    for i, gdp in enumerate(gdps):
        ax.text(gdp, i, f' {gdp:,.0f}', va='center')

    # Customization
    ax.set_title("Top 5 Countries by Estimated GDP", fontsize=16, pad=20)
    ax.set_xlabel("Estimated GDP (units consistent with calculation)")
    ax.ticklabel_format(style='plain', axis='x') 
    
    # Add required text metadata to the Figure (using fig.text)
    fig.text(0.5, 0.95, f"Total Cached Countries: {total_countries}", 
             fontsize=12, ha='center', transform=fig.transFigure)
    fig.text(0.5, 0.92, f"Last Refresh: {last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S')} UTC", 
             fontsize=10, ha='center', transform=fig.transFigure)

    # 6. Save the Image
    os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)
    plt.tight_layout(rect=[0, 0.05, 1, 0.88])
    fig.savefig(IMAGE_PATH, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✅ Summary image successfully saved as: {IMAGE_PATH}")
"""
