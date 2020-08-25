import React from "react"

import "./BackdoorOutput.scss"

class BackdoorOutput extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className={"tile backdoorOutput"}>
                BackdoorOutput
                <ul>
                    {this.props.messages.map(message =>
                        <li>
                            {message}
                        </li>
                    )}
                </ul>
            </div>
        )
    }
}

export default BackdoorOutput