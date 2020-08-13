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
        this.clear = this.clear.bind(this)
    }

    find_all_z() {
        window.pywebview.api.backdoor_paths(this.state.x, this.state.y, []).then(response => {
            console.log(response)
        })
    }

    add_v(set, v) {
        if (set === "X" && this.state.x.indexOf(v) === -1) {
            let c = this.state.x
            c.push(v)
            this.setState({x: c})
        } else if (set === "Y"  && this.state.y.indexOf(v) === -1) {
            let c = this.state.y
            c.push(v)
            this.setState({y: c})
        }
    }

    clear(set) {
        if (set === "X") {
            this.setState({x: []})
        } else {
            this.setState({y: []})
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        console.log(prevState.x, prevState.y, this.state.x, this.state.y)
    }

    render() {
        return (
            <div className={"contentSection"} id={"backdoorPathContainer"}>
                <BackdoorButtons z_callback={this.find_all_z} clear={this.clear} x={this.state.x} y={this.state.y} />
                <BackdoorGraph add_v={this.add_v} x={this.state.x} y={this.state.y}/>
                <Z_Sets />
                <BackdoorOutput />
            </div>
        )
    }
}

export default BackdoorPaths