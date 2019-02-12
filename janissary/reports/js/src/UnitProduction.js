import React, { Component } from "react";
import {Line} from "react-chartjs-2";
import Tooltip from "@material-ui/core/Tooltip";
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import GenericTable from "./GenericTable.js";

const PEASANT_ID = 83; // It feels kind of bad to encode this here, but this is the object ID for peasants

class UnitProduction extends Component{

    peasantData = () => {
        let series = this.props.report.reports.unit_production.series
        let labels = series.time.map((t) => {
            return (t / 60.).toString();
        });

        return {
            labels: labels,
            datasets: Object.keys(series.players).map((player_id) => {
                let player_name = series.players[player_id].player_name;
                
                return {
                    label: player_name,
                    fill: false,
                    data: series.players[player_id].units[PEASANT_ID].counts,
                    lineTension: 0 // Don't do cubic interpolation; it's all lies
                }
            })
        };

    }

    peasantOptions = () => {
        return {
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            // hover: {
            //     mode: 'nearest',
            //     intersect: true
            // },
            maintainAspectRatio: false,
            fill: false,
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time (min)'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Cumulative Peasants Produced'
                    }
                }]
            }
        };
    }

    playerMilitaryData = (player_id) => {
        let series = this.props.report.reports.unit_production.series;
        let labels = series.time.map((t) => {
            return (t / 60.).toString();
        });

        // Don't plot peasants here
        let units_to_plot = Object.keys(series.players[player_id].units).filter((unit_id) => unit_id != PEASANT_ID)

        return {
            labels: labels,
            datasets: units_to_plot.map((unit_id) => {
                let unit_name = series.players[player_id].units[unit_id].unit_name;
                return {
                    label: unit_name,
                    fill: false,
                    data: series.players[player_id].units[unit_id].counts,
                    lineTension: 0 // Don't do cubic interpolation; it's all lies
                }
            })
        };

    };

    largestUnitCount = () => {
        let maxNum = 0;
        let rows = this.props.report.reports.unit_production.total_units_table.rows;
        rows.forEach((row) => {
            row.slice(1).forEach((col) => {
                if (col > maxNum) {
                    maxNum = col;
                }
            });
        });
        return  maxNum;
    }

    handleLockYAxesChange = (event) => {
        this.setState({lockYAxes: event.target.checked});
    }

    playerMilitaryOptions = (player_id) => {
        let maxValue = 0;
        if (this.state.lockYAxes) {
            maxValue = Math.ceil(this.largestUnitCount() / 10) * 10;
        }
        
        return {
            responsive: true,
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            fill: false,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Time (min)'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Cumulative Units Produced'
                    },
                    ticks: {
                        suggestedMax: maxValue
                    }
                }]
            }
        };
    };

    playerMilitaryCharts = () => {
        let series = this.props.report.reports.unit_production.series 
        return Object.keys(series.players).map((player_id) => {
            return (
                <div>
                    <h4>{series.players[player_id].player_name}</h4>
                    <div style={{width:"100%", height:"250px"}}>
                        <Line 
                            data={this.playerMilitaryData(player_id)}
                            options={this.playerMilitaryOptions(player_id)}
                            height={250} key={player_id}
                            />
                    </div>
                </div>
            )
        })
    };

    state = {
        lockYAxes: true
    };

    
    render() {
        let cancelLongExplanation = `Cancel commands give the position in the queue that is cancelled. Unfortunately, without modelling all of the timing on unit production, 
        and for example knowing whether there are sufficient houses to build, we don't know what 
        the state of the queue was at the time of the cancel command. Most of the time, this error will be small in the grand scheme of things.`;
        return(
            <div>
                <h1>Unit Production</h1>
                <p>These reports are based on the units trained. Roughly, they represent the sum of units created or queued for creation, because we do not model the full game
                dynamics and don't know when units are <strong>created</strong>, or when they die; we only know when they were queued for training. Also, units can be canceled 
                after queueing, and although we know when a unit in a particular building is canceled, we can't know for sure <strong>which</strong> unit type is canceled. 
                In cases where multiple types of units are trained in a building at the same time, and some of them are cancelled, this <Tooltip title={cancelLongExplanation}><a href='#'>report may be wrong</a></Tooltip>.
                </p>
                <h3>Total Units Produced</h3>
                
                <GenericTable 
                    header={this.props.report.reports.unit_production.total_units_table.header}
                    rows={this.props.report.reports.unit_production.total_units_table.rows} >
                </GenericTable>

                <h3>Peasant Production</h3>
                <div style={{width: "100%", height: "500px"}}>
                    <Line data={this.peasantData()} options={this.peasantOptions()} />
                </div>

                
                <div>
                    <h3>Military Production</h3>
                    <FormControlLabel 
                        control={<Switch checked={this.state.lockYAxes} onChange={this.handleLockYAxesChange} color="primary" />}
                        label="Lock Y Axes" />
                    {this.playerMilitaryCharts()}
                </div>
            </div>
        )
    }
}

export default UnitProduction;