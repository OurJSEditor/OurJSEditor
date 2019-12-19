const { readdirSync } = require("fs");
const path = require("path");


const fileRegex =  /^(.+).jsx?$/;
const entry = readdirSync("./js/entries/").filter(fileRegex.test.bind(fileRegex)).reduce((obj, entry) => {
    const [, name] = fileRegex.exec(entry) || [console.error("ERROR: %s DID NOT MATCH REGEX", entry)];
    obj[name] = `./js/entries/${entry}`;
    return obj;
}, {});

module.exports = {
    entry,
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "js/build/jsx-components")
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: path.resolve(__dirname, "node_modules"),
                include: path.resolve(__dirname, "js"),
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["react", "es2015"],
                        plugins: [
                            ["transform-react-jsx", { "pragma": "Preact.h" }]
                        ]
                    },
                },
            }
        ]
    },
    resolve: {
        extensions: [".js", ".jsx"]
    },
};
