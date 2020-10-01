// dont mess around with this, please.
module.exports = {
  future: {
    removeDeprecatedGapUtilities: true,
    purgeLayersByDefault: true,
  },
  purge: {
    content: [
      './templates/**/*.html', 
      './templates/**/*.js'
    ],
  },
  theme: {
    extend: {},
  },
  variants: {},
  plugins: [],
}
