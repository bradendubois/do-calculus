import * as React from 'react'

import "./Main.scss"


class Main extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            active: "None"
        }

        this.setActive = this.setActive.bind(this)
    }

    setActive(page) {
        this.setState({active: page})
    }

    render() {

        return (
            <div>
                {this.state.active}
            </div>
        )
    }
}

export default Main;