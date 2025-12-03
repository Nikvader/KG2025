function rgbToCmyk(r, g, b) {
    if (r === 0 && g === 0 && b === 0) {
        return { c: 0, m: 0, y: 0, k: 100 };
    }
    if(r>255){r=255}
    if(r<0){r=0}
    if(g>255){g=255}
    if(g<0){g=0}
    if(b>255){b=255}
    if(b<0){b=0}

    
    let c = 1 - (r / 255);
    let m = 1 - (g / 255);
    let y = 1 - (b / 255);
    const k = Math.min(c, m, y);
    c = Math.round(((c - k) / (1 - k)) * 100);
    m = Math.round(((m - k) / (1 - k)) * 100);
    y = Math.round(((y - k) / (1 - k)) * 100);
    return { c, m, y, k: Math.round(k * 100) };
}

function cmykToRgb(c, m, y, k) {
        if(c>100){c=100}
        if(c<0){c=0}
        if(m>100){m=100}
        if(m<0){m=0}
        if(y>100){y=100}
        if(y<0){y=0}
        if(k>100){k=100}
        if(k<0){k=0}
    c /= 100; m /= 100; y /= 100; k /= 100;
    const r = Math.round(255 * (1 - c) * (1 - k));
    const g = Math.round(255 * (1 - m) * (1 - k));
    const b = Math.round(255 * (1 - y) * (1 - k));
    return { r, g, b };
}

function rgbToHsv(r, g, b) {
        if(r>255){r=255}
    if(r<0){r=0}
    if(g>255){g=255}
    if(g<0){g=0}
    if(b>255){b=255}
    if(b<0){b=0}
    r /= 255; g /= 255; b /= 255;
    let max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, v = max;
    let d = max - min;
    s = max === 0 ? 0 : d / max;
    if (max === min) {
        h = 0; // achromatic
    } else {
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }
    return { h: Math.round(h * 360), s: Math.round(s * 100), v: Math.round(v * 100) };
}

function hsvToRgb(h, s, v) {
    if(h<0){h=0}
    if(h>360){h=360}
    if(s<0){s=0}
    if(s>360){s=100}
    if(v<0){v=0}
    if(v>100){v=100}

    h /= 360; s /= 100; v /= 100;
    let r, g, b;
    let i = Math.floor(h * 6);
    let f = h * 6 - i;
    let p = v * (1 - s);
    let q = v * (1 - f * s);
    let t = v * (1 - (1 - f) * s);
    switch (i % 6) {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }
    return { r: Math.round(r * 255), g: Math.round(g * 255), b: Math.round(b * 255) };
}



// Флаг для предотвращения рекурсивных вызовов
let isUpdating = false;

// Cсылки на элементы интерфейса
const elements = {
    preview: document.getElementById('color-preview'),
    picker: document.getElementById('color-picker'),
    inputs: {
        c: document.getElementById('c-input'), m: document.getElementById('m-input'), y: document.getElementById('y-input'), k: document.getElementById('k-input'),
        r: document.getElementById('r-input'), g: document.getElementById('g-input'), b: document.getElementById('b-input'),
        h: document.getElementById('h-input'), s: document.getElementById('s-input'), v: document.getElementById('v-input'),
    },
    sliders: {
        c: document.getElementById('c-slider'), m: document.getElementById('m-slider'), y: document.getElementById('y-slider'), k: document.getElementById('k-slider'),
        r: document.getElementById('r-slider'), g: document.getElementById('g-slider'), b: document.getElementById('b-slider'),
        h: document.getElementById('h-slider'), s: document.getElementById('s-slider'), v: document.getElementById('v-slider'),
    }
};

// Главная функция обновления
function updateColors(source) {
    if (isUpdating) return; // Защита от рекурсии
    isUpdating = true;

    let rgb, cmyk, hsv;

    // Определяем исходные значения и приводим всё к RGB
    switch (source) {
        case 'cmyk':
            cmyk = { c: +elements.inputs.c.value, m: +elements.inputs.m.value, y: +elements.inputs.y.value, k: +elements.inputs.k.value };
            rgb = cmykToRgb(cmyk.c, cmyk.m, cmyk.y, cmyk.k);
            hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
            break;
        case 'hsv':
            hsv = { h: +elements.inputs.h.value, s: +elements.inputs.s.value, v: +elements.inputs.v.value };
            rgb = hsvToRgb(hsv.h, hsv.s, hsv.v);
            cmyk = rgbToCmyk(rgb.r, rgb.g, rgb.b);
            break;
        case 'picker':
            const hex = elements.picker.value;
            rgb = {
                r: parseInt(hex.slice(1, 3), 16),
                g: parseInt(hex.slice(3, 5), 16),
                b: parseInt(hex.slice(5, 7), 16)
            };
            cmyk = rgbToCmyk(rgb.r, rgb.g, rgb.b);
            hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
            break;
        case 'rgb':
        default:
            rgb = { r: +elements.inputs.r.value, g: +elements.inputs.g.value, b: +elements.inputs.b.value };
            cmyk = rgbToCmyk(rgb.r, rgb.g, rgb.b);
            hsv = rgbToHsv(rgb.r, rgb.g, rgb.b);
            break;
    }

 
    updateUI({ rgb, cmyk, hsv });
    isUpdating = false;
}


function updateUI(colors) {
    const { rgb, cmyk, hsv } = colors;

    const hexColor = `#${rgb.r.toString(16).padStart(2, '0')}${rgb.g.toString(16).padStart(2, '0')}${rgb.b.toString(16).padStart(2, '0')}`;
    elements.preview.style.backgroundColor = hexColor;
    elements.picker.value = hexColor;

    Object.keys(cmyk).forEach(key => elements.inputs[key].value = cmyk[key]);
    Object.keys(rgb).forEach(key => elements.inputs[key].value = rgb[key]);
    Object.keys(hsv).forEach(key => elements.inputs[key].value = hsv[key]);

    Object.keys(cmyk).forEach(key => elements.sliders[key].value = cmyk[key]);
    Object.keys(rgb).forEach(key => elements.sliders[key].value = rgb[key]);
    Object.keys(hsv).forEach(key => elements.sliders[key].value = hsv[key]);
}


// Событие input срабатывает мгновенно при любом изменении
document.getElementById('cmyk-group').addEventListener('input', () => updateColors('cmyk'));
document.getElementById('rgb-group').addEventListener('input', () => updateColors('rgb'));
document.getElementById('hsv-group').addEventListener('input', () => updateColors('hsv'));
elements.picker.addEventListener('input', () => updateColors('picker'));

// Начальный цвет
document.addEventListener('DOMContentLoaded', () => {
    elements.inputs.r.value = 255;
    elements.inputs.g.value = 0;
    elements.inputs.b.value = 0;
    updateColors('rgb');
});