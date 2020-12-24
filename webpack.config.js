const path = require('path');

module.exports = (env = {mode: "production", presets: []}) => {
  return {
    mode: env.mode,
    entry: './js/index.js',
    output: {
        path: path.join(__dirname, './backend/quizzz/static'),
        filename: (env.mode === 'production') ? 'bundle.min.js' : "bundle.js",
        library: "jsFuncs"
    }
  }
};
