import React from "react"

import "./BackdoorGraph.scss"

class BackdoorGraph extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            table: <p>Loading...</p>
        }

        window.pywebview.api.v_to_parents_and_children().then(response => {
            let table = <table>
                <tr>
                    <th />
                    <th />
                    <th>Variable</th>
                    <th>Parents</th>
                    <th>Children</th>
                    <th />
                </tr>
                {response.map(row =>
                    <tr>
                        <td>Add to X</td>
                        <td>Add to Y</td>
                        <td>{row[0]}</td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                        <td>Reset</td>
                    </tr>)}
            </table>

            this.setState({table: table})
        })
    }

    render() {
        return (
            <div className={"debug backdoorGraph"}>
                {this.state.table}
            </div>
        )
    }
}

export default BackdoorGraph