import React from 'react'
import ReactDOM from 'react-dom'

import FileSelector from "./components/FileSelector/FileSelector";
import Sidebar from "./components/Sidebar/Sidebar"
import Main from "./components/Main/Main"

import './index.scss'

class App extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            selected: false,
            webviewReady: true // TODO
        }

        this.sidebarRef = React.createRef()
        this.mainRef = React.createRef()

        // this.sidebar = <Sidebar ref={this.sidebarRef}/>
        // this.main = <Main ref={this.mainRef}/>

        this.load = this.load.bind(this)
        this.unload = this.unload.bind(this)
    }

    load(graph) {
        window.pywebview.api.load_file(graph).then(() => {
            let selector = document.getElementById("fileSelectorContainer");
            selector.style.animationName = "slideAway"
            selector.style.animationDuration = "2.0s";

            let content = document.getElementById("content")
            setTimeout(() => {
                this.setState({selected: true})
                content.style.animationName = "slideIn"
                content.style.animationDuration = "1.0s"
            }, 2000)
        })
    }

    unload() {

        // let selector = document.getElementById("fileSelectorContainer")
        // selector.style.animationName = ""

        // let content = document.getElementById("content")
        // content.style.animationName = ""

        this.setState({selected: false})
    }

    render() {
        return (
            <div id={"probability-app"}>
                {this.state.webviewReady &&
                    <div id={"content"}>
                        {this.state.selected &&
                            <>
                                <Sidebar mainRef={this.mainRef} callback={this.unload}/>
                                <Main ref={this.mainRef}/>
                            </>
                        }
                        {!this.state.selected && <FileSelector callback={this.load}/>}
                    </div>
                }
            </div>
        )
    }
}


const view = <App props={"pywebview"}/>

const element = document.getElementById('app')
ReactDOM.render(view, element)