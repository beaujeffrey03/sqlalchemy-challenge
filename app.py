# Import Flask
from flask import Flask

# Create an app
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f'Welcome to the Hawaii Weather API! \n'
        f'<br/>'
        f'<br/>'
        f'Here are the available routes: \n'
        f'<br/>'
        f'<br/>'
        f'/api/v1.0/precipitation <br/>'
        f'/api/v1.0/stations <br/>'
        f'/api/v1.0/tobs <br/>'
        f'/api/v1.0/<start> <br/>'
        f'/api/v1.0/<start>/<end> <br/>'
    )

# Make routes
@app.route('/api/v1.0/precipitation')
def precipitation():
    return (
        
    )

@app.route("/api/v1.0/stations")
def stations():
    return (
        
    )

@app.route('/api/v1.0/tobs')
def tobs():
    return (
        
    )

@app.route('/api/v1.0/<start>')
def start():
    return (
        
    )

@app.route('/api/v1.0/<start>/<end>')
def start_end():
    return (
        
    )

if __name__ == "__main__":
    app.run(debug=True)