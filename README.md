# Running Decay Curve Calculator

This web application helps runners visualize and analyze their performance across different distances using the concept of fatigue curves. Based on insights from [@johngetstrong](https://twitter.com/johngetstrong), this tool helps you understand your running profile and make informed training decisions.

## Features

- Input your personal best times for distances from 400m to Half Marathon
- Visualize your performance curve
- Adjust the fatigue curve percentage to match your actual performance
- Get personalized analysis and training recommendations
- Interactive visualization of your times vs the theoretical decay curve

## Setup

1. Make sure you have Python 3.7+ installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Navigate to the application directory:
   ```bash
   cd running_decay_app
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. The application will open in your default web browser

## Usage

1. Enter your best times for each distance in the format specified (mm:ss or h:mm:ss)
2. Use the slider to adjust the fatigue curve percentage
3. The graph will update automatically to show your actual times vs the theoretical curve
4. Read the analysis section for insights about your running profile

## About Fatigue Curves

- A fatigue curve shows how your speed decreases as distance increases
- Sprint/middle-distance runners typically show ~10% fatigue curves
- Well-trained endurance runners can achieve fatigue curves as low as 4%
- Your curve can help you decide whether to focus on:
  1. Lifting the entire curve (getting faster across all distances)
  2. Bending the curve through specialized training

## Credits

Created based on insights from [@johngetstrong](https://twitter.com/johngetstrong) 