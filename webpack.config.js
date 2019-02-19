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
        path: path.resolve(__dirname, "static/scripts/components")
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: path.resolve(__dirname, "node_modules"),
                include: path.resolve(__dirname, "js"),
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["react", "es2015"]
                    },
                },
            }
        ]
    },
    resolve: {
        extensions: [".js", ".jsx"]
    },
};