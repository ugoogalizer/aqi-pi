//Plot.ly Javascript plot used to display latest measurements
//Original sounced from "aqi" fork: https://github.com/jtme/aqi

var xmlhttp = new XMLHttpRequest();
xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        var myArr = JSON.parse(this.responseText);
        PlotGraph(myArr);
        PlotGraph2(myArr);
    }
};

xmlhttp.open("GET", "aqi.json", true);
xmlhttp.send();

function PlotGraph(data) {
  let trace1 = {
    x: [],
    y: [],
    //mode: "lines"
    type: "scatter",
    name: "PM2.5"
  };
  let trace2 = {
    x: [],
    y: [],
    //mode: "lines"
    type: "scatter",
    name: "PM10"
  };
    data.forEach(function(val) {
      var entryDateTime = new Date(val.time);
      if (entryDateTime >= (Date.now() - 24*60*60*1000)) {
        trace1.x.push(entryDateTime);
        trace1.y.push(val["pm25"]);
        trace2.x.push(entryDateTime);
        trace2.y.push(val["pm10"]);
      
      }
    });
  Plotly.newPlot('AQIplot', [trace1, trace2]);
}; 


function PlotGraph2(data) {
  let trace1 = {
    x: [],
    y: [],
    //mode: "lines"
    type: "bar",
    name: "PM2.5"
  };
    data.forEach(function(val) {
      var entryDateTime = new Date(val.time);
      if (entryDateTime >= (Date.now() - 24*60*60*1000)) {
        trace1.x.push(entryDateTime);
        trace1.y.push(val["pm25"]);
      
      }
    });
  Plotly.newPlot('AQIplotBarpm25', [trace1]);
}; 