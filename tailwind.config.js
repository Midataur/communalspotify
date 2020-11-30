// dont mess around with this, please.
module.exports = {
  future: {
    removeDeprecatedGapUtilities: true,
    purgeLayersByDefault: true,
  },
  purge: {
    content: [
      './templates/**/*.html', 
      './templates/**/*.js',
      './components/**/*.js'
    ],
  },
  theme: {
    aspectRatio: {
      'square':[1,1]
    },
    extend: {
      
    },
  },
  variants: {},
  plugins: [
    require('tailwindcss-aspect-ratio')
  ],
}
