import React from "react"

import "./InfoBox.scss"

class InfoBox extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            errors: []
        }

        this.receive_error = this.receive_error.bind(this)
        this.clear = this.clear.bind(this)
    }

    receive_error(error_message) {
        let cur = this.state.errors
        cur.push(error_message)
        this.setState({errors: cur})
    }

    clear() {
        this.setState({errors: []})
    }

    render() {
        return (
            <div>
                <h3>Info / Errors</h3>
                <ul>
                    {this.state.errors.map(error => <li>{error}</li>)}
                </ul>
            </div>
        )
    }
}

export default InfoBox