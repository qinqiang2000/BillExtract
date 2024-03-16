let scale = 1;
let rotation = 0;

function zoomIn() {
    scale *= 1.1;
    updateTransform();
}

function zoomOut() {
    scale /= 1.1;
    updateTransform();
}

function rotate() {
    rotation += 90;
    updateTransform(false);
}

function updateTransform(zoom=true) {
    const image = document.getElementById('preview-image');
    image.style.transform = `scale(${scale}) rotate(${rotation}deg)`;
}
