# Adaptive Resource Lab

This project is a self-contained browser app with:

- A dashboard page at `index.html`
- A simulator page at `simulator.html`
- Scheduling models for `FCFS`, `Round Robin`, `Priority Round Robin`, `MLQ`, `MLFQ`, and a macOS-style adaptive scheduler
- Process configuration with arrival time, burst, priority, queue, QoS, and memory footprint
- Timeline, per-process metrics, event log, and memory-pressure visualization

## Run locally

Because the app uses JavaScript modules, it should be served through a small local web server instead of opening the files directly.

```bash
cd "/Users/shivambharti/Documents/New project"
python3 -m http.server 4173
```

Then open:

- `http://127.0.0.1:4173/index.html`
- `http://127.0.0.1:4173/simulator.html`

## Files

- `index.html` - dashboard overview
- `simulator.html` - interactive simulator
- `styles/main.css` - shared styling
- `scripts/algorithms.js` - scheduling and memory-pressure logic
- `scripts/dashboard.js` - dashboard rendering
- `scripts/simulator.js` - simulator interactions
- `scripts/data-store.js` - local storage helpers
