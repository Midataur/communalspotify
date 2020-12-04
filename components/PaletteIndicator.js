const PaletteIndicator = ({paletteStr, profileInUse}) => {
    
    if (paletteStr == false) {return html`
    <div class="fixed top-0 right-0 border-l-2 border-b-2 border-page-contrast z-40">
        <div class="tracking-wider px-2 bg-page-contrast text-page-bg">COLOUR PALETTE</div>
        <div class="px-2">Loading...</div>
    </div>
    
    `}
    
    
    const palette = JSON.parse(paletteStr)
    console.log(palette)
    const lines = Object.keys(palette).map((key) => {
        const rgbArray = palette[key].rgb
        const rgbColor = `rgb(${rgbArray.join(",")})`
        const lColor = RGBtoHSL(rgbArray[0], rgbArray[1], rgbArray[2])[2]
        const textColor = lColor >= 0.6 ? "text-black" : "text-white"
        return html`
        <div class="px-2 ${textColor}" style="background-color: ${rgbColor}">
            ${profileInUse === key ? '· ' : ''}${key}
        </div>`
        
    })
    
    return (
        html`
            <div class="fixed top-0 right-0 border-l-2 border-b-2 border-page-contrast">
                <div class="tracking-wider px-2 bg-page-contrast text-page-bg">COLOUR PALETTE</div>
                ${lines}
            </div>
        `
    );
}

export default PaletteIndicator;
