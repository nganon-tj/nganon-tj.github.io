import React, { Component} from "react";

class GameInfo extends Component{
    render() {
        const attrTableRows = this.props.report.header.game_attributes.map((attr) => {
            return (
            <tr key={attr[0]}>
                <td className="attrName">{attr[0]}</td>
                <td>{attr[1]}</td>
            </tr>);
        })

        const playerTableRows = this.props.report.header.players.map((p) => {
            return (
                <tr key={p.player_id}>
                    <td>{p.name}</td>
                    <td>{p.civilization_name}</td>
                    <td>{p.team}</td>
                </tr>
            )
        })
        return (
            <div>
                <h1>Game Information</h1>
                <div className="flex-container">
                    <div className="game-attr">
                        <h3>Settings</h3>
                        <table>
                            <tbody>
                                {attrTableRows}
                            </tbody>
                        </table>
                    </div>
                    <div className="player-list">
                        <h3>Players</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Civilization</th>
                                    <th>Team</th>
                                </tr>
                            </thead>
                            <tbody>
                                {playerTableRows}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    }
}

export default GameInfo;