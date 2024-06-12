import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go

# Load the dataset
file_path = r"C:\Users\Eric_Rash\OneDrive - Baylor University\AppliedPerformancProjects\BW_061124.csv"  # Replace with your file path
data = pd.read_csv(file_path)

# Convert the DATE column to datetime format
data['DATE'] = pd.to_datetime(data['DATE'])

# Extract date from the DATE column
data['Date'] = data['DATE'].dt.date

# Add YearMonth column
data['YearMonth'] = data['DATE'].dt.to_period('M')

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Body Weight Analysis by Position"),
    dcc.Dropdown(
        id='position-dropdown',
        options=[{'label': pos, 'value': pos} for pos in data['POS'].unique()],
        value='DB'
    ),
    dcc.Graph(id='weight-graph')
])

@app.callback(
    Output('weight-graph', 'figure'),
    [Input('position-dropdown', 'value')]
)
def update_graph(selected_position):
    # Filter data for the selected position
    pos_data = data[data['POS'] == selected_position].copy()

    # Calculate average weight for each day
    avg_weight_by_day = pos_data.groupby(['Date'])['WEIGHT'].mean().reset_index()

    # Calculate average weight for each month
    avg_weight_by_month = pos_data.groupby(['YearMonth'])['WEIGHT'].mean().reset_index()

    # Convert YearMonth back to datetime for plotting
    avg_weight_by_month['YearMonth'] = avg_weight_by_month['YearMonth'].dt.to_timestamp()

    # Create the figure
    fig = go.Figure()

    # Plot the average weight for each day with breaks at the end of each month
    for i, month in enumerate(avg_weight_by_month['YearMonth']):
        if i < len(avg_weight_by_month['YearMonth']) - 1:
            mask = (pd.to_datetime(avg_weight_by_day['Date']) >= month) & (pd.to_datetime(avg_weight_by_day['Date']) < avg_weight_by_month['YearMonth'][i + 1])
        else:
            mask = pd.to_datetime(avg_weight_by_day['Date']) >= month
        
        monthly_data = avg_weight_by_day.loc[mask]
        fig.add_trace(go.Scatter(x=monthly_data['Date'], y=monthly_data['WEIGHT'],
                                 mode='lines+markers', name=f'Daily Avg Weight ({month.strftime("%b %Y")})', line=dict(color='teal'), showlegend=False))

    # Plot the average weight for each month as separate segments
    for date, weight in zip(avg_weight_by_month['YearMonth'], avg_weight_by_month['WEIGHT']):
        fig.add_trace(go.Scatter(x=[date, date + pd.DateOffset(days=30)], y=[weight, weight],
                            mode='lines+text', line=dict(color='navy', width=2), 
                            name=f'Monthly Avg Weight ({date.strftime("%b %Y")})',
                            # text=[f'{weight:.2f}', f'{weight:.2f}'],  # Add data labels
                            # textposition='bottom center',  # Position the text
                            # textfont=dict(color='darkgoldenrod', family='Arial Black', size=8)  # Set the color, font, and size of the text
                            ))

    # Update the layout to list each individual month on the x-axis
    fig.update_layout(
        title=f'Body Weight per Month for {selected_position} Position',
        xaxis_title='Date',
        yaxis_title='Weight (lbs)',
        xaxis=dict(
            tickmode='array',
            tickvals=avg_weight_by_month['YearMonth'],
            ticktext=avg_weight_by_month['YearMonth'].dt.strftime('%b %y'),
            tickangle=-45  # Rotate the x-axis labels by 45 degrees
        ),
        legend_title_text='',
        legend=dict(
            x=0.01,
            y=0.99,
            traceorder='normal',
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        ),
        showlegend=False
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)