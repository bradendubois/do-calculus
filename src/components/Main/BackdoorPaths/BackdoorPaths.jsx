import React from "react"

import BackdoorButtons from "./BackdoorButtons/BackdoorButtons";
import BackdoorGraph from "./BackdoorGraph/BackdoorGraph";
import Z_Sets from "./Z_Sets/Z_Sets";
import BackdoorOutput from "./BackdoorOutput/BackdoorOutput";


import "./BackdoorPaths.scss"

class BackdoorPaths extends React.Component {

    constructor(props) {
        super(props);

        this.find_all_z = this.find_all_z.bind(this)
    }

    find_all_z(x, y) {

    }

    render() {
        return (
            <div className={"contentSection"} id={"backdoorPathContainer"}>
                <BackdoorButtons z_callback={this.find_all_z} />
                <BackdoorGraph />
                <Z_Sets />
                <BackdoorOutput />
            </div>
        )
    }
}

export default BackdoorPaths