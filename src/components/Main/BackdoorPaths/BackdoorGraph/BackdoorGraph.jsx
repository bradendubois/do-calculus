import React from "react"

import "./BackdoorGraph.scss"

class BackdoorGraph extends React.Component {

    constructor(props) {
        super(props);

        window.pywebview.api.v_to_parents_and_children().then(response => {
            console.log(response)
        })
    }

    render() {
        return (
            <div className={"debug backdoorGraph"}>
                {this.table}
            </div>
        )
    }
}

export default BackdoorGraph