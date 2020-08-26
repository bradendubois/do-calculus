import React from "react"

import BackdoorButtons from "./BackdoorButtons/BackdoorButtons";
import BackdoorGraph from "./BackdoorGraph/BackdoorGraph";
import Z_Sets from "./Z_Sets/Z_Sets";
import BackdoorOutput from "./BackdoorOutput/BackdoorOutput";


import "./BackdoorPaths.scss"

const stringify = (x, y, z) => {

    x.sort()
    y.sort()
    z.sort()

    // TODO - Import a font such that ⫫ can be properly rendered
    let message = x.join(", ") + " _||_ " + y.join(", ");
    if (z.length > 0)
        message += " | " + z.join(", ")
    return message
}

class BackdoorPaths extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            x: [],
            y: [],
            z: [],
            backdoor_results: [],
            messages: []
        }

        this.compute_backdoor_paths = this.compute_backdoor_paths.bind(this)
        this.find_all_z = this.find_all_z.bind(this)
        this.add_v = this.add_v.bind(this)
        this.clear = this.clear.bind(this)
    }

    compute_backdoor_paths() {

        let x = this.state.x
        let y = this.state.y
        let z = this.state.z

        x.sort()
        y.sort()
        z.sort()

        if (x.length === 0) {
            let messages = this.state.messages
            let message = "Error: Measurable variables X cannot be empty."
            messages.splice(0, 0, message);
            this.setState({messages: messages})
            return
        }

        if (y.length === 0) {
            let messages = this.state.messages
            let message = "Error: Measurable variables Y cannot be empty."
            messages.splice(0, 0, message);
            this.setState({messages: messages})
            return
        }

        let message = stringify(x, y, z)

        if (this.state.messages.includes(message)) {
            let cur = this.state.messages;
            cur.push("Already computed: " + message)
            this.setState({messages: cur})
            return
        }

        window.pywebview.api.backdoor_paths(x, y, z).then(response => {

            x.sort()
            y.sort()
            z.sort()
            
            let cur = this.state.backdoor_results
            if (response.length > 0) {
                cur.push(
                    <details>
                        <summary>{message}</summary>
                        {response.map(path => <li>{path}</li>)}
                    </details>
                )
            } else {
                cur.push(<li>{message}</li>)
            }

            let messages = this.state.messages
            messages.splice(0, 0, message)
            this.setState({backdoor_results: cur, messages: messages})
        })
    }

    find_all_z() {

        let x = this.state.x
        let y = this.state.y

        window.pywebview.api.all_z_results(x, y).then(response => {

            /*
            for (let z_response of response) {
                if (z_response["sufficient"] === true) {
                    results.push(<li>{stringify(x, y, z_response.z)}</li>)
                } else {
                    results.push(
                        <details>
                            <summary>{stringify(x, y, z_response["z"])}</summary>
                            {z_response["paths"].map(path => <li>{path}</li>)}
                        </details>
                    )
                }
            }*/

            console.log(response)

            this.setState({backdoor_results: response})
        })
    }

    add_v(set, v) {
        let taken = this.state.x.concat(this.state.y).concat(this.state.z)
        console.log("Parent", taken)
        if (set === "X" && taken.indexOf(v) === -1) {
            let c = this.state.x
            c.push(v)
            this.setState({x: c})
        } else if (set === "Y"  && taken.indexOf(v) === -1) {
            let c = this.state.y
            c.push(v)
            this.setState({y: c})
        } else if (set === "Z" && taken.indexOf(v) === -1) {
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

                <div className={"topContainer"}>
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
                </div>

                <div className={"bottomContainer"}>
                    <Z_Sets content={this.state.backdoor_results}/>
                    <BackdoorOutput
                        messages={this.state.messages}
                    />
                </div>
            </div>
        )
    }
}

export default BackdoorPaths