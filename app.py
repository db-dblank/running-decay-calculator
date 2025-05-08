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
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Enter Your Times")
    use_400 = st.checkbox("Include 400m", value=True)
    track_400 = st.text_input("400m time (mm:ss)", "1:02", disabled=not use_400)
    
    use_800 = st.checkbox("Include 800m", value=True)
    track_800 = st.text_input("800m time (mm:ss)", "2:25", disabled=not use_800)

with col2:
    st.subheader(" ")  # For alignment
    use_1600 = st.checkbox("Include 1600m", value=True)
    track_1600 = st.text_input("1600m time (mm:ss)", "4:57", disabled=not use_1600)
    
    use_5k = st.checkbox("Include 5K", value=True)
    time_5k = st.text_input("5K time (mm:ss or h:mm:ss)", "17:20", disabled=not use_5k)

with col3:
    st.subheader(" ")  # For alignment
    use_10k = st.checkbox("Include 10K", value=True)
    time_10k = st.text_input("10K time (h:mm:ss)", "39:16", disabled=not use_10k)
    
    use_14k = st.checkbox("Include 14K", value=True)
    time_14k = st.text_input("14K time (h:mm:ss)", "55:16", disabled=not use_14k)
    
    use_hm = st.checkbox("Include Half Marathon", value=True)
    time_hm = st.text_input("Half Marathon time (h:mm:ss)", "1:24:04", disabled=not use_hm)
    
    use_marathon = st.checkbox("Include Marathon", value=True)
    time_marathon = st.text_input("Marathon time (h:mm:ss)", "3:00:00", disabled=not use_marathon)

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
    if not time_str or not isinstance(time_str, str):
        st.error(f"Invalid time input: {time_str}")
        st.stop()
        
    parts = time_str.strip().split(":")
    try:
        if len(parts) == 2:  # mm:ss format
            minutes = int(parts[0])
            seconds = int(parts[1])
            if seconds >= 60:
                st.error(f"Seconds should be less than 60 in time: {time_str}")
                st.stop()
            return minutes * 60 + seconds
        elif len(parts) == 3:  # h:mm:ss format
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            if minutes >= 60 or seconds >= 60:
                st.error(f"Minutes and seconds should be less than 60 in time: {time_str}")
                st.stop()
            return hours * 3600 + minutes * 60 + seconds
        else:
            st.error(f"Time must be in mm:ss or h:mm:ss format. Got: {time_str}")
            st.stop()
    except (ValueError, IndexError) as e:
        st.error(f"Invalid time format: {time_str}. Please use mm:ss for times under 1 hour or h:mm:ss for longer times.")
        st.stop()

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
    # Create lists of all possible times, distances, and labels
    all_times = [
        (use_400, track_400),
        (use_800, track_800),
        (use_1600, track_1600),
        (use_5k, time_5k),
        (use_10k, time_10k),
        (use_14k, time_14k),
        (use_hm, time_hm),
        (use_marathon, time_marathon)
    ]
    
    all_distances = [400, 800, 1600, 5000, 10000, 14000, 21097.5, 42195]
    all_labels = ["Track 400", "Track 800", "Track 1600", "5k", "10k", "14k", "Half Marathon", "Marathon"]

    # Filter based on selected distances
    selected_times = [(use, time) for use, time in all_times if use]
    if not selected_times:
        st.error("Please select at least one distance to include in the analysis.")
        st.stop()
    
    times_pb = [time_to_seconds(time) for _, time in selected_times]
    distances = [d for use, d in zip([use_400, use_800, use_1600, use_5k, use_10k, use_14k, use_hm, use_marathon], all_distances) if use]
    labels = [l for use, l in zip([use_400, use_800, use_1600, use_5k, use_10k, use_14k, use_hm, use_marathon], all_labels) if use]

    # Calculate pace in sec/km from PB times
    pace_pb = [t / (d / 1000) for t, d in zip(times_pb, distances)]

    # Find the reference distance for the decay curve
    if use_1600 and "Track 1600" in labels:
        ref_idx = labels.index("Track 1600")
        ref_distance_name = "1600m"
    else:
        # Find the distance closest to the middle of the selected range
        middle_distance = (min(distances) + max(distances)) / 2
        ref_idx = min(range(len(distances)), key=lambda i: abs(distances[i] - middle_distance))
        ref_distance_name = labels[ref_idx]

    start_distance = distances[ref_idx]
    start_time_sec = times_pb[ref_idx]
    start_speed = start_distance / start_time_sec

    # Add explanation of reference point
    st.info(f"Using {ref_distance_name} as the reference point for calculating the fatigue curve.")

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
    plt.close('all')  # Clean up any existing plots
    fig, ax = plt.subplots(figsize=(12, 7))

    try:
        # Plot PB data points and line
        plt.plot(labels, pace_pb, 'ro-', label="Your Times", linewidth=2, markersize=8)

        # Plot decay projection line
        plt.plot(labels, projected_pace, 
                label=f"{decay_percent}% decay model (from {ref_distance_name})", 
                linestyle='--', color='orange', marker='x', markersize=6)

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

        # Title and legend
        plt.title('Your Running Times & Estimated Fatigue Curve', fontsize=14, pad=20)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Adjust layout
        fig.set_tight_layout(True)

        # Display the plot in Streamlit
        st.pyplot(fig)
    finally:
        plt.close(fig)  # Ensure figure is cleaned up even if there's an error

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
1. Select which distances to include in your analysis
2. Enter your best times for the selected distances
3. Adjust the fatigue curve percentage to match your actual performance curve
4. Use the insights to guide your training focus

### About the Fatigue Curve
The fatigue curve represents how much your speed decreases as the distance doubles. A lower percentage indicates better endurance capacity, while a higher percentage suggests stronger speed but less endurance.

Created based on insights from [@johngetstrong](https://twitter.com/johngetstrong)
""") 