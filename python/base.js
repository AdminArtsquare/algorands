const server_api = "http://127.0.0.1:5000/";
async function callApi(form, method, data = {}, type = "POST"){

    const formData = new FormData(form);

    formData.append('unit_name', data['unit_name']);
    formData.append('asset_name', data['asset_name']);
    formData.append('total', data['total']);
    formData.append('description', data['description']);
        
    var url = server_api + method;

    try{
        $("#form_submit").attr("disabled", true);
        var result = await $.ajax({
            url: url,
            type: type,
            data: formData,
            processData: false,
            contentType: false
        });
        
        $("#container").append(JSON.stringify(result) + "\n");
    }catch(error){
        console.error(error.statusText);
        $("#container").append("connection_error" + "\n");
    }finally{
        $("#form_submit").attr("disabled", false);
    }
}
function allDataFilled(){
    return ($("#unit_name").val().length > 0) &&
        ($("#asset_name").val().length > 0) &&
        ($("#total").val().length > 0) &&
        ($("#description").val().length > 0);
}