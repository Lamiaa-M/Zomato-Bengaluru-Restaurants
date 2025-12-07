# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Zomato Dashboard")

@st.cache_data
def load_data(path="ZomatoCleanedData.csv"):
    df = pd.read_csv(path)
    for col in ["online_order", "table_booking"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"Yes":"Yes","No":"No","TRUE":"Yes","False":"False","true":"Yes","false":"False"})
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    if "votes" in df.columns:
        df["votes"] = pd.to_numeric(df["votes"], errors="coerce")
    return df

df = load_data()

# Sidebar navigation
st.sidebar.title("Navigator")
questions = [
    "Locations Analysis",
    "Restaurant Types Analysis",
    "Liked Dishes and Online Orders",
    "Cost, Cuisine, and Customer Satisfaction",
    "Most Popular Cuisine & Pricing Dynamics",
    "Restaurant Operations"]
choice = st.sidebar.selectbox(
    "Category",
    list(range(1, len(questions)+1)),
    format_func=lambda i: f"{i}. {questions[i-1]}"
)
bar_colors: list[str] = ['#FEFECC', '#F3BDA1', '#687980', '#02475E', '#FFE7D1', '#F6C89F', '#4B8E8D', '#396362']

st.title("Zomato Bengaluru Restaurants: A Data-Driven Analysis")
st.markdown("      Mid Project After Cleansing Epsilon AI")
st.markdown("Presented by :Lamiaa Mohamed Mahmoud")

# Common filters (optional)
st.sidebar.markdown("### Filters (optional)")
if "location" in df.columns:
    locs = ["All"] + sorted(df["location"].dropna().unique().tolist())
    sel_loc = st.sidebar.selectbox("Location", locs)
else:
    sel_loc = "All"

if "restaurant_type" in df.columns:
    types = ["All"] + sorted(df["restaurant_type"].dropna().unique().tolist())
    sel_rest_type = st.sidebar.selectbox("Restaurant type", types)
else:
    sel_rest_type = "All"

# Apply basic filters
df_view = df.copy()
if sel_loc != "All":
    df_view = df_view[df_view["location"] == sel_loc]
if sel_rest_type != "All":
    df_view = df_view[df_view["restaurant_type"] == sel_rest_type]

# Utility safe plotting
def safe_plot(fig, width_type='stretch'):
    st.plotly_chart(fig, use_container_width=True)

# 1
if choice == 1:
    
    if "location" not in df_view.columns:
        st.write("Column `location` not found in dataset.")
    else:
       counts = df_view['location'].value_counts().head(20)
        
        # Your custom colors
       colors_for_bars = [bar_colors[i % len(bar_colors)] for i in range(len(counts))]
        
       fig = px.bar(
            x=counts.index, 
            y=counts.values,
            labels={'x':'Location','y':'Number of Restaurants'},
            title="Top 20 Locations with Most Restaurants",
        )
        
        # Apply custom colors
       fig.update_traces(
            marker_color=colors_for_bars,
            textposition='outside',
            textfont=dict(color='#02475E', size=12),
            cliponaxis=False
        )
        
       fig.update_layout(xaxis_tickangle=45)
       safe_plot(fig)
        
        
    if "location" not in df_view.columns:
        st.write("Column `location` not found in dataset.")
    else:
        counts = df_view['location'].value_counts().tail(20)
        colors_for_bars = [bar_colors[i % len(bar_colors)] for i in range(len(counts))]

        fig = px.bar(
            x=counts.index, y=counts.values,
            labels={'x':'Location','y':'Number of Restaurants'},
            title="Bottom 20 Locations with Least Restaurants",
        )
        fig.update_traces(
            marker_color=colors_for_bars,
            textposition='outside',
            textfont=dict(color='#02475E', size=12),
            cliponaxis=False
        )
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)

# 2
if choice == 2:
    if "restaurant_type" not in df_view.columns:
        st.write("Column `restaurant_type` not found in dataset.")
    else:
        counts = df_view['restaurant_type'].value_counts().head(20)
        colors_for_bars = [bar_colors[i % len(bar_colors)] for i in range(len(counts))]

        fig = px.bar(
            x=counts.index, y=counts.values,
            labels={'x':'Restaurant Type','y':'Count'},
            title="Most Common Restaurant Types (Top 20)",
        )
        fig.update_traces(
            marker_color=colors_for_bars,
            textposition='outside',
            textfont=dict(color='#02475E', size=12),
            cliponaxis=False
        )
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)


    if not {"location","restaurant_type"}.issubset(df_view.columns):
        st.write("Required columns `location` and `restaurant_type` not found.")
    else:
     restaurant_type_per_location = df_view.groupby(['location', 'restaurant_type']).size().reset_index(name='count')
    # Get most common type per location
    most_common_type_per_location = restaurant_type_per_location.sort_values(
        ['location', 'count'], ascending=[True, False]
    ).groupby('location').first().reset_index()
    # Take top 15 locations
    top_15 = most_common_type_per_location.head(15)
    # Sunburst chart
    fig1 = px.sunburst(
        top_15,
        path=['location', 'restaurant_type'],
        values='count',
        title="Top 15 Locations and Their Most Common Restaurant Type",
        color='count',
        color_continuous_scale=bar_colors
    )
    
    fig1.update_layout(width=1000, height=800)
    

    if not {"location","restaurant_type"}.issubset(df_view.columns):

        st.write("Column `restaurant_type` not found in dataset.")
    else:
     restaurant_type_per_location = df.groupby(['restaurant_type', 'location']).size().reset_index(name='count')

    total_per_type = df.groupby('restaurant_type').size().reset_index(name='total_count')

    top_10_types = total_per_type.sort_values('total_count', ascending=False).head(10)['restaurant_type']

    filtered = restaurant_type_per_location[restaurant_type_per_location['restaurant_type'].isin(top_10_types)]

    most_common_location_per_type = filtered.sort_values(['restaurant_type', 'count'], ascending=[True, False]).groupby('restaurant_type').first().reset_index()

    fig2 = px.sunburst(
    most_common_location_per_type,
    path=['restaurant_type', 'location'],  
    values='count',
    title="Top 10 Restaurant Types and Their Most Common Location",
    color='count',
    color_continuous_scale=bar_colors
    )
  
    fig2.update_layout(width=1000, height=800)
    
    col1, col2 = st.columns(2)
    with col1:
        safe_plot(fig1)
    with col2:
        safe_plot(fig2)
# 3
if choice == 3:
   
    if "location" not in df_view.columns:
        st.write("Required columns `location` not found.")

    else:
      filtered_dishes = df[df['dish_liked'] != 'No Review']
     # Top 10 liked dishes
      top_dishes = filtered_dishes['dish_liked'].value_counts().head(10)
      top_dishes_df = top_dishes.reset_index()
      top_dishes_df.columns = ['dish_liked', 'count']

      # Custom color palette
      colors = ['#FEFECC', '#F3BDA1', '#02475E', '#396362', '#687980', '#02475E', '#02475E', '#F3BDA1']

      # Treemap
      fig = px.treemap(
      top_dishes_df,
      path=['dish_liked'],       
      values='count',  
      title="Top 10 Liked Dishes",
      color='count', 
      color_continuous_scale=colors
     )

     # Show both label and value
      fig.data[0].textinfo = 'label+value'

     # Display in Streamlit
    safe_plot(fig)
    
    
    online_rating = df.groupby('online_order')['rating'].mean().reset_index()
    fig = px.pie(
    online_rating,
    names='online_order',
    values='rating',
    color='online_order',
    title="Relationship between online_order and rating",
    color_discrete_map={
        "True": '#02475E',
        "False": '#F3BDA1'
    },
    hole=0.4
    )

    fig.update_traces(
    textinfo='label+percent',   
    textfont_size=20,   
    textposition='inside'
    )

    fig.update_layout(width=800, height=600)
    safe_plot(fig)
     
if choice == 4:
    
    cuisine_counts = df['cuisines'].value_counts().head(20)
    colors_for_bars = [bar_colors[i % len(bar_colors)] for i in range(len(cuisine_counts))]

    fig = px.bar(
    cuisine_counts,
    x=cuisine_counts.index,
    y=cuisine_counts.values,
    title="Top 20 Most Common Cuisines",
    labels={'x': 'Cuisine', 'y': 'Count'},
    text=cuisine_counts.values
    )

    fig.update_traces(
            marker_color=colors_for_bars,
            textposition='outside',
            textfont=dict(color='#02475E', size=12),
            cliponaxis=False
        )

    fig.update_layout(
    xaxis_tickangle=45,
    width=1000,
    height=600
     )

    safe_plot(fig)
    
    
    fig = px.scatter(
    df,
    x='approximately_cost_for_two',
    y='rating',
    title='Cost for Two vs Rating',
    opacity=0.7,
    trendline='ols',
    labels={'approximately_cost_for_two': 'Cost for Two'},
    color='rating',
    color_continuous_scale='mint'  
    )

    safe_plot(fig)

if choice == 5:
    top_cuisine_per_location = df.groupby(['location', 'cuisines']).size().reset_index(name='count')
    top_cuisine_per_location = top_cuisine_per_location.sort_values(['location', 'count'], ascending=[True, False]).groupby('location').first().reset_index()
    top_10_locations = top_cuisine_per_location.head(10)

    fig = px.treemap(
    top_10_locations,
    path=['location', 'cuisines'],  
    values='count',
    title="Top 10 Locations and Their Most Popular Cuisine",
    color='count',
    color_continuous_scale=bar_colors
    )
    fig.data[0].textinfo = 'label+value'
    fig.update_layout(xaxis_tickangle=45)
    safe_plot(fig)
    
    
    
    fig = px.histogram(
    df,
    x='approximately_cost_for_two',
    nbins=40,
    title='Distribution of Cost for Two',
    labels={'approximately_cost_for_two': 'Cost for Two'},
    color_discrete_sequence=['#F3BDA1'],
    text_auto=True,
    marginal='box',
    )

    fig.update_traces(
    selector=dict(type='histogram'),
    textposition='outside',
    textfont=dict(color='#02475E', size=12),
    cliponaxis=False
    )
    fig.update_traces(
    selector=dict(type='box'),
    marker_color='#02475E', 
    )
 
    fig.update_layout(xaxis_tickangle=45)
    safe_plot(fig)

if choice == 6:
    
       colors = ['#02475E', '#F3BDA1','#FEFECC', '#687980', '#FFE7D1', '#F6C89F', '#4B8E8D', '#396362']

       listed_type_counts = df['listed_in_type'].value_counts()

       fig = px.pie(
       names=listed_type_counts.index,
       values=listed_type_counts.values,
       title="Distribution of Restaurant Listing Types",
       color_discrete_sequence=colors,
       hole=0.3  
       )

       fig.update_traces(textinfo='label+percent', textposition='inside')

       fig.update_layout(
       width=1000,
       height=800, 
       )

       safe_plot(fig)
       
       type_rating = df.groupby('listed_in_type')['rating'].mean().sort_values(ascending=False)
       fig = px.pie(
       names=type_rating.index,
       values=type_rating.values,
       title="Distribution of Restaurant Listing Types",
       color_discrete_sequence=colors,
       hole=0.3  
       )
       fig.update_traces(textinfo='label+percent', textposition='inside')

       fig.update_layout(
       width=1000,
       height=800,
       )
       safe_plot(fig)





# Footer
st.sidebar.markdown("---")


