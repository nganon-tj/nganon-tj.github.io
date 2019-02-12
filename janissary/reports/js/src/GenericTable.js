import React, { Component} from "react";

class GenericTable extends Component {

    tableHeader = () => {
        return this.props.header.map((header, index) => {
            return <td key={index}>{header}</td>;
        })
    }

    tableRows = () => {
        let rows = this.props.rows;
        
        return rows.map((row, index) => {
            let cells = row.map((cell, index) => {
                return <td key={index}>{cell}</td>;
            });
            return <tr key={index}>{cells}</tr>
        });
    }

    render() {
        return (
            <div>
                <table>
                    <thead>
                        <tr>
                            {this.tableHeader()}
                        </tr>
                    </thead>
                    <tbody>
                        {this.tableRows()}
                    </tbody>
                </table>
            </div>
        )
    }
}

export default GenericTable;

            