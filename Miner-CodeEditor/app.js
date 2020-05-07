

var express = require ('express');
var app = express();
var http = require('http');
var bodyParser = require('body-parser');
const fs = require('fs')
const { exec } = require('child_process');
var process = require('process');

var PORT = process.env.PORT || 5000;
var server = http.createServer(app);

app.use(express.static(__dirname));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
  extended: true
}));

app.get('/', function(req, res)
{
    //res.sendFile('index.html', { root: __dirname });
    res.redirect('index.html');
});

app.post('/compile', function(req, res){

    var language = req.body.language;
    var code = req.body.code;

    if(language == "python"){
      process.chdir('languages/Python');
      fs.writeFileSync('temp.py', code);
    }
    else if (language == "java"){
      process.chdir('languages/Java');

      // change the class name to temp. We need it to be temp because the file used in Docker is temp.java
      var split = code.split(" ");
      var indexOf_class = split.indexOf("class");
      split[indexOf_class+1] = "temp"
      code = split.join(" ")

      fs.writeFileSync('temp.java', code);
    }
    else{
      res.send("Please choose a language");
      return;

    }


    exec("docker build -t tempdocker .", (error, stdout, stderr) => {
    if (error) {
        console.log(`error: ${error.message}`);
        process.chdir('../..');
        return;
    }
    if (stderr) {
        console.log(`stderr: ${stderr}`);
        process.chdir('../..');
        return;
    }
    console.log(`stdout: ${stdout}`);

    exec("docker run tempdocker", (error, stdout, stderr) => {
    if (error) {
        console.log(`error: ${error.message}`);
        res.send(error.message);
        process.chdir('../..');
        return;
    }
    if (stderr) {
        console.log(`stderr: ${stderr}`);
        res.send(stderr);
        process.chdir('../..');
        return;
    }
    process.chdir('../..');
    res.send(stdout);
    });

    });



});

server.listen(PORT, () => console.log('Server started '));
