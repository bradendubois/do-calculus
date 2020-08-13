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
            y: [],
            z: []
        }

        this.compute_backdoor_paths = this.compute_backdoor_paths.bind(this)
        this.find_all_z = this.find_all_z.bind(this)
        this.add_v = this.add_v.bind(this)
        this.clear = this.clear.bind(this)
    }

    compute_backdoor_paths() {
        window.pywebview.api.backdoor_paths(this.state.x, this.state.y, this.state.z).then(response => {
            console.log(response)
        })
    }

    find_all_z() {

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
        } else if (set === "Z" && this.state.z.indexOf(v) === -1) {
            let c = this.state.z
            c.push(v)
            this.setState({z: c})
        }
    }

    clear(set) {
        if (set === "X") {
            this.setState({x: []})
        } else if (set === "Y") {
            this.setState({y: []})
        } else if (set === "Z") {
            this.setState({z: []})
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        // console.log(prevState.x, prevState.y, prevState.z, "->", this.state.x, this.state.y, this.state.z)
    }

    render() {
        return (
            <div className={"contentSection"} id={"backdoorPathContainer"}>
                <BackdoorButtons
                    z_callback={this.find_all_z}
                    path_callback={this.compute_backdoor_paths}
                    clear={this.clear}
                    x={this.state.x}
                    y={this.state.y}
                    z={this.state.z}
                />

                <BackdoorGraph
                    add_v={this.add_v}
                    x={this.state.x}
                    y={this.state.y}
                    z={this.state.z}
                />

                <Z_Sets />
                <BackdoorOutput />
            </div>
        )
    }
}

export default BackdoorPaths