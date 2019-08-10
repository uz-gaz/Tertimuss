// Imports
const ref_parser = require("json-schema-ref-parser");
const fs = require('fs');
const path = require('path');

// Get number of arguments
let number_arguments = process.argv.length;

// Check if number of arguments is correct
if (number_arguments === 4) {
    const input_path = process.argv[2];
    const output_path = process.argv[3];

    ref_parser.dereference(input_path, (err, schema) => {
        if (err) {
            console.error("Error: " + err);
            return 1;
        } else {
            // stringify JSON Object
            let json_content = JSON.stringify(schema);

            fs.writeFile(output_path, json_content, 'utf8', function (err) {
                if (err) {
                    console.log("Error: An error occured while writing JSON Object to File");
                    return 1;
                } else {
                    console.log("JSON file has been parsed");
                }
            });
        }
    });
    console.log("Lo que hay al final")
} else {
    // Get name of the script
    const filename = path.basename(__filename);

    // Input error
    console.log("Error: You must specify the input path and the output path \n" +
        "\t Usage: node " + filename + " \"input path\" \"output path\"");

    return 1;
}
