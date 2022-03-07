const READTHEDOCS_SIDEBAR_ELEMENT_ID = "furo-readthedocs-versions";

const remove_readthedocs_element = () => {
    const element = document.getElementById(READTHEDOCS_SIDEBAR_ELEMENT_ID);
    try {
        element.parentNode.removeChild(element);
    } catch (e) {
        // pause and try again
        console.log(e);
        setTimeout(remove_readthedocs_element, 400);
    }
}

window.onload = () => {
    remove_readthedocs_element()
}
