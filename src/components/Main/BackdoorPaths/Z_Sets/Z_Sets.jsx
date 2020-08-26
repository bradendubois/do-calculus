import React, { useState, useEffect } from "react"

import "./Z_Sets.scss"

const Z_Sets =({ content }) =>

    <div className={"tile z_sets"}>
        <h3>Z (De-confounding) Sets</h3>
        <ul>
            {content.map(x => <li>{x}</li>)}
        </ul>
    </div>

export default Z_Sets
