import React from "react"

import "./InfoBox.scss"

class InfoBox extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            warnings: [],
            errors: [],
            messages: []
        }

        this.receive_error = this.receive_error.bind(this)
        this.clear = this.clear.bind(this)
    }

    receive_warning(warning_message) {
        let cur = this.state.warnings
        cur.push(warning_message)
        this.setState({warnings: cur})
    }

    receive_error(error_message) {
        let cur = this.state.errors
        cur.push(error_message)
        this.setState({errors: cur})
    }

    receive_message(message) {
        let cur = this.state.messages
        cur.push(message)
        this.setState({messages: cur})
    }

    clear() {
        this.setState({errors: []})
    }

    render() {
        return (
            <div>
                <h3>Warnings</h3>
                <ul>
                    {this.state.warnings.length > 0 ?
                        this.state.warnings.map(warning => <li>{warning}</li>) : <p>Looks good so far...</p>}
                </ul>
                <h3>Errors</h3>
                <ul>
                    {this.state.errors.length > 0 ?
                        this.state.errors.map(error => <li>{error}</li>) : <p>Looks good so far...</p>}
                </ul>
                <h3>Messages</h3>
                <ul>
                    {this.state.messages.length > 0 ?
                        this.state.messages.map(message => <li>{message}</li>) : <p>Looks good so far...</p>}
                </ul>
            </div>
        )
    }
}

export default InfoBox