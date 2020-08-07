import * as React from 'react'

import "./Main.scss"

import GraphData from "./GraphData/GraphData";
import ProbabilityQuery from "./ProbabilityQuery/ProbabilityQuery";


class Main extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            active: <h1>Select an option from the sidebar on the left.</h1>
        }

        this.graphData = <GraphData />
        this.probabilityQuery = <ProbabilityQuery />

        this.setActive = this.setActive.bind(this)
    }

    setActive(page) {

        switch (page) {
            case "Graph Data":
                this.setState({active: this.graphData})
                break
            case "Probability Query":
                this.setState({active: this.probabilityQuery})
                break
            default:
                break
        }
    }

    render() {

        return (
            <div className={"mainContent"}>
                {this.state.active}
            </div>
        )
    }
}

export default Main;