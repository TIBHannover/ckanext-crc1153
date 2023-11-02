$(document).ready(function(){
    
    $('#push-to-sparql-btn').click(function(){
        let endPoint = $('#push-to-sparql-url').val();
        $.ajax({
            url: endPoint,
            method: "GET",  
            dataType: "json",          
            success: function(responseData) {              
              if (responseData["_result"]){
                createSuccessAlert();

              }
            },
            error: function(jqXHR, textStatus, errorThrown) {              
              createFailAlert();
            }
          });
    });


    $('#delete-sparql-btn').click(function(){
        let endPoint = $('#delete-sparql-url').val();
        $.ajax({
            url: endPoint,
            method: "GET",
            dataType: "json",            
            success: function(responseData) {  
                console.info(responseData)            
              if (responseData["_result"]){
                createSuccessAlert();

              }
            },
            error: function(jqXHR, textStatus, errorThrown) {              
              createFailAlert();
            }
          });
    });



});



function createSuccessAlert(){
    let alertDiv = document.createElement("div");
    alertDiv.classList.add("alert", "alert-success");
    let strongElement = document.createElement("strong");
    strongElement.textContent = "Job is in queue!";
    let textNode = document.createTextNode(" It may take some time to finish. You can check the result in the CKAN log.");    
    alertDiv.appendChild(strongElement);
    alertDiv.appendChild(textNode);
    let container = document.getElementById("alert_container");
    container.appendChild(alertDiv);
}



function createFailAlert(){
    let alertDiv = document.createElement("div");
    alertDiv.classList.add("alert", "alert-danger");
    let strongElement = document.createElement("strong");
    strongElement.textContent = "Something wen wrong!";
    let textNode = document.createTextNode("Please try later or check CKAN for possible bugs/issues!");    
    alertDiv.appendChild(strongElement);
    alertDiv.appendChild(textNode);
    let container = document.getElementById("alert_container");
    container.appendChild(alertDiv);
}