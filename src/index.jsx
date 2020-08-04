import React from 'react'
import ReactDOM from 'react-dom'

import Header from './components/Header/Header'
import Editor from './components/Editor/Editor'
import FileSelector from "./components/FileSelector/FileSelector";

import Sidebar from "./components/Sidebar/Sidebar"
import Main from "./components/Main/Main"

import './index.scss'





class App extends React.Component {


    constructor(props) {
        super(props)
        this.state = {
            selected: false
        }


        this.sidebarRef = React.createRef();
        this.mainRef = React.createRef();

        // this.sidebar = <Sidebar ref={this.sidebarRef}/>
        // this.main = <Main ref={this.mainRef}/>

        this.load = this.load.bind(this);
    }

    load(graph) {
        window.pywebview.api.load_file(graph)
        this.setState({selected: true})
    }

    render() {
        return (
            <div>
                {this.state.selected && <div className={"full"}>
                    <Sidebar mainRef={this.mainRef}/>
                    <Main ref={this.mainRef}/>
                </div>}
                {!this.state.selected && <FileSelector callback={this.load}/>}
            </div>
        )
    }
}


const view = <App props={"pywebview"}/>

const element = document.getElementById('app')
ReactDOM.render(view, element)