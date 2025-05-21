import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

st.set_page_config(page_title="Calculadora de redução de desempenho", layout="wide")

st.title("Calculadora de redução de desempenho")

st.markdown("""
### Entendendo a sua curva de redução de performance

Esta ferramenta ajuda você visualizar o seu desempenho na corrida em diferentes distâncias e calcular a sua curva de fadiga. A curva de fadiga mostra como sua velocidade diminui à medida que a distância aumenta.

Como observado por [@johngetstrong](https://twitter.com/johngetstrong):
- Corredores de sprint/distâncias menores, normalmente apresentam curvas de fadiga em torno de 10%.
- Corredores de longas distâncias bem treinados podem alcançar curvas de fadiga tão baixas quanto 4%.
- Sua curva de fadiga pode indicar se você deve focar em:
  1. Elevar toda a curva (ficando mais rápido em todas as distâncias)
  2. Ajustar a curva por meio de treinamento especializado

Digite seus tempos abaixo para ver onde você se encontra!
""")

# Input columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Insira seus tempos")
    use_400 = st.checkbox("400m", value=True)
    track_400 = st.text_input("Tempo dos 400m (mm:ss)", "1:02", disabled=not use_400)
    
    use_800 = st.checkbox("800m", value=True)
    track_800 = st.text_input("Tempo dos 800m (mm:ss)", "2:25", disabled=not use_800)

with col2:
    st.subheader(" ")  # For alignment
    use_1600 = st.checkbox("1600m", value=True)
    track_1600 = st.text_input("Tempo dos 1600m (mm:ss)", "4:57", disabled=not use_1600)
    
    use_5k = st.checkbox("5K", value=True)
    time_5k = st.text_input("Tempo dos 5K (mm:ss or h:mm:ss)", "17:20", disabled=not use_5k)

with col3:
    st.subheader(" ")  # For alignment
    use_10k = st.checkbox("10K", value=True)
    time_10k = st.text_input("Tempo dos 10K (h:mm:ss)", "39:16", disabled=not use_10k)
    
    use_14k = st.checkbox("14K", value=True)
    time_14k = st.text_input("Tempo dos 14K (h:mm:ss)", "55:16", disabled=not use_14k)
    
    use_hm = st.checkbox("Meia Maratona", value=True)
    time_hm = st.text_input("Tempo da Meia Maratona (h:mm:ss)", "1:24:04", disabled=not use_hm)
    
    use_marathon = st.checkbox("Maratona", value=True)
    time_marathon = st.text_input("Tempo da Maratona (h:mm:ss)", "3:00:00", disabled=not use_marathon)

# Decay rate slider
decay_percent = st.slider(
    "Percentual da curva de fadiga (maior = mais fadiga entre as distâncias)",
    min_value=0.0,
    max_value=20.0,
    value=6.5,
    step=0.1,
    format="%0.1f%%"
)

def time_to_seconds(time_str):
    if not time_str or not isinstance(time_str, str):
        st.error(f"Tempo inválido: {time_str}")
        st.stop()
        
    parts = time_str.strip().split(":")
    try:
        if len(parts) == 2:  # mm:ss format
            minutes = int(parts[0])
            seconds = int(parts[1])
            if seconds >= 60:
                st.error(f"Os segundos devem ser menores que 60: {time_str}")
                st.stop()
            return minutes * 60 + seconds
        elif len(parts) == 3:  # h:mm:ss format
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            if minutes >= 60 or seconds >= 60:
                st.error(f"Minutos e segundos devem ser menores que 60: {time_str}")
                st.stop()
            return hours * 3600 + minutes * 60 + seconds
        else:
            st.error(f"O tempo deve estar no formato mm:ss ou h:mm:ss: {time_str}")
            st.stop()
    except (ValueError, IndexError) as e:
        st.error(f"Invalid time format: {time_str}. Use mm:ss para tempos menores que 1 hora ou h:mm:ss para tempos maiores.")
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
    all_labels = ["400m", "800m", "1600m", "5k", "10k", "14k", "Meia Maratona", "Maratona"]

    # Filter based on selected distances
    selected_times = [(use, time) for use, time in all_times if use]
    if not selected_times:
        st.error("Por favor, selecione pelo menos uma distância para incluir na análise.")
        st.stop()
    
    times_pb = [time_to_seconds(time) for _, time in selected_times]
    distances = [d for use, d in zip([use_400, use_800, use_1600, use_5k, use_10k, use_14k, use_hm, use_marathon], all_distances) if use]
    labels = [l for use, l in zip([use_400, use_800, use_1600, use_5k, use_10k, use_14k, use_hm, use_marathon], all_labels) if use]

    # Calculate pace in sec/km from PB times
    pace_pb = [t / (d / 1000) for t, d in zip(times_pb, distances)]

    # Find the reference distance for the decay curve
    if use_1600 and "1600m" in labels:
        ref_idx = labels.index("1600m")
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
    st.info(f"Usando {ref_distance_name} como ponto de referência para calcular a curva de fadiga.")

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
        plt.plot(labels, pace_pb, 'ro-', label="Seus tempos", linewidth=2, markersize=8)

        # Plot decay projection line
        plt.plot(labels, projected_pace, 
                label=f"{decay_percent}% redução do modelo (de {ref_distance_name})", 
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
        plt.xlabel('Distância', fontsize=12)
        plt.ylabel('Pace (/km)', fontsize=12)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_time))
        plt.xticks(rotation=45)

        # Title and legend
        plt.title('Seus tempos de corrida e curva de fadiga estimada', fontsize=14, pad=20)
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        
        # Adjust layout with specific margins
        plt.subplots_adjust(left=0.12, right=0.95, top=0.9, bottom=0.15)

        # Display the plot in Streamlit
        st.pyplot(fig)
    finally:
        plt.close(fig)  # Ensure figure is cleaned up even if there's an error

    # Analysis section
    st.subheader("Análises")
    
    if decay_percent > 8:
        st.write("Sua curva de fadiga sugere que você tem um bom desempenho em distâncias curtas. Considere o treinamento para melhorar sua resistência e o desempenho em distâncias mais longas.")
    elif decay_percent < 5:
        st.write("Sua curva de fadiga sugere que você tem um bom desempenho em distâncias longas. Considere o treinamento para melhorar sua velocidade e o desempenho em todas as distâncias.")
    else:
        st.write("Sua curva de fadiga está na faixa típica para corredores bem treinados. Você pode focar em melhorar sua velocidade ou priorizar o desempenho em distâncias específicas.")

except ValueError as e:
    st.error("Por favor, insira todos os tempos com a forma correta (mm:ss ou h:mm:ss)")

st.markdown("""
### Como usar a calculadora

1. Selecione as distâncias que você irá incluir
2. Coloque os seus melhores tempos para as distâncias selecionadas
3. Ajuste o percentual da curva de fadiga para corresponder a sua curva de desempenho atual
4. Use as informações para orientar o foco do seu treino

### Sobre a curva de fadiga
A curva de fadiga representa o quanto a sua velocidade diminui à medida que a distância aumenta. Um percentual baixo indica uma grande capacidade de resistência, enquanto um percentual maior sugere menor resistência.

Criado baseado nas informações do [@johngetstrong](https://twitter.com/johngetstrong)
""") 
