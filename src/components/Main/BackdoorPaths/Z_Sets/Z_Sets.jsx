import React, { useState, useEffect } from "react"

import "./Z_Sets.scss"

/*
const stringify = (x, y, z) => {

    x.sort()
    y.sort()
    z.sort()

    // TODO - Import a font such that ⫫ can be properly rendered
    let message = x.join(", ") + " _||_ " + y.join(", ");
    if (z.length > 0)
        message += " | " + z.join(", ")
    return message
}

const Z_Sets = ({ content }) => {

    const [value, setValue] = useState(content);

    useEffect(() => { setValue(content) }, [content]);

    return (
        <div className={"tile z_sets"}>
            <h3>Paths Computed</h3>
            <ul>
                {value["responses"].map(z_response =>
                    z_response["sufficient"] ?
                        <li>{stringify(value["x"], value["y"], z_response.z)}</li>
                        :
                        <details>
                            <summary>{stringify(value["x"], value["y"], z_response["z"])}</summary>
                            {z_response["paths"].map(path => <li>{path}</li>)}
                        </details>
                )}
            </ul>
        </div>
    )
}

*/

class Z_Sets extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            content: this.props.content
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        if (prevProps.content.length !== this.props.content.length) {
            this.setState({content: this.props.content})
        }
    }

    render() {
        return (
            <div className={"tile z_sets"}>
                <h3>Z (De-confounding) Sets</h3>
                <ul>
                    {this.state.content.map(x => <li>{x}</li>)}
                </ul>
            </div>
        )
    }
}

export default Z_Sets