import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Carbon Footprint Calculator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and introduction
st.title("Carbon Footprint Calculator")
st.markdown("""
This application helps you understand and track your carbon emissions based on your daily activities.
Enter information about your lifestyle to calculate your carbon footprint and receive personalized recommendations.
""")

# Initialize session state variables if they don't exist
if 'total_emissions' not in st.session_state:
    st.session_state.total_emissions = 0
if 'emissions_data' not in st.session_state:
    st.session_state.emissions_data = {
        'date': [],
        'transport': [],
        'home_energy': [],
        'diet': [],
        'consumption': [],
        'waste': [],
        'total': []
    }

# Create tabs for different input categories
tabs = st.tabs(["Transportation", "Home Energy", "Diet", "Consumer Habits", "Waste Management"])

with tabs[0]:  # Transportation
    st.header("Transportation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Daily Commute")
        transport_mode = st.selectbox(
            "Primary mode of transportation", 
            ["Car (Gasoline)", "Car (Diesel)", "Car (Electric)", "Car (Hybrid)", 
             "Public Bus", "Train/Subway", "Bicycle", "Walking", "Motorcycle"]
        )
        
        daily_distance = st.number_input("Daily commute distance (km)", min_value=0.0, value=10.0, step=0.5)
        
        if transport_mode.startswith("Car"):
            fuel_efficiency = st.number_input("Fuel efficiency (L/100km or kWh/100km)", min_value=0.1, value=8.0, step=0.1)
        
    with col2:
        st.subheader("Air Travel")
        flight_short = st.number_input("Short flights (<1500 km) this year", min_value=0, value=0)
        flight_medium = st.number_input("Medium flights (1500-4000 km) this year", min_value=0, value=0)
        flight_long = st.number_input("Long flights (>4000 km) this year", min_value=0, value=0)

with tabs[1]:  # Home Energy
    st.header("Home Energy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Electricity")
        electricity_kwh = st.number_input("Monthly electricity consumption (kWh)", min_value=0, value=300)
        renewable_percentage = st.slider("Percentage of renewable energy", 0, 100, 20)
        
    with col2:
        st.subheader("Heating & Cooling")
        heating_type = st.selectbox(
            "Primary heating system",
            ["Natural Gas", "Oil", "Electric", "Heat Pump", "Wood", "Coal"]
        )
        heating_usage = st.number_input("Monthly heating fuel consumption (units)", min_value=0, value=100)
        
        has_ac = st.checkbox("I use air conditioning")
        if has_ac:
            ac_hours = st.number_input("Average daily AC usage (hours)", min_value=0, value=2)

with tabs[2]:  # Diet
    st.header("Diet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        diet_type = st.selectbox(
            "What best describes your diet?",
            ["Heavy Meat Eater", "Regular Meat Eater", "Low Meat Eater", "Pescatarian", "Vegetarian", "Vegan"]
        )
        
        local_food = st.slider("Percentage of locally produced food", 0, 100, 20)
        organic_food = st.slider("Percentage of organic food", 0, 100, 20)
        
    with col2:
        food_waste = st.slider("Percentage of food wasted", 0, 100, 15)
        processed_food = st.slider("Percentage of processed food consumed", 0, 100, 30)

with tabs[3]:  # Consumer Habits
    st.header("Consumer Habits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Clothing & Personal Items")
        clothing_spending = st.select_slider(
            "Monthly spending on new clothing",
            options=["Very Low", "Low", "Average", "High", "Very High"]
        )
        
        electronics_yearly = st.number_input("New electronic devices per year", min_value=0, value=1)
        
    with col2:
        st.subheader("Other Consumption")
        recycled_items = st.multiselect(
            "Which items do you regularly recycle?",
            ["Paper", "Plastic", "Glass", "Metal", "Electronics"]
        )
        
        second_hand = st.slider("Percentage of items bought second-hand", 0, 100, 10)

with tabs[4]:  # Waste Management
    st.header("Waste Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        waste_weekly = st.number_input("Average weekly waste (kg)", min_value=0.0, value=10.0)
        composting = st.checkbox("I practice composting")
    
    with col2:
        recycling_rate = st.slider("Percentage of waste recycled", 0, 100, 30)
        zero_waste = st.select_slider(
            "Efforts to reduce packaging waste",
            options=["None", "Minimal", "Moderate", "Significant", "Zero-waste lifestyle"]
        )

# Create emission factors dictionary
emission_factors = {
    # Transportation (kg CO2 per km)
    "Car (Gasoline)": 0.192,
    "Car (Diesel)": 0.171,
    "Car (Electric)": 0.053,
    "Car (Hybrid)": 0.106,
    "Public Bus": 0.105,
    "Train/Subway": 0.041,
    "Bicycle": 0,
    "Walking": 0,
    "Motorcycle": 0.103,
    
    # Flights (kg CO2 per flight)
    "Short Flight": 500,
    "Medium Flight": 1500, 
    "Long Flight": 3000,
    
    # Home Energy
    "Electricity": 0.5, # kg CO2 per kWh (varies by region)
    "Natural Gas": 2.0,  # kg CO2 per unit
    "Oil": 2.7,          # kg CO2 per unit
    "Electric Heating": 0.5, # kg CO2 per kWh
    "Heat Pump": 0.25,   # kg CO2 per unit
    "Wood": 1.5,         # kg CO2 per unit
    "Coal": 2.88,        # kg CO2 per unit
    
    # Diet (kg CO2 per day)
    "Heavy Meat Eater": 7.19,
    "Regular Meat Eater": 5.63,
    "Low Meat Eater": 4.67,
    "Pescatarian": 3.91,
    "Vegetarian": 3.81,
    "Vegan": 2.89,
    
    # Consumer habits (multipliers)
    "Clothing Spending": {
        "Very Low": 0.5,
        "Low": 0.75,
        "Average": 1.0,
        "High": 1.5,
        "Very High": 2.0
    },
    
    # Electronics (kg CO2 per device)
    "Electronics": 100,
    
    # Waste (kg CO2 per kg waste)
    "Waste": 0.5,
    "Zero Waste Efforts": {
        "None": 1.0,
        "Minimal": 0.9,
        "Moderate": 0.7,
        "Significant": 0.5,
        "Zero-waste lifestyle": 0.2
    }
}

st.header("Calculate Your Carbon Footprint")

if st.button("Calculate Carbon Footprint"):
    # Calculate transport emissions
    transport_emissions = 0
    
    # Daily commute (annualized)
    if transport_mode.startswith("Car"):
        if transport_mode == "Car (Electric)":
            # Electric cars use kWh/100km
            kwh_per_day = (daily_distance * fuel_efficiency) / 100
            transport_emissions += kwh_per_day * emission_factors[transport_mode] * 365
        else:
            # Gas/diesel cars use L/100km
            liters_per_day = (daily_distance * fuel_efficiency) / 100
            transport_emissions += daily_distance * emission_factors[transport_mode] * 365
    else:
        transport_emissions += daily_distance * emission_factors[transport_mode] * 365
    
    # Air travel
    transport_emissions += flight_short * emission_factors["Short Flight"]
    transport_emissions += flight_medium * emission_factors["Medium Flight"]
    transport_emissions += flight_long * emission_factors["Long Flight"]
    
    # Calculate home energy emissions (monthly * 12)
    energy_emissions = 0
    
    # Electricity with renewable adjustment
    energy_emissions += electricity_kwh * emission_factors["Electricity"] * (1 - renewable_percentage/100) * 12
    
    # Heating
    heating_factor = emission_factors["Electric Heating"] if heating_type == "Electric" else emission_factors[heating_type]
    energy_emissions += heating_usage * heating_factor * 12
    
    # AC (if applicable)
    if has_ac:
        # Assuming 1 kWh per hour of AC usage
        energy_emissions += ac_hours * 365 * emission_factors["Electricity"] * (1 - renewable_percentage/100)
    
    # Calculate diet emissions (daily * 365)
    diet_emissions = emission_factors[diet_type] * 365
    
    # Apply modifiers for diet choices
    local_modifier = 1 - (local_food / 200)  # Local food reduces by up to 50%
    organic_modifier = 1 - (organic_food / 250)  # Organic food reduces by up to 40%
    waste_modifier = 1 + (food_waste / 100)  # Food waste increases impact
    processed_modifier = 1 + (processed_food / 200)  # Processed food increases impact
    
    diet_emissions *= local_modifier * organic_modifier * waste_modifier * processed_modifier
    
    # Calculate consumption emissions
    consumption_emissions = 0
    
    # Clothing impact
    clothing_factor = emission_factors["Clothing Spending"][clothing_spending]
    consumption_emissions += clothing_factor * 500  # Base clothing footprint
    
    # Electronics
    consumption_emissions += electronics_yearly * emission_factors["Electronics"]
    
    # Adjust based on recycling and second-hand purchases
    recycling_modifier = 1 - (len(recycled_items) * 0.05)  # Each recycled category reduces impact by 5%
    secondhand_modifier = 1 - (second_hand / 200)  # Second-hand reduces impact by up to 50%
    
    consumption_emissions *= recycling_modifier * secondhand_modifier
    
    # Calculate waste emissions
    waste_emissions = waste_weekly * emission_factors["Waste"] * 52
    
    # Apply modifiers for waste management
    if composting:
        waste_emissions *= 0.8  # Composting reduces waste impact by 20%
    
    waste_emissions *= (1 - recycling_rate/200)  # Recycling reduces impact
    waste_emissions *= emission_factors["Zero Waste Efforts"][zero_waste]  # Zero waste efforts
    
    # Calculate total emissions
    total_emissions = transport_emissions + energy_emissions + diet_emissions + consumption_emissions + waste_emissions
    
    # Update session state
    st.session_state.total_emissions = total_emissions
    st.session_state.emissions_data['date'].append(datetime.now().strftime('%Y-%m-%d'))
    st.session_state.emissions_data['transport'].append(transport_emissions)
    st.session_state.emissions_data['home_energy'].append(energy_emissions)
    st.session_state.emissions_data['diet'].append(diet_emissions)
    st.session_state.emissions_data['consumption'].append(consumption_emissions)
    st.session_state.emissions_data['waste'].append(waste_emissions)
    st.session_state.emissions_data['total'].append(total_emissions)
    
    st.success(f"Calculation complete! Your annual carbon footprint is {total_emissions:.2f} kg CO2e")

# Display results if calculations have been made
if st.session_state.total_emissions > 0:
    st.header("Your Carbon Footprint Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create a DataFrame for the current emissions
        latest_data = {
            'Category': ['Transportation', 'Home Energy', 'Diet', 'Consumer Habits', 'Waste'],
            'Emissions (kg CO2e)': [
                st.session_state.emissions_data['transport'][-1],
                st.session_state.emissions_data['home_energy'][-1],
                st.session_state.emissions_data['diet'][-1],
                st.session_state.emissions_data['consumption'][-1],
                st.session_state.emissions_data['waste'][-1]
            ]
        }
        df = pd.DataFrame(latest_data)
        
        # Create pie chart
        fig = px.pie(
            df, 
            values='Emissions (kg CO2e)', 
            names='Category', 
            title='Breakdown of Your Carbon Footprint',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig)
        
    with col2:
        st.subheader("Footprint Summary")
        st.metric("Total Annual Emissions", f"{st.session_state.total_emissions:.2f} kg CO2e")
        
        # Calculate per capita comparison (using world average of 4,700 kg)
        world_average = 4700
        percentage_diff = ((st.session_state.total_emissions - world_average) / world_average) * 100
        
        if percentage_diff > 0:
            st.metric("Compared to World Average", f"{percentage_diff:.1f}% higher")
        else:
            st.metric("Compared to World Average", f"{abs(percentage_diff):.1f}% lower")
    
    # Show historical data if multiple calculations exist
    if len(st.session_state.emissions_data['date']) > 1:
        st.subheader("Your Emissions Over Time")
        
        history_df = pd.DataFrame({
            'Date': st.session_state.emissions_data['date'],
            'Total Emissions (kg CO2e)': st.session_state.emissions_data['total']
        })
        
        fig = px.line(
            history_df, 
            x='Date', 
            y='Total Emissions (kg CO2e)', 
            title='Carbon Footprint Trend',
            markers=True
        )
        st.plotly_chart(fig)

    # Recommendations
    st.header("Personalized Recommendations")
    
    # Get the highest emission category
    categories = ['transport', 'home_energy', 'diet', 'consumption', 'waste']
    emissions = [
        st.session_state.emissions_data[cat][-1] for cat in categories
    ]
    highest_category_index = emissions.index(max(emissions))
    highest_category = categories[highest_category_index]
    
    # Generic recommendations by category
    recommendations = {
        'transport': [
            "Consider carpooling or using public transportation more frequently",
            "If possible, work from home a few days a week to reduce commute emissions",
            "For short distances, consider walking or cycling instead of driving",
            "If you're in the market for a new vehicle, consider electric or hybrid options"
        ],
        'home_energy': [
            "Switch to LED light bulbs throughout your home",
            "Improve home insulation to reduce heating/cooling needs",
            "Consider investing in renewable energy sources like solar panels",
            "Unplug electronics when not in use to avoid phantom energy usage"
        ],
        'diet': [
            "Try to incorporate more plant-based meals into your diet",
            "Buy more locally produced and seasonal foods",
            "Plan meals to reduce food waste",
            "Compost food scraps instead of sending them to landfill"
        ],
        'consumption': [
            "Before buying new items, consider if you can repair, borrow, or buy second-hand",
            "Invest in quality items that will last longer, even if they cost more initially",
            "Recycle as much as possible and properly dispose of electronics",
            "Support companies with sustainable practices and certifications"
        ],
        'waste': [
            "Start composting food scraps and yard waste",
            "Switch to reusable alternatives for common disposable items",
            "Buy products with minimal or recyclable packaging",
            "Participate in local recycling programs and ensure you're recycling correctly"
        ]
    }
    
    # Display category-specific recommendations
    st.subheader(f"Focus Area: {highest_category.replace('_', ' ').title()}")
    st.write("Based on your inputs, this area contributes most to your carbon footprint.")
    
    for rec in recommendations[highest_category]:
        st.markdown(f"- {rec}")
    
    # General recommendations
    st.subheader("General Tips")
    st.markdown("""
    - Track your carbon footprint regularly using this calculator
    - Set specific reduction goals for the coming months
    - Share your sustainability journey with friends and family to inspire others
    - Stay informed about climate issues and support climate-friendly policies
    """)

    # Save data button
    if st.button("Download Your Carbon Footprint Data"):
        # Convert session state data to DataFrame
        full_df = pd.DataFrame(st.session_state.emissions_data)
        
        # Convert DataFrame to CSV
        csv = full_df.to_csv(index=False)
        
        # Create download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="carbon_footprint_data.csv",
            mime="text/csv"
        )

# Load global carbon emissions data
@st.cache_data
def load_emissions_data():
    try:
        csv_path = "d:/Christ/resume_builder-main/resume_builder-main/pdfs/Carbon_(CO2)_Emissions_by_Country.csv"
        df = pd.read_csv(csv_path)
        # Convert date to datetime and extract year
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        df['Year'] = df['Date'].dt.year
        return df
    except Exception as e:
        st.error(f"Error loading emissions data: {e}")
        return pd.DataFrame()

# Add a new tab for global emissions data after the main calculator
if st.session_state.total_emissions > 0:
    # Add global emissions comparison
    st.header("Global Emissions Comparison")
    
    # Load the emissions data
    emissions_df = load_emissions_data()
    
    if not emissions_df.empty:
        # User's country selection
        countries = sorted(emissions_df['Country'].unique())
        selected_country = st.selectbox("Select your country for comparison", countries)
        
        # Get the most recent data for the selected country
        country_data = emissions_df[emissions_df['Country'] == selected_country].sort_values('Year', ascending=False)
        
        if not country_data.empty:
            latest_year = country_data.iloc[0]['Year']
            latest_emissions_per_capita = country_data.iloc[0]['Metric Tons Per Capita'] * 1000  # Convert to kg
            
            col1, col2, col3 = st.columns(3)
            
            # Display user's emissions compared to country average
            with col1:
                st.metric("Your Annual Emissions", f"{st.session_state.total_emissions:.2f} kg CO2e")
            
            with col2:
                st.metric(f"{selected_country} Average ({latest_year})", f"{latest_emissions_per_capita:.2f} kg CO2e")
            
            with col3:
                percentage_diff = ((st.session_state.total_emissions - latest_emissions_per_capita) / latest_emissions_per_capita) * 100
                st.metric("Difference", f"{percentage_diff:.1f}% {'higher' if percentage_diff > 0 else 'lower'}")
            
            # Show historical emissions for the selected country
            st.subheader(f"Historical CO2 Emissions for {selected_country}")
            
            # Prepare data for chart
            chart_data = country_data.sort_values('Year')
            
            # Create line chart for emissions over time
            fig = px.line(
                chart_data, 
                x='Year', 
                y='Metric Tons Per Capita',
                title=f'Per Capita CO2 Emissions for {selected_country} (1990-2019)',
                labels={'Metric Tons Per Capita': 'Metric Tons CO2 per Person', 'Year': 'Year'},
                markers=True
            )
            st.plotly_chart(fig)
            
            # Add a regional comparison
            st.subheader("Regional Comparison")
            
            # Get the region of the selected country
            country_region = country_data.iloc[0]['Region']
            
            # Get the most recent data for all countries in the region
            region_data = emissions_df[
                (emissions_df['Region'] == country_region) & 
                (emissions_df['Year'] == latest_year)
            ].sort_values('Metric Tons Per Capita', ascending=False)
            
            # Create bar chart for regional comparison
            fig_region = px.bar(
                region_data,
                x='Country',
                y='Metric Tons Per Capita',
                title=f'CO2 Emissions in {country_region} ({latest_year})',
                labels={'Metric Tons Per Capita': 'Metric Tons CO2 per Person', 'Country': 'Country'},
                color='Metric Tons Per Capita',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_region.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_region)
            
            # Global rankings
            st.subheader("Global Rankings")
            
            # Get global rankings for the selected year
            global_data = emissions_df[emissions_df['Year'] == latest_year].sort_values('Metric Tons Per Capita', ascending=False)
            global_data = global_data.reset_index(drop=True)
            global_data.index = global_data.index + 1  # Start index at 1
            
            # Find the rank of the selected country
            country_rank = global_data[global_data['Country'] == selected_country].index[0]
            total_countries = len(global_data)
            
            st.write(f"{selected_country} ranks #{country_rank} out of {total_countries} countries in per capita CO2 emissions.")
            
            # Show top 10 and the position of the selected country
            if country_rank <= 10:
                st.write("Top 10 countries by per capita emissions:")
                st.dataframe(global_data[['Country', 'Region', 'Metric Tons Per Capita']].head(10))
            else:
                st.write("Top 5 countries by per capita emissions:")
                st.dataframe(global_data[['Country', 'Region', 'Metric Tons Per Capita']].head(5))
                
                # Show a few countries around the selected country
                lower_bound = max(1, country_rank - 2)
                upper_bound = min(total_countries, country_rank + 2)
                st.write(f"Countries around {selected_country}'s rank:")
                st.dataframe(global_data.loc[lower_bound:upper_bound, ['Country', 'Region', 'Metric Tons Per Capita']])

    # Add global emission trends
    st.header("Global Emission Trends")
    
    if not emissions_df.empty:
        # Aggregate data by year and region
        yearly_region_data = emissions_df.groupby(['Year', 'Region'])['Kilotons of Co2'].sum().reset_index()
        
        # Create line chart for emissions by region over time
        fig_global = px.line(
            yearly_region_data,
            x='Year',
            y='Kilotons of Co2',
            color='Region',
            title='Global CO2 Emissions by Region (1990-2019)',
            labels={'Kilotons of Co2': 'Kilotons of CO2', 'Year': 'Year'},
            line_shape='spline'
        )
        st.plotly_chart(fig_global)
        
        # Add interesting insights
        st.subheader("Global Emission Insights")
        
        # Calculate growth rates
        total_by_year = emissions_df.groupby('Year')['Kilotons of Co2'].sum()
        earliest_year = total_by_year.index.min()
        latest_year = total_by_year.index.max()
        total_growth = (total_by_year.loc[latest_year] / total_by_year.loc[earliest_year] - 1) * 100
        
        st.write(f"Global CO2 emissions have grown by {total_growth:.1f}% from {earliest_year} to {latest_year}.")
        
        # Find fastest growing and declining regions
        region_growth = yearly_region_data.pivot(index='Year', columns='Region', values='Kilotons of Co2')
        region_growth_pct = (region_growth.loc[latest_year] / region_growth.loc[earliest_year] - 1) * 100
        fastest_growing = region_growth_pct.idxmax()
        fastest_declining = region_growth_pct.idxmin()
        
        st.write(f"The fastest growing region is {fastest_growing} with {region_growth_pct[fastest_growing]:.1f}% growth.")
        if region_growth_pct[fastest_declining] < 0:
            st.write(f"The fastest declining region is {fastest_declining} with {abs(region_growth_pct[fastest_declining]):.1f}% reduction.")

# Add a footer with information
st.markdown("---")
st.markdown("""
**About This Calculator**

This Carbon Footprint Calculator provides an estimate of your greenhouse gas emissions based on your lifestyle choices.
The calculations are based on average emission factors and may vary depending on your specific circumstances.
Regular tracking can help you identify areas for improvement and monitor your progress toward a more sustainable lifestyle.
""")
