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
        if (prevProps.x.length !== this.props.x.length ||
            prevProps.y.length !== this.props.y.length ||
            prevProps.z.length !== this.props.z.length)
        {
            this.setState({
                x: this.props.x,
                y: this.props.y,
                z: this.props.z
            })
        }
    }

    render() {
        return (
            <div className={"tile backdoorButtons"}>
                <div className={"buttonHeader"}>

                    {[
                        [this.state.x, "X",  "interventions"],
                        [this.state.y, "Y", "outcomes"],
                        [this.state.z, "Z", "covariates/deconfounders"]
                    ].map(s =>
                        <div className={"setContainer"}>
                            <div className={"setItems"} title={"This is a set " + s[1] + ", our " + s[2] + "."}>
                                {s[0].map(i => <p>{i}</p>)}
                            </div>
                            <button title={"Clear all " + s[2]} onClick={() => this.props.clear(s[1])}
                            >Clear {s[1]}</button>
                        </div>
                    )}

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