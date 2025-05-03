module.exports = function override(config, env) {
  // Add webpack polling configuration
  config.watchOptions = {
    poll: 1000, // Check for changes every second
    aggregateTimeout: 300, // Delay before rebuilding
    ignored: /node_modules/,
  };

  return config;
};