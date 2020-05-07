var editor = CodeMirror(document.getElementById("text-editor"), {
    lineNumbers: true,
	   name: "text/x-cython",
	   matchBrackets: true
  })
 editor.setSize(null, 650);

var usertext;
var language;

$("#languages a").click(function(e){
    e.preventDefault(); // cancel the link behaviour
    language = $(this).text();
    $("#languages-btn").text(language);
});

var run_button = document.getElementById("run-button");

run_button.onclick = function(){

   //clears the contents of the output area
   document.getElementById("output").innerHTML = "";

    var code = editor.getValue();
    var json = {
        language: language,
        code: code
    };

    console.log(json);

    $.post("/compile", json, function(data, error, xhr) {

            document.getElementById("output").innerHTML = data;
    });

};

window.onbeforeunload = function(){
	sessionStorage.setItem('input', editor.getValue());
}
window.onload = function(){
	editor.setValue(sessionStorage.getItem('input'));
}


// After choosing the file to upload, changes the text to the file name chosen
document.querySelector('.custom-file-input').addEventListener('change',function(e){

  var fileName = document.getElementById("myInput").files[0].name;
  var nextSibling = e.target.nextElementSibling
  nextSibling.innerText = fileName
})


function load(file){
    var reader = new FileReader();
    reader.onload = function(e) {
    editor.setValue(e.target.result);
}
reader.readAsText(file.files[0]);}

function saveOutput() {
  output = document.getElementById("output").textContent;
	var bl = new Blob([output], {type:"text/plain"});
	var fn = document.getElementById("chosenfilename-output").value;
	if (window.navigator.msSaveOrOpenBlob)
        window.navigator.msSaveOrOpenBlob(bl, fn);
    else {
        var a = document.createElement("a"),
        url = URL.createObjectURL(bl);
        a.href = url;
        a.download = fn;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }, 0);
    }
 }

 function saveCode() {
  usertext = editor.getValue();
 	var bl = new Blob([usertext], {type:"text/plain"});
 	var fn = document.getElementById("chosenfilename-code").value;
 	if (window.navigator.msSaveOrOpenBlob)
         window.navigator.msSaveOrOpenBlob(bl, fn);
     else {
         var a = document.createElement("a"),
         url = URL.createObjectURL(bl);
         a.href = url;
         a.download = fn;
         document.body.appendChild(a);
         a.click();
         setTimeout(function() {
             document.body.removeChild(a);
             window.URL.revokeObjectURL(url);
         }, 0);
     }
  }
