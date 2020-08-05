import React from 'react'

import InfoBox from "./InfoBox/InfoBox";

import "./ProbabilityQuery.scss"

class ProbabilityQuery extends React.Component {

    constructor(props) {
        super(props);


        this.reset_row = this.reset_row.bind(this)
        this.cycle = this.cycle.bind(this)

        this.infoBoxRef = React.createRef()

        this.state = {
            queryTable: <p>Loading...</p>,
            infoBox: <InfoBox ref={this.infoBoxRef}/>,
            outcomes: {},
            outcome_index: {},
            variable_type: {}
        }

        let full_outcomes = {}
        let full_outcome_index = {}
        let variable_type = {}

        window.pywebview.api.outcome_dict().then(data => {
            full_outcomes = data
        }).then(() => {

            // console.log("VARIABLES", full_outcomes)
            for (let key of Object.keys(full_outcomes)){
                // console.log("Key:", key)
                full_outcome_index[key] = -1
                variable_type[key] = ""
            }

            let table = <table>
                <thead>
                <tr>
                    <th />
                    <th>Variable</th>
                    <th>Outcome</th>
                    <th>Observation</th>
                    <th>Intervention</th>
                </tr>
                </thead>
                <tbody>
                {Object.keys(full_outcomes).map(row => {

                    console.log("Row", row)
                    return (
                        <tr>
                            <td>
                                <button onClick={() => this.reset_row(row)}>Reset</button>
                            </td>
                            <td>{row}</td>
                            <td>
                                <button
                                    onClick={() => this.cycle(row, "outcome")}
                                    id={row.toString()+"-outcome"}
                                >Outcome: {row}</button>
                            </td>
                            <td>
                                <button
                                    onClick={() => this.cycle(row, "observation")}
                                    id={row.toString()+"-observation"}
                                >Observation: {row}</button>
                            </td>
                            <td>
                                <button
                                    onClick={() => this.cycle(row, "intervention")}
                                    id={row.toString()+"-intervention"}
                                >Intervention: {row}</button>
                            </td>
                        </tr>
                    )})}
                </tbody>

            </table>

            this.setState({
                queryTable: table,
                outcomes: full_outcomes,
                outcome_index: full_outcome_index,
                variable_type: variable_type
            })
        })
    }

    reset_row(variable) {
        for (let variable_type of ["outcome", "observation", "intervention"]) {
            let button = document.getElementById(variable + "-" + variable_type)
            button.innerText = variable_type.charAt(0).toUpperCase() + variable_type.substr(1) + ": " + variable
            let indexes = this.state.outcome_index
            indexes[variable] = -1
            let variable_types = this.state.variable_type
            variable_types[variable] = ""
            this.setState({
                outcome_index: indexes,
                variable_type: variable_types
            })
        }

        this.infoBoxRef.current.receive_error("RESET")
    }

    cycle(variable, variable_type) {

        if (this.state.variable_type[variable] !== "" && this.state.variable_type[variable] !== variable_type)
            return

        // This is the button clicked from; ID = for example, "Xj-intervention"
        let button_pressed = document.getElementById(variable + "-" + variable_type)

        // The index of text that should be shown; initialized to -1 as a sentinel value
        let current_indexes = this.state.outcome_index

        // Increment by 1 to show next/first text, and wrap around if hit the end
        let new_index = (current_indexes[variable] + 1) % this.state.outcomes[variable].length

        // New text from the list of outcomes that can be shown
        let new_text = this.state.outcomes[variable][new_index]

        // Update index and set type
        current_indexes[variable] = new_index
        let variable_types = this.state.variable_type
        variable_types[variable] = variable_type
        this.setState({
            outcome_index: current_indexes,
            variable_type: variable_types
        })

        // Update text
        button_pressed.innerText = new_text
    }

    render() {
        return (
            <div className={"probabilityQueryContainer"}>
                <h1>ProbabilityQueryPage</h1>
                <div className={"mainContent"}>
                    {this.state.queryTable}
                    {this.state.infoBox}
                </div>
            </div>
        )
    }
}

export default ProbabilityQuery