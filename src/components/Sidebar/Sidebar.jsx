import * as React from 'react'

import "./Sidebar.scss"

class Sidebar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            active: ""
        }

        this.content = [
            ["graphData", <>Graph Data</>],
            ["probabilityQuery", <>Probability Query</>],
            ["doCalculus", <><i>do</i>-Calculus</>],
            ["backdoorPath", <>Backdoor Paths</>]
        ]

        this.setActive = this.setActive.bind(this)
        this.revealButton = this.revealButton.bind(this)
        setTimeout(this.revealButton, 1000, 0)
    }

    setActive(section) {

        if (this.state.active !== "") {
            document.getElementById(this.state.active + "-button").classList.remove("active")
            // document.getElementById(this.state.active + "Container").classList.remove("currentContent")
        }

        this.setState({active: section})

        this.props.mainRef.current.setActive(section)

        let pageElement = document.getElementById(section + "Container")
        if (pageElement) {
            // pageElement.classList.add("currentContent")
        }

        let buttonID = section + "-button"
        document.getElementById(buttonID).classList.add("active")
    }

    revealButton(button_index) {
        document.getElementById(this.content[button_index][0] + "-button").classList.add("revealed")
        if (button_index < this.content.length - 1) {
            setTimeout(this.revealButton, 1000, button_index + 1)
        }
    }

    render() {

        return (
            <div className={"sidebar"}>
                {this.content.map(entry =>
                    <button id={entry[0] + "-button"} onClick={() => this.setActive(entry[0])}>{entry[1]}</button>)
                }
                <button
                    id={"unloadButton"}
                    onClick={() => this.props.callback()}
                >Unload Graph</button>
            </div>

        )
    }
}


export default Sidebar;