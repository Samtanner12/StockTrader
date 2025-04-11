import plotly.graph_objects as go

def plot_candlestick(data, title="Stock Data"):
    # Flatten multi-level columns
    data.columns = data.columns.get_level_values('Price')

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Candlestick'
    )])

    # Add volume bars
    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        name='Volume',
        marker_color='blue',
        yaxis='y2'
    ))

    # Update layout to make the graph more readable
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=True,  # Add range slider for scroll
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False,
        ),
        template="plotly_dark",  # Use a dark theme for better readability
        xaxis_rangeslider_thickness=0.05,  # Adjust range slider thickness
        height=600,  # Adjust height for better readability
        width=1000  # Adjust width for better readability
    )

    # Show the interactive plot
    fig.show()
