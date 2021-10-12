// method for printing logs in textarea and console
function addLog(text, new_line = true){
    text = JSON.stringify(text);
    if(new_line)
        $("#textarea").append(text + "\n");
    else
        $("#textarea").append(text);
    console.log(text);
}