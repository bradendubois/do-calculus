

navigation = document.getElementById("tabs")
Array.prototype.forEach.call(navigation.childNodes, node => {

    let id = node.id;
    let page = id + "-page"

    node.addEventListener("click", () => {

        console.log(id, page)

        // Remove "shown" from everything
        let elements = document.querySelectorAll(".shown");
        Array.prototype.forEach.call(elements, (element) => {
            element.classList.remove("shown");
        })

        // Add "shown" class
        document.getElementById(id).classList.add("shown");
        document.getElementById(page).classList.add("shown");
    })
})
