// All imported files in the document
const links = document.querySelectorAll('link[rel="import"]')

// "Main" area of the page
const main = document.getElementById("main")

// Import and add each page to the DOM
Array.prototype.forEach.call(links, (link) => {

    console.log("Link:", link)

    let template = link.getElementsByTagName('section')
    for (let t of template) {
        console.log(t)
    }

    console.log("Content: ", template)

    console.log(template)
    let clone = document.importNode(template.content, true)
    main.appendChild(clone)
})
