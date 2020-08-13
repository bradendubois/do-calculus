import * as React from 'react'

import "./Main.scss"

import GraphData from "./GraphData/GraphData";
import ProbabilityQuery from "./ProbabilityQuery/ProbabilityQuery";
import BackdoorPaths from "./BackdoorPaths/BackdoorPaths";

class Main extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            active: <h1>Select an option from the sidebar on the left.</h1>
        }

        this.graphData = <GraphData />
        this.probabilityQuery = <ProbabilityQuery />
        this.backdoorPath = <BackdoorPaths />

        this.setActive = this.setActive.bind(this)
    }

    setActive(page) {

        console.log(page)

        switch (page) {
            case "graphData":
                this.setState({active: this.graphData})
                break
            case "probabilityQuery":
                this.setState({active: this.probabilityQuery})
                break
            case "backdoorPath":
                this.setState({active: this.backdoorPath})
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