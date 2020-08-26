import React from "react"

import "./BackdoorOutput.scss"

const BackdoorOutput = ({ messages }) =>

    <div className={"tile backdoorOutput"}>
        Output / Warnings
        <ul>
            {messages.map(message => <li>{message}</li>)}
        </ul>
    </div>

export default BackdoorOutput
