import React, { Component} from "react";
import {report} from "./utils.js";
import "./App.css";
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import GameInfo from "./GameInfo.js"
import ActionRate from "./ActionRate.js"
import UnitProduction from "./UnitProduction.js"
import "react-tabs/style/react-tabs.css";

class App extends Component{
  render(){
    let report_data = report();
    return(
      <div className="App">
        <Tabs>
            <TabList>
                <Tab>Game Info</Tab>
                <Tab>Action Rate</Tab>
                <Tab>Unit Production</Tab>
            </TabList>

            <TabPanel>
                <GameInfo report={report_data}></GameInfo>
            </TabPanel>
            <TabPanel>
                <ActionRate report={report_data}></ActionRate>
            </TabPanel>
            <TabPanel>
                <UnitProduction report={report_data}></UnitProduction>
            </TabPanel>
        </Tabs>
      </div>
    );
  }
}

export default App;