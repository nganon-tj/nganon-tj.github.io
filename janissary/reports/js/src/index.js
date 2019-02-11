
import React from "react";
import ReactDOM from "react-dom";
import App from "./App.js";
ReactDOM.render(<App />, document.getElementById("root"));


// import {Chart} from "chart.js"
// import 'chartjs-plugin-colorschemes';

// let jsdata = null



// function CreateApsGraph() {
//     let series = jsdata.aps_graph.series
//     let players = jsdata.aps_graph.players
   
//     let ctx = document.getElementById("apsgraph").getContext('2d');
//     let datasets = []
//     for (var player_id in players) {
//         let d = {
//             label: players[player_id],
//             // Convert ms to minutes for time axis
//             data: series[player_id].map((tuple) => { return {x: tuple[0]/60.0/1000.0, y: tuple[1]}; })
//         };
//         datasets.push(d);
//     }
//     let chart = new Chart(ctx, {
//         type: 'scatter',
//         data: {
//             datasets: datasets,
//         },
//         options: {
//             responsive: true,
//             tooltips: {
//                 mode: 'index',
//                 intersect: false,
//             },
//             hover: {
//                 mode: 'nearest',
//                 intersect: true
//             },
//             showLines: true,
//             fill: false,
//             scales: {
//                 xAxes: [{
//                     display: true,
//                     scaleLabel: {
//                         display: true,
//                         labelString: 'Time (min)'
//                     }
//                 }],
//                 yAxes: [{
//                     display: true,
//                     scaleLabel: {
//                         display: true,
//                         labelString: 'Actions/minute'
//                     }
//                 }]
//             }
//         }
//    });
// }

// function Init() {
//     jsdata = JSON.parse(document.getElementById('data').innerHTML);
//     // Prove we load
//     // alert("Javascript bundle installed!");
//     CreateApsGraph();
// }

// $(document).ready( function() { Init(); } );