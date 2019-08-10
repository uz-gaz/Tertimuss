const $RefParser = require("json-schema-ref-parser");
// file system module to perform file operations
const fs = require('fs');

mySchema = "input-schema.json";
$RefParser.dereference(mySchema, (err, schema) => {
  if (err) {
    console.error(err);
  }
  else {
    // parse json
    // var jsonObj = JSON.parse(jsonData);

    // stringify JSON Object
    var jsonContent = JSON.stringify(schema);
    console.log(jsonContent);
 
    fs.writeFile("output.json", jsonContent, 'utf8', function (err) {
    if (err) {
        console.log("An error occured while writing JSON Object to File.");
        return console.log(err);
    }
 
    console.log("JSON file has been saved.");
});
  }
})