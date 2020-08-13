import React from "react"

import BackdoorButtons from "./BackdoorButtons/BackdoorButtons";
import BackdoorGraph from "./BackdoorGraph/BackdoorGraph";
import Z_Sets from "./Z_Sets/Z_Sets";
import BackdoorOutput from "./BackdoorOutput/BackdoorOutput";


import "./BackdoorPaths.scss"

class BackdoorPaths extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            x: [],
            y: []
        }

        this.find_all_z = this.find_all_z.bind(this)
        this.add_v = this.add_v.bind(this)
    }

    find_all_z(x, y) {

    }

    add_v(set, v) {
        if (set === "X") {
            let c = this.state.x
            c.push(v)
            this.setState({x: c})
        } else {
            let c = this.state.y
            c.push(v)
            this.setState({y: c})
        }
    }

    render() {
        return (
            <div className={"contentSection"} id={"backdoorPathContainer"}>
                <BackdoorButtons z_callback={this.find_all_z} x={this.state.x} y={this.state.y} />
                <BackdoorGraph add_v={this.add_v} x={this.state.x} y={this.state.y}/>
                <Z_Sets />
                <BackdoorOutput />
            </div>
        )
    }
}

export default BackdoorPaths