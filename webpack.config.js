const path = require("path");
const nodeExternals = require("webpack-node-externals");
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  target: "node",
  entry: {
    app: ["./app.js"],
  },
  output: {
    path: path.resolve(__dirname, "./build"),
    filename: "app.js",
  },
  externals: [nodeExternals()],
  plugins: [
    new CopyPlugin({
      patterns: [
        {
          from: "./package.json",
          to: "./package.json",
        },
        {
          from: "./.env.production",
          to: "./.env.production",
        },
        {
          from: "./.env.test",
          to: "./.env.test",
        },
      ],
    }),
  ],
};
