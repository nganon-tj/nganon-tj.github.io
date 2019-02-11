function report() {
    let dataTag = document.getElementById('data');
    return JSON.parse(dataTag.innerHTML);
}

export {report}