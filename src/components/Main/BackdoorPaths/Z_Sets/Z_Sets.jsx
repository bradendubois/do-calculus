import React from "react"

import "./Z_Sets.scss"

class Z_Sets extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            xyz: []
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {

    }



    render() {
        return (
            <div className={"debug z_sets"}>
                <ul>
                    {this.props.content}
                </ul>
            </div>
        )
    }
}

export default Z_Sets