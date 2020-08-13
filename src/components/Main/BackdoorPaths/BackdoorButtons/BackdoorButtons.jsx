import React from "react"

import "./BackdoorButtons.scss"

class BackdoorButtons extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            getInput: true,
            x: this.props.x,
            y: this.props.y
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps.x.length !== this.props.x.length || prevProps.y.length !== this.props.y.length) {
            this.setState({
                x: this.props.x,
                y: this.props.y
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
                </div>
                <div className={"backdoorMainButtons"}>
                    <button onClick={() => this.props.z_callback()}>Find all Z</button>
                </div>
            </div>
        )
    }
}

export default BackdoorButtons