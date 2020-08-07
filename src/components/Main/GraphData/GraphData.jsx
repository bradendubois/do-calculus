import React from 'react'

import "./GraphData.scss"

class GraphData extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            tbody: <p>Loading...</p>,
            table: <p>Select a Variable to see its Table...</p>
        }

        window.pywebview.api.all_variable_data().then(data => {

            let tbody = (
                <tbody>
                <tr>
                    <th>Variable</th><th>Outcomes</th><th>Parents</th>
                </tr>
                {data.map(row =>
                    <tr>
                        <td><button
                            className={"niceButton"}
                            onClick={() => this.load_table(row[0])}
                        >{row[0]}</button></td>
                        <td>{row[1].map(o => <>{o}</>)}</td>
                        <td>{row[2].map(p => <a onClick={() => this.load_table(p)}>{p}</a>)}</td>
                    </tr>
                )}
                </tbody>
            )

            this.setState({tbody: tbody})
        })
    }

    load_table(variable) {
        window.pywebview.api.variable_table(variable).then(response => {
            let table = (
                <tbody>
                <tr>
                    {<th>{response[0][0]}</th>}
                    {response[0][1].map(o => <th>{o}</th>)}
                    {<th>{response[0][2]}</th>}
                </tr>
                {response.slice(1).map((row, idx) =>
                    <tr>
                        <td>{row[0]}</td>
                        {row[1].map(o => <td><>{o}</></td>)}
                        <td><p>{row[2]}</p></td>
                    </tr>
                )}
                </tbody>
            )

            this.setState({table: table})
        })
    }

    render() {
        return (
            <div className={"graphDataContainer"}>
                <h1>Variable Data</h1>
                <div className={"mainGraphContent"}>
                    <div>
                        {this.state.tbody}
                    </div>
                    <div>
                        {this.state.table}
                    </div>
                </div>
            </div>
        )
    }
}

export default GraphData