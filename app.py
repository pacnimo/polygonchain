from flask import Flask, render_template
import json
import plotly
import plotly.graph_objs as go

app = Flask(__name__)

@app.route('/')
def index():
    with open("swap_counts.json", "r") as f:
        swap_counts = json.load(f)
    
    # Extract data for the plot
    pairs = list(swap_counts.keys())
    counts = list(swap_counts.values())

    # Create a bar chart
    data = [
        go.Bar(
            x=pairs,
            y=counts
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('index.html', graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)

