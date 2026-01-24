import Plotly from "plotly.js-dist-min";

// payload: { time: [...], series: {name: [...], ...}, indicators: [...] }
export function renderFredChart(payload) {
  const mainDiv = document.getElementById("main-chart");
  const miniDiv = document.getElementById("mini-chart");

  if (!mainDiv || !miniDiv) {
    console.error("Divs not found");
    return;
  }

  const time = payload.time || [];
  const series = payload.series || {};
  const indicators = payload.indicators || Object.keys(series);

  const traces = indicators.map((name) => ({
    x: time,
    y: series[name] || [],
    mode: "lines",
    name: name,
    line: { width: 2.4 }
  }));

  // full domain
  const minX = time[0];
  const maxX = time[time.length - 1];

  // --- MAIN CHART ---
  const mainLayout = {
    margin: { l: 40, r: 140, t: 30, b: 10 },
    showlegend: true,
    legend: {
      x: 1.02,
      y: 1,
      xanchor: "left",
      yanchor: "top",
      bgcolor: "rgba(0,0,0,0)",
      orientation: "v",
      font: { size: 11 }
    },
    xaxis: {
      type: "date",
      range: [minX, maxX],
      rangeslider: { visible: false },
      showgrid: false,
      title: ""
    },
    yaxis: {
      title: "",
      zeroline: false,
      showgrid: true,
      gridcolor: "rgba(224,224,224,0.3)"
    },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    height: 400
  };

  // --- MINI CHART ---
  const miniLayout = {
    margin: { l: 40, r: 40, t: 0, b: 30 },
    showlegend: false,
    xaxis: {
      type: "date",
      range: [minX, maxX],
      rangeslider: {
        visible: true,
        range: [minX, maxX] // window
      },
      showgrid: false,
      title: ""
    },
    yaxis: {
      fixedrange: true,
      title: "",
      showgrid: false
    },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    height: 80
  };

  Plotly.newPlot(mainDiv, traces, mainLayout, { displaylogo: false });
  Plotly.newPlot(miniDiv, traces, miniLayout, {
    displaylogo: false,
    staticPlot: false
  });

  // --- Sync: main -> mini ---
  mainDiv.on("plotly_relayout", (ev) => {
    const s = ev["xaxis.range[0]"];
    const e = ev["xaxis.range[1]"];
    if (s && e) {
      Plotly.relayout(miniDiv, {
        "xaxis.rangeslider.range": [s, e]
      });
    }
  });

  // --- Sync: mini -> main ---
  miniDiv.on("plotly_relayout", (ev) => {
    const s = ev["xaxis.range[0]"];
    const e = ev["xaxis.range[1]"];
    if (s && e) {
      Plotly.relayout(mainDiv, {
        "xaxis.range": [s, e]
      });
    }
  });
}
