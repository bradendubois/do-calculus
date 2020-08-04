import React from 'react'
import ReactDOM from 'react-dom'

import Header from './components/Header/Header'
import Editor from './components/Editor/Editor'
import FileSelector from "./components/FileSelector/FileSelector";

import './index.scss'


const App = function() {

    function load(graph) {
        console.log(graph)
        // window.pywebview.api.load_file(graph)
    }

    return (
    <>
      <Header/>
      <Editor/>
      <FileSelector callback={load}/>
    </>
  )
}

const view = App('pywebview')

const element = document.getElementById('app')
ReactDOM.render(view, element)