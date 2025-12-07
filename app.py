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
            df[col] = df[col].astype(str).str.strip().replace({"Yes":"Yes","No":"No","TRUE":"Yes","False":"No","true":"Yes","false":"No"})
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
    "Q4 — Top 15 Locations and Their Most Common Restaurant Type",
    "Q5 — Top 10 Restaurant Types and Their Most Common Location",
    "Q6 — Relationship: Online Order vs Rating (mean)",
    "Q7 — Relationship: Cost for Two vs Rating",
    "Q8 — Most Common Cuisines / Popular Foods",
    "Q9 — Top 10 Liked Dishes",
    "Q10 — Top 10 Locations and Their Most Popular Cuisine",
    "Q11 — Distribution of Cost for Two",
    "Q12 — Most Common 'Listed In' Type",
    "Q13 — Ratings vs Restaurant Listing Type (mean)",
    "Q14 — Restaurants Offering Online Ordering (pie)",
    "Q15 — Distribution of Ratings (histogram)",
    "Q16 — Restaurants Offering Table Booking (pie)",
    "Q17 — Top 20 Menu Items",
    "Q18 — Average Cost for Two by Cuisine",
    "Q19 — Votes vs Rating (scatter)",
    "Q20 — Top Locations by Number of Popular Menu Items"
]
choice = st.sidebar.selectbox("Select question", list(range(1,21)), format_func=lambda i: f"{i}. {questions[i-1]}")
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
def safe_plot(fig):
    st.plotly_chart(fig, use_container_width=True)

# Q1
if choice == 1:
    
    st.header("Top 20 Locations with Most Restaurants")
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
        
        
    st.header("Bottom 20 Locations with Most Restaurants")
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

# Q2
if choice == 2:
    st.header("Most Common Restaurant Types")
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


    st.header("Top 15 Locations and Their Most Common Restaurant Type")
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
    
    # Custom color palette
    bar_colors = ['#FEFECC', '#F3BDA1', '#687980', '#02475E', '#FFE7D1', '#F6C89F', '#4B8E8D', '#396362']
    
    # Sunburst chart
    fig = px.sunburst(
        top_15,
        path=['location', 'restaurant_type'],
        values='count',
        title="Top 15 Locations and Their Most Common Restaurant Type",
        color='count',
        color_continuous_scale=bar_colors
    )
    
    fig.update_layout(width=1000, height=800)
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
# Q3
if choice == 3:
   
    st.header("Top 10 Liked Dishes")
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
      
# Q4
if choice == 4:
    
    st.header(questions[4])
    if not {"restaurant_type","location"}.issubset(df_view.columns):
        st.write("Required columns `restaurant_type` and `location` not found.")
    else:
        grp = df_view.groupby(['restaurant_type','location']).size().reset_index(name='count')
        top10_types = df_view['restaurant_type'].value_counts().head(10).index.tolist()
        grp = grp[grp['restaurant_type'].isin(top10_types)]
        top_locs_for_types = grp.sort_values(['restaurant_type','count'], ascending=[True,False]).groupby('restaurant_type').first().reset_index()
        fig = px.bar(top_locs_for_types, x='restaurant_type', y='count', color='location',
                     labels={'count':'Count','restaurant_type':'Restaurant Type'},
                     title="Top 10 Restaurant Types & Their Most Common Location")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)
        st.dataframe(top_locs_for_types)
# Q5
if choice == 5:
    st.header(questions[4])
    if not {"restaurant_type","location"}.issubset(df_view.columns):
        st.write("Required columns `restaurant_type` and `location` not found.")
    else:
        grp = df_view.groupby(['restaurant_type','location']).size().reset_index(name='count')
        top10_types = df_view['restaurant_type'].value_counts().head(10).index.tolist()
        grp = grp[grp['restaurant_type'].isin(top10_types)]
        top_locs_for_types = grp.sort_values(['restaurant_type','count'], ascending=[True,False]).groupby('restaurant_type').first().reset_index()
        fig = px.bar(top_locs_for_types, x='restaurant_type', y='count', color='location',
                     labels={'count':'Count','restaurant_type':'Restaurant Type'},
                     title="Top 10 Restaurant Types & Their Most Common Location")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)
        st.dataframe(top_locs_for_types)

# Q6
if choice == 6:
    st.header(questions[5])
    if "online_order" not in df_view.columns or "rating" not in df_view.columns:
        st.write("Required columns `online_order` and `rating` not found.")
    else:
        avg = df_view.groupby('online_order')['rating'].mean().reset_index()
        fig = px.bar(avg, x='online_order', y='rating', labels={'rating':'Average Rating','online_order':'Online Order'},
                     title="Average Rating by Online Order Availability")
        safe_plot(fig)
        st.dataframe(avg)

# Q7
if choice == 7:
    st.header(questions[6])
    if "approximately_cost_for_two" not in df_view.columns or "rating" not in df_view.columns:
        st.write("Required columns `approximately_cost_for_two` and `rating` not found.")
    else:
        # ensure numeric
        df_view['approximately_cost_for_two'] = pd.to_numeric(df_view['approximately_cost_for_two'], errors='coerce')
        grp = df_view.groupby('approximately_cost_for_two')['rating'].mean().reset_index()
        fig = px.scatter(grp, x='approximately_cost_for_two', y='rating',
                         labels={'approximately_cost_for_two':'Cost for Two','rating':'Average Rating'},
                         title="Average Rating vs Cost for Two")
        safe_plot(fig)
        st.dataframe(grp.head(50))

# Q8
if choice == 8:
    st.header(questions[7])
    if "cuisines" not in df_view.columns:
        st.write("Column `cuisines` not found.")
    else:
        # cuisines often comma separated
        cuisines_series = df_view['cuisines'].dropna().astype(str).str.split(',').explode().str.strip()
        counts = cuisines_series.value_counts().head(30)
        fig = px.bar(x=counts.index, y=counts.values, labels={'x':'Cuisine','y':'Count'}, title="Most Common Cuisines")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)

# Q9
if choice == 9:
    st.header(questions[8])
    if "dish_liked" not in df_view.columns:
        st.write("Column `dish_liked` not found.")
    else:
        dishes = df_view[df_view['dish_liked'].notna() & (df_view['dish_liked']!='No Review')]['dish_liked'].astype(str).str.split(',').explode().str.strip()
        counts = dishes.value_counts().head(10)
        fig = px.bar(x=counts.index, y=counts.values, labels={'x':'Dish','y':'Count'}, title="Top 10 Liked Dishes")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)

# Q10
if choice == 10:
    st.header(questions[9])
    if not {"location","cuisines"}.issubset(df_view.columns):
        st.write("Required columns `location` and `cuisines` not found.")
    else:
        # explode cuisines and compute top cuisine per location
        exploded = df_view[['location','cuisines']].dropna()
        exploded = exploded.assign(cuisine=exploded['cuisines'].str.split(',')).explode('cuisine')
        exploded['cuisine'] = exploded['cuisine'].str.strip()
        grp = exploded.groupby(['location','cuisine']).size().reset_index(name='count')
        top10_locs = df_view['location'].value_counts().head(10).index.tolist()
        grp = grp[grp['location'].isin(top10_locs)]
        top_cuisine_per_loc = grp.sort_values(['location','count'], ascending=[True,False]).groupby('location').first().reset_index()
        fig = px.bar(top_cuisine_per_loc, x='location', y='count', color='cuisine',
                     labels={'count':'Count','location':'Location'}, title="Top 10 Locations & Their Most Popular Cuisine")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)
        st.dataframe(top_cuisine_per_loc)

# Q11
if choice == 11:
    st.header(questions[10])
    if "approximately_cost_for_two" not in df_view.columns:
        st.write("Column `approximately_cost_for_two` not found.")
    else:
        df_view['approximately_cost_for_two'] = pd.to_numeric(df_view['approximately_cost_for_two'], errors='coerce')
        fig = px.histogram(df_view, x='approximately_cost_for_two', nbins=30, labels={'approximately_cost_for_two':'Cost for Two'}, title="Distribution of Cost for Two")
        safe_plot(fig)

# Q12
if choice == 12:
    st.header(questions[11])
    if "listed_in_type" not in df_view.columns:
        st.write("Column `listed_in_type` not found.")
    else:
        counts = df_view['listed_in_type'].value_counts().head(20)
        fig = px.bar(x=counts.index, y=counts.values, labels={'x':'Listed In Type','y':'Count'}, title="Most Common Listed In Type")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)

# Q13
if choice == 13:
    st.header(questions[12])
    if not {"listed_in_type","rating"}.issubset(df_view.columns):
        st.write("Required columns `listed_in_type` and `rating` not found.")
    else:
        grp = df_view.groupby('listed_in_type')['rating'].mean().reset_index().sort_values('rating', ascending=False)
        fig = px.bar(grp, x='listed_in_type', y='rating', labels={'rating':'Average Rating','listed_in_type':'Listed In Type'}, title="Average Rating by Listing Type")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)
        st.dataframe(grp)

# Q14
if choice == 14:
    st.header(questions[13])
    if "online_order" not in df_view.columns:
        st.write("Column `online_order` not found.")
    else:
        counts = df_view['online_order'].value_counts()
        fig = px.pie(names=counts.index, values=counts.values, title="Restaurants Offering Online Ordering", hole=0.35)
        fig.update_traces(textinfo='label+percent', textposition='inside')
        safe_plot(fig)

# Q15
if choice == 15:
    st.header(questions[14])
    if "rating" not in df_view.columns:
        st.write("Column `rating` not found.")
    else:
        fig = px.histogram(df_view, x='rating', nbins=20, labels={'rating':'Rating'}, title="Distribution of Ratings")
        safe_plot(fig)

# Q16
if choice == 16:
    st.header(questions[15])
    if "table_booking" not in df_view.columns:
        st.write("Column `table_booking` not found.")
    else:
        counts = df_view['table_booking'].value_counts()
        fig = px.pie(names=counts.index, values=counts.values, title="Restaurants Offering Table Booking", hole=0.35)
        fig.update_traces(textinfo='label+percent', textposition='inside')
        safe_plot(fig)

# Q17
if choice == 17:
    st.header(questions[16])
    if "menu_items" not in df_view.columns:
        st.write("Column `menu_items` not found.")
    else:
        menu = df_view[df_view['menu_items'].notna() & (df_view['menu_items']!='[]')]['menu_items'].astype(str).str.split(',').explode().str.strip()
        counts = menu.value_counts().head(20)
        fig = px.bar(x=counts.index, y=counts.values, labels={'x':'Menu Item','y':'Count'}, title="Top 20 Menu Items")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)

# Q18
if choice == 18:
    st.header(questions[17])
    if "cuisines" not in df_view.columns or "approximately_cost_for_two" not in df_view.columns:
        st.write("Required columns `cuisines` and `approximately_cost_for_two` not found.")
    else:
        exploded = df_view[['cuisines','approximately_cost_for_two']].dropna()
        exploded = exploded.assign(cuisine=exploded['cuisines'].str.split(',')).explode('cuisine')
        exploded['cuisine'] = exploded['cuisine'].str.strip()
        exploded['approximately_cost_for_two'] = pd.to_numeric(exploded['approximately_cost_for_two'], errors='coerce')
        grp = exploded.groupby('cuisine')['approximately_cost_for_two'].mean().reset_index().sort_values('approximately_cost_for_two', ascending=False).head(30)
        fig = px.bar(grp, x='cuisine', y='approximately_cost_for_two', labels={'approximately_cost_for_two':'Avg Cost for Two','cuisine':'Cuisine'}, title="Average Cost for Two by Cuisine (Top 30)")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)
        st.dataframe(grp)

# Q19
if choice == 19:
    st.header(questions[18])
    if not {"votes","rating"}.issubset(df_view.columns):
        st.write("Required columns `votes` and `rating` not found.")
    else:
        df_vr = df_view.dropna(subset=['votes','rating'])
        fig = px.scatter(df_vr, x='votes', y='rating', labels={'votes':'Votes','rating':'Rating'}, title="Votes vs Rating (scatter)")
        safe_plot(fig)

# Q20
if choice == 20:
    st.header(questions[19])
    # heuristic: count number of "popular" menu items per location
    if not {"location","menu_items"}.issubset(df_view.columns):
        st.write("Required columns `location` and `menu_items` not found.")
    else:
        menu = df_view[df_view['menu_items'].notna() & (df_view['menu_items']!='[]')][['location','menu_items']].copy()
        menu = menu.assign(menu_item=menu['menu_items'].str.split(',')).explode('menu_item')
        menu['menu_item'] = menu['menu_item'].str.strip()
        # consider "popular" as items appearing more than once overall
        popular_items = menu['menu_item'].value_counts().head(200).index.tolist()
        menu = menu[menu['menu_item'].isin(popular_items)]
        loc_counts = menu.groupby('location')['menu_item'].nunique().sort_values(ascending=False).head(20)
        fig = px.bar(x=loc_counts.index, y=loc_counts.values, labels={'x':'Location','y':'Number of Popular Menu Items'}, title="Top Locations by # of Popular Menu Items")
        fig.update_layout(xaxis_tickangle=45)
        safe_plot(fig)
        st.dataframe(loc_counts)

# Footer
st.sidebar.markdown("---")

