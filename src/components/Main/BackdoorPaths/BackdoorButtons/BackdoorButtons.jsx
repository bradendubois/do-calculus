import React from "react"

import "./BackdoorButtons.scss"

class BackdoorButtons extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            getInput: true,
            x: [],
            y: []
        }
    }

    render() {
        return (
            <div className={"debug backdoorButtons"}>
                <div className={"buttonHeader"}>
                    <div>{this.state.x.map(x => <p>{x}</p>)}</div>
                    <button onClick={() => this.setState({x: []})}>Clear X</button>
                    <div>{this.state.y.map(y => <p>{y}</p>)}</div>
                    <button onClick={() => this.setState({y: []})}>Clear Y</button>
                </div>
                <div className={"backdoorMainButtons"}>
                    <button onClick={() => this.props.z_callback(x, y)}>Find all Z</button>
                </div>
            </div>
        )
    }
}

export default BackdoorButtons