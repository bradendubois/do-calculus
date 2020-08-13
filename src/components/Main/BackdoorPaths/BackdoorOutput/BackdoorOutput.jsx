import React from "react"

import "./BackdoorGraph.scss"

class BackdoorGraph extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <div className={"debug backdoorOutput"}>
                    BackdoorOutput
                </div>
            </div>
        )
    }
}

export default BackdoorGraphA