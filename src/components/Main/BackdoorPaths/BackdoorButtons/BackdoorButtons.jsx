import React from "react"

import "./BackdoorButtons.scss"

class BackdoorButtons extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            getInput: true,
            x: this.props.x,
            y: this.props.y,
            z: this.props.z
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps.x.length !== this.props.x.length || prevProps.y.length !== this.props.y.length || prevProps.z.length !== this.props.z.length) {
            this.setState({
                x: this.props.x,
                y: this.props.y,
                z: this.props.z
            })
        }
    }

    render() {
        return (
            <div className={"debug backdoorButtons"}>
                <div className={"buttonHeader"}>

                    <div>{this.state.x.map(x => <p>{x}</p>)}</div>
                    <button onClick={() => this.props.clear("X")}>Clear X</button>

                    <div>{this.state.y.map(y => <p>{y}</p>)}</div>
                    <button onClick={() => this.props.clear("Y")}>Clear Y</button>

                    <div>{this.state.z.map(z => <p>{z}</p>)}</div>
                    <button onClick={() => this.props.clear("Z")}>Clear Z</button>

                </div>
                <div className={"backdoorMainButtons"}>
                    <button onClick={() => this.props.path_callback()}>Find Backdoor Paths with Given Data</button>
                    <button onClick={() => this.props.z_callback()}>Find all for given X, Y</button>
                </div>
            </div>
        )
    }
}

export default BackdoorButtons