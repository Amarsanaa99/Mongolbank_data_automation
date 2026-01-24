import { renderFredChart } from "./fredChart";

function main() {
  // Streamlit component тайлбар:
  // window.streamlitData дотор Python-аас ирсэн JSON байхаар тохируулах.
  const params = window.streamlitData || {};
  if (!params.data) {
    console.error("No data payload passed to component");
    return;
  }
  let payload;
  try {
    payload = JSON.parse(params.data);
  } catch (e) {
    console.error("Failed to parse payload", e);
    return;
  }

  renderFredChart(payload);
}

// Streamlit component бүр ачаалах үед main() дуудагдах ёстой.
window.renderFredChartComponent = main;
main();
