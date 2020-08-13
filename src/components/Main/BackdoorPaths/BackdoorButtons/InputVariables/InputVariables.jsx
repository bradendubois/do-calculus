import React from "react"

import "./InputVariables.scss"

const InputVariables = (setLabel, callback) => {

    const [gettingInput, toggleGettingInput] = React.useState(true)
    const [inputVariables, updateInputVariables] = React.useState()

    const validateInput = (variables) => {

    }

    return (
        <div>
            {gettingInput &&
                <>
                    <textarea placeholder={"Enter set " + setLabel + ", separated by commas..."} value={inputVariables} />
                    <button onClick={() => validateInput()}>Confirm</button>
                </>}
        </div>
    )
}