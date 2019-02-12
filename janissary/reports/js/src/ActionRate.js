import React, { Component} from "react";
import {Line, Scatter} from "react-chartjs-2";
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormLabel from '@material-ui/core/FormLabel';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import "chartjs-plugin-colorschemes";
import { object } from "prop-types";

import GenericTable from "./GenericTable.js";

class Plot extends Component {
    totalData() {
        let labels = this.props.report.reports.actions_rate.series[1].map((item) => {
            // convert ms to minutes for x axis
            return Math.round(item[0]/60.0/1000.0).toString();
        });

        return {
            labels: labels,
            datasets: this.props.report.header.players.map((p) => {
                let player_id = p.player_id;
                let player_name = p.name
                return {
                    label: player_name,
                    data: this.props.report.reports.actions_rate.series[player_id].map((item) => {
                            return item[1]['Total'];
                        }),
                    lineTension: 0 // Don't do cubic interpolation; it's all lies

                }
                // return {
                //     label: player_name,
                //     data: this.props.report.reports.actions_rate.series[player_id].map((item) => {
                //         // convert ms to minutes for x axis
                //         return {x: item[0]/60.0/1000.0, y: item[1]['Total'] };
                //     })
                // }
            })
        };
    }

    playerData(player_id) {
        let series = this.props.report.reports.actions_rate.series
        // A list of all action types from the first time series value for the first player
        let action_types = Object.keys(series[1][0][1])
        action_types = action_types.filter((item) => item != "Total" && item != "Other")

        // Count total actions by action type for this player
        let counts_map = {}
        action_types.forEach((action) => {
            counts_map[action] = 0;
        })
        series[player_id].forEach((item) => { 
            Object.keys(item[1]).forEach((action) => {
                counts_map[action] += item[1][action];
            })
        });
        
        // Pick the top action types to display and aggregate the others to "other"
        let counts_list = Object.keys(counts_map).map((key) => {
            return {action_type: key, count: counts_map[key]};
        })
        counts_list.sort((a, b) => (b.count - a.count));
        action_types = counts_list.slice(0, 4).map((item) => item.action_type)
        action_types.sort()
        action_types.push("Other");
        
        for(var i=0; i<series[player_id].length; i++) {
            let other_count = 0
            Object.keys(series[player_id][i][1]).forEach((key) => {
                if(key != "Total" && !action_types.includes(key)) {
                    other_count += series[player_id][i][1][key];    
                }
            })
            series[player_id][i][1]["Other"] = other_count;
        }

        return {
            datasets: action_types.map((action) => {
                return {
                    label: action,
                    data: series[player_id].map((item) => {
                        // convert ms to minutes for x axis
                        return {x: item[0]/60.0/1000.0, y: item[1][action] };
                    }),
                    lineTension: 0 // Don't do cubic interpolation; it's all lies
                }
            })
        };
    }

    chartData() {
        if(this.props.plotSelect == 0) {
            let data = this.totalData();
            return this.totalData();
        } else {
            let data = this.playerData(this.props.plotSelect);
            return data;
        }
        // return {
        //     datasets: [
        //         {
        //             label: 'line 1',
        //             data: [
        //                 {x: 0, y:0},
        //                 {x: 10, y:20},
        //                 {x: 20, y:19}
        //             ]
        //         },
        //         {
        //             label: 'line 2',
        //             data: [
        //                 {x: 0, y:20},
        //                 {x: 10, y:15},
        //                 {x: 20, y:5}
        //             ]
        //         }
        //     ]
        // }
    }

    chartOptions() {
        let series = this.props.report.reports.actions_rate.series;
        let maxValue = 0;
        for (var player_id in series) {
            series[player_id].forEach((item) => {
                let total = item[1]["Total"];
                if (total > maxValue) {
                    maxValue = total;
                }
            });
        }
        maxValue = Math.ceil(maxValue / 10) * 10;

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
            showLines: true,
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
                        labelString: 'Actions/minute'
                    },
                    stacked: this.props.plotSelect != 0,
                    ticks: {
                        suggestedMax: maxValue
                    }
                }]
            }
        }
    }
    render () {
        return <Line data={this.chartData()} options={this.chartOptions()} width={800} height={500}/>
    }
}

class PlayerSelector extends Component {
    constructor(props) {
        super(props);
        this.state = {value: this.props.value || "0"};
    }

    handleChange = event => {
        this.setState({value: event.target.value});
        this.props.onChange(event.target.value);
    };

    
    playerList() {
        return this.props.players.map((p) => {
            return <FormControlLabel 
                value={p.player_id.toString()}
                control={<Radio color="primary" />}
                label={p.name}
                labelPlacement="end"
                />
        })
    }
    render () {
        return (
            <div>
                <FormControl component="fieldset">
                    <FormLabel component="legend">Plot</FormLabel>
                    <RadioGroup
                        aria-label="plot-type"
                        name="plottype"
                        value={this.state.value}
                        onChange={this.handleChange}>
                        <FormControlLabel
                        value="0"
                        control={<Radio color="primary" />}
                        label="All Players"
                        labelPlacement="end"
                        />
                        {this.playerList()}
                    </RadioGroup>
                </FormControl>
            </div>
        );
    }
}

class ActionRate extends Component{
    constructor(props) {
        super(props);
        this.state = {plotSelect: 0}
    }
    handlePlayerSelect = (value) => {
        this.setState({plotSelect: parseInt(value)});
        console.log("Player selected: ", value);
    }

    render() {
        return (
            <div>
                <h1>Action Rate</h1>
                <div className="flex-container">
                    <div className="chart-container">
                        <Plot report={this.props.report} plotSelect={this.state.plotSelect} />
                    </div>
                    <PlayerSelector players={this.props.report.header.players} value="0" onChange={this.handlePlayerSelect} />
                </div>
                <div>
                    <h3>Total player commands</h3>
                    <GenericTable header={this.props.report.reports.command_summary.player_command_table.header} rows={this.props.report.reports.command_summary.player_command_table.rows} />
                </div>
                <div>
                    <h3>Unassigned Commands</h3>
                    <p>These are commands that were found in the log, but were not assigned to any player. This is probably because they are not understood by the log parser.</p>
                    <GenericTable header={this.props.report.reports.command_summary.unassigned_command_table.header} rows={[this.props.report.reports.command_summary.unassigned_command_table.row]} />
                </div>
            </div>
        )
    }
}

export default ActionRate;