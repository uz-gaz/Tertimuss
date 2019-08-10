let number_arguments = process.argv.length;
if (number_arguments === 4){
    // Check if number of arguments is correct
    let input_path =12;
    console.log(number_arguments);
    console.log("Esto es una prueba");
}
else {
    let path = require('path');
    let filename = path.basename(__filename);

    // Input error
    console.log("Error: You must specify the input path and the output path \n" +
        "\t Usage: node " + filename + " \"input path\" \"output path\"");
}
