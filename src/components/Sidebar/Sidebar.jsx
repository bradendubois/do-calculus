import * as React from 'react'

import "./Sidebar.scss"

class Sidebar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {}

        this.mainRef = this.props.mainRef

        this.button_ids = [
            "graphDataPageButton",
            "probabilityQueryPageButton",
            "doCalculusPageButton",
            "backdoorPathsPageButton"
        ]

        this.setActive = this.setActive.bind(this)
        this.revealButton = this.revealButton.bind(this)
        setTimeout(this.revealButton, 1000, 0)
    }

    setActive(page) {
        this.mainRef.current.setActive(page)
    }

    revealButton(button_index) {
        document.getElementById(this.button_ids[button_index]).classList.add("revealed")
        if (button_index < this.button_ids.length - 1) {
            setTimeout(this.revealButton, 1000, button_index + 1)
        }
    }

    render() {
        return (
            <div className={"sidebar"}>
                <button id={"graphDataPageButton"} onClick={() => this.setActive("Graph Data")}>Graph Data</button>
                <button id={"probabilityQueryPageButton"} onClick={() => this.setActive("Probability Query")}>Probability Query</button>
                <button id={"doCalculusPageButton"} onClick={() => this.setActive("Do-Calculus")}>Do-Calculus</button>
                <button id={"backdoorPathsPageButton"} onClick={() => this.setActive("Backdoor Paths")}>Backdoor Paths</button>
            </div>

        )
    }
}


export default Sidebar;