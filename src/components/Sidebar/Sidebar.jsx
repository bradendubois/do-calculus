import * as React from 'react'

import "./Sidebar.scss"

class Sidebar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            text: "not pow",
            buttons: [
                <button onClick={() => this.setActive("Graph Data")}>Graph Data</button>,
                <button onClick={() => this.setActive("Probability Query")}>Probability Query</button>,
                <button onClick={() => this.setActive("Do-Calculus")}>Do-Calculus</button>,
                <button onClick={() => this.setActive("Backdoor Paths")}>Backdoor Paths</button>
            ]
        }

        this.mainRef = this.props.mainRef

        this.setActive = this.setActive.bind(this)
        // this.revealButton = this.revealButton.bind(this)
        //setTimeout(this.revealButton, 1000, 0)
    }

    setActive(page) {
        this.mainRef.current.setActive(page)
    }

    revealButton(button_index) {

        let copied = this.state.buttons;
        let button = this.buttons[button_index]
        // console.log(button);
        // button.setAttribute("className", "shown");// = "shown"
        copied.push(this.buttons[button_index])
        this.setState({buttons: copied})

        if (button_index < this.state.buttons.length - 1) {
            setTimeout(this.revealButton, 1000, button_index + 1)
        }
    }

    render() {
        return (
            <div>
                <h1>Sidebar</h1>
                {this.state.buttons}
            </div>

        )
    }
}


export default Sidebar;