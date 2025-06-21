import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(
    page_title="QuantDog",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("QuantDog: Quantum Threat Detection & Cryptography Swap")
st.markdown("### Real-time demonstration of adaptive cryptographic routing based on quantum threat levels")

if 'threat_level' not in st.session_state:
    st.session_state.threat_level = 20
if 'crypto_method' not in st.session_state:
    st.session_state.crypto_method = "Classical"
if 'threat_history' not in st.session_state:
    st.session_state.threat_history = [20] * 20
if 'routing_history' not in st.session_state:
    st.session_state.routing_history = []

def get_crypto_method(threat_level, transaction_value=1000):
    if transaction_value > 10000:
        threshold = 30
    elif transaction_value > 1000:
        threshold = 50
    else:
        threshold = 70
    
    if threat_level >= threshold:
        return "Post-Quantum", threshold
    else:
        return "Classical", threshold

def simulate_threat_change(increase=True):
    current = st.session_state.threat_level
    if increase:
        new_level = min(100, current + np.random.randint(15, 35))
    else:
        new_level = max(0, current - np.random.randint(10, 25))
    
    st.session_state.threat_level = new_level
    st.session_state.threat_history.append(new_level)
    if len(st.session_state.threat_history) > 20:
        st.session_state.threat_history.pop(0)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("Real-Time Threat Monitoring")
    
    fig = go.Figure()
    
    x = list(range(len(st.session_state.threat_history)))
    y = st.session_state.threat_history
    
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines+markers',
        name='Threat Level',
        line=dict(color='orange', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_hrect(y0=0, y1=30, fillcolor="green", opacity=0.1,
                  annotation_text="Low Risk", annotation_position="right")
    fig.add_hrect(y0=30, y1=70, fillcolor="yellow", opacity=0.1,
                  annotation_text="Medium Risk", annotation_position="right")
    fig.add_hrect(y0=70, y1=100, fillcolor="red", opacity=0.1,
                  annotation_text="High Risk", annotation_position="right")
    
    fig.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Threat Level (%)",
        yaxis=dict(range=[0, 100]),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Current Status")
    
    st.metric(
        label="Quantum Threat Level",
        value=f"{st.session_state.threat_level}%",
        delta=f"{st.session_state.threat_level - st.session_state.threat_history[-2]}%" if len(st.session_state.threat_history) > 1 else "0%"
    )
    
    st.markdown("---")
    
    crypto_method, threshold = get_crypto_method(st.session_state.threat_level)
    
    st.metric(
        label="Active Cryptography",
        value=crypto_method
    )
    
    st.markdown(f"**Threshold:** {threshold}%")

with col3:
    st.subheader("Threat Simulation")
    
    if st.button("Simulate Quantum Attack", use_container_width=True):
        simulate_threat_change(increase=True)
        crypto_method, _ = get_crypto_method(st.session_state.threat_level)
        
        if crypto_method != st.session_state.crypto_method:
            st.session_state.crypto_method = crypto_method
            st.session_state.routing_history.append({
                'time': datetime.now(),
                'threat': st.session_state.threat_level,
                'from': 'Classical' if crypto_method == 'Post-Quantum' else 'Post-Quantum',
                'to': crypto_method
            })
    
    if st.button("Reduce Threat Level", use_container_width=True):
        simulate_threat_change(increase=False)
        crypto_method, _ = get_crypto_method(st.session_state.threat_level)
        
        if crypto_method != st.session_state.crypto_method:
            st.session_state.crypto_method = crypto_method
            st.session_state.routing_history.append({
                'time': datetime.now(),
                'threat': st.session_state.threat_level,
                'from': 'Post-Quantum' if crypto_method == 'Classical' else 'Classical',
                'to': crypto_method
            })
    
    st.markdown("---")
    
    transaction_value = st.slider(
        "Transaction Value ($)",
        min_value=100,
        max_value=50000,
        value=5000,
        step=100
    )
    
    crypto_method, threshold = get_crypto_method(st.session_state.threat_level, transaction_value)
    st.info(f"Threshold: {threshold}% for ${transaction_value:,}")

st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Cryptographic Swap Events")
    
    if st.session_state.crypto_method == "Classical":
        st.success("**Classical Cryptography Active**")
        st.markdown("""
        - Using RSA-2048 / ECDSA
        - Standard blockchain signatures
        - Optimized for speed and efficiency
        - Suitable for current threat levels
        """)
    else:
        st.error("**Post-Quantum Cryptography Active**")
        st.markdown("""
        - Using CRYSTALS-Dilithium / FALCON
        - Quantum-resistant signatures
        - Enhanced security against quantum attacks
        - Protecting high-value transactions
        """)

with col2:
    st.subheader("Recent Routing Decisions")
    
    if st.session_state.routing_history:
        for event in reversed(st.session_state.routing_history[-5:]):
            if event['to'] == 'Post-Quantum':
                st.error(f"**Switched to {event['to']}** at threat level {event['threat']}%")
            else:
                st.success(f"**Switched to {event['to']}** at threat level {event['threat']}%")
            st.caption(f"{event['time'].strftime('%H:%M:%S')} - From {event['from']}")
    else:
        st.info("No routing changes yet. Simulate threats to see cryptographic swaps!")

st.markdown("---")
st.sidebar.markdown("---")
st.sidebar.markdown("### Status")
st.sidebar.markdown(f"Current Threat: **{st.session_state.threat_level}%**")
st.sidebar.markdown(f"Active Crypto: **{st.session_state.crypto_method}**")
st.sidebar.markdown(f"Swaps Made: **{len(st.session_state.routing_history)}**")
