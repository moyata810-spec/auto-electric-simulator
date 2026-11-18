from flask import Flask, render_template

app = Flask(__name__)

# ዋናው የዳሽቦርድ ገጽ (Main Hub Dashboard)
@app.route('/')
def home():
    return render_template('home.html')

# 1. የመብራት ሲስተም ገጽ (Lighting System)
@app.route('/lighting')
def lighting():
    return render_template('lighting.html')

# 2. የስታርቲንግ ሲስተም ገጽ (Starting System)
@app.route('/starter')
def starter():
    return render_template('starter.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
