import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

st.set_page_config(page_title="Running Decay Curve Calculator", layout="wide")

st.title("Running Decay Curve Calculator")

st.markdown("""
### Understanding Your Running Performance Curve

This tool helps you visualize your running performance across different distances and calculate your personal fatigue curve. 
The fatigue curve shows how your speed decreases as distance increases.

As noted by [@johngetstrong](https://twitter.com/johngetstrong):
- Sprint/middle-distance runners typically show ~10% fatigue curves
- Well-trained endurance runners can achieve fatigue curves as low as 4%
- Your fatigue curve can indicate whether to focus on:
  1. Lifting the entire curve (getting faster across all distances)
  2. Bending the curve through specialized training

Enter your times below to see where you stand!
""")

# Input columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("Enter Your Times")
    track_400 = st.text_input("400m time (mm:ss)", "1:02")
    track_800 = st.text_input("800m time (mm:ss)", "2:25")
    track_1600 = st.text_input("1600m time (mm:ss)", "4:57")
    time_5k = st.text_input("5K time (mm:ss or h:mm:ss)", "17:20")

with col2:
    st.subheader(" ")  # For alignment
    time_10k = st.text_input("10K time (h:mm:ss)", "39:16")
    time_14k = st.text_input("14K time (h:mm:ss)", "55:16")
    time_hm = st.text_input("Half Marathon time (h:mm:ss)", "1:24:04")

# Decay rate slider
decay_percent = st.slider(
    "Fatigue curve percentage (higher = more fatigue between distances)",
    min_value=0.0,
    max_value=20.0,
    value=6.5,
    step=0.1,
    format="%0.1f%%"
)

def time_to_seconds(time_str):
    parts = time_str.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

def format_time(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f'{minutes}:{seconds:02d}'

def format_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f'{hours}:{minutes:02d}:{secs:02d}'
    else:
        return f'{minutes}:{secs:02d}'

try:
    # Convert input times to seconds
    times_pb = [
        time_to_seconds(track_400),
        time_to_seconds(track_800),
        time_to_seconds(track_1600),
        time_to_seconds(time_5k),
        time_to_seconds(time_10k),
        time_to_seconds(time_14k),
        time_to_seconds(time_hm)
    ]

    # Define distances and labels
    labels = ["Track 400", "Track 800", "Track 1600", "5k", "10k", "14k", "Half Marathon"]
    distances = [400, 800, 1600, 5000, 10000, 14000, 21097.5]

    # Calculate pace in sec/km from PB times
    pace_pb = [t / (d / 1000) for t, d in zip(times_pb, distances)]

    # Create decay model based on 1600m time
    start_distance = 1600
    start_time_sec = times_pb[2]  # 1600m time
    start_speed = start_distance / start_time_sec

    decay = (100 - decay_percent) / 100  # Convert percentage to decimal
    projected_pace = []
    projected_times = []

    for d in distances:
        ratio = np.log2(d / start_distance)
        decayed_speed = start_speed * (decay ** ratio)
        pace_sec_per_km = 1000 / decayed_speed
        projected_pace.append(pace_sec_per_km)
        projected_times.append(d / decayed_speed)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot PB data
    plt.plot(labels, pace_pb, label="Your Times", linewidth=4, marker='o', color='red')

    # Plot decay projection line
    plt.plot(labels, projected_pace, 
             label=f"{decay_percent}% decay model (from 1600m time)", 
             linestyle='--', color='orange', marker='x')

    # Label PB times
    for i, label in enumerate(labels):
        plt.text(i, pace_pb[i], format_hms(times_pb[i]), 
                fontsize=10, ha='center', va='bottom', color='red')

    # Label decay model with projected finish times
    for i, label in enumerate(labels):
        plt.text(i, projected_pace[i], format_hms(projected_times[i]), 
                fontsize=8, ha='center', va='top', color='black')

    # Axis and formatting
    plt.xlabel('Distance', fontsize=12)
    plt.ylabel('Pace (/km)', fontsize=12)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_time))
    plt.xticks(rotation=45)

    # Title, legend, grid
    plt.title('Your Running Times & Estimated Fatigue Curve', fontsize=14)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)

    # Analysis section
    st.subheader("Analysis")
    
    if decay_percent > 8:
        st.write("Your fatigue curve suggests you may have strengths in shorter distances. Consider endurance training to improve your performance in longer distances.")
    elif decay_percent < 5:
        st.write("Your fatigue curve shows excellent endurance capacity. You might benefit from speed work to improve your times across all distances.")
    else:
        st.write("Your fatigue curve falls within a typical range for well-trained runners. You could focus on either improving overall speed or specializing in specific distances.")

except ValueError as e:
    st.error("Please ensure all times are entered in the correct format (mm:ss or h:mm:ss)")

st.markdown("""
### How to Use This Tool
1. Enter your best times for each distance
2. Adjust the fatigue curve percentage to match your actual performance curve
3. Use the insights to guide your training focus

### About the Fatigue Curve
The fatigue curve represents how much your speed decreases as the distance doubles. A lower percentage indicates better endurance capacity, while a higher percentage suggests stronger speed but less endurance.

Created based on insights from [@johngetstrong](https://twitter.com/johngetstrong)
""") 