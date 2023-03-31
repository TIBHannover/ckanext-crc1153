$(window).on('pageshow', function(){
  if($("#reload_page").val() === "yes"){    
    window.location.href = window.location.href;
  }
});

$(document).ready(function(){

    var skipWarning = false;
    // ser resource count (for the data resources that already have the metadata values in them)
    let all_modals_save_btn = $('.res_custom_metadat_modal_save');
    for(let i=0; i<all_modals_save_btn.length; i++){
        setResourceCount(all_modals_save_btn[i]);
    }


    $('.resource-custom-metadata-modal').on('shown.bs.modal', function () {
        let id = $(this).attr('id');
        let field_name_box_and_id = id.split('resourcesModal_')[1];
        $('#modal-header-name-' + field_name_box_and_id).text($('#' + field_name_box_and_id).val());
    })

    /**
     * Click on skip warning in the warning modal
     */
    $('#resource_custom_warning_skip').click(function(){
        skipWarning = true;
        $('#resource-custom-metadata-form').submit();
    });



    /**
     * Check for missing field and trigger warning
     */
    $('#resource-custom-metadata-form').submit(function(e){
      if(skipWarning){
        $("#reload_page").val("yes");
        e.target.submit();
      }
      e.preventDefault();
      $('#warning_result_box').html('')      
      let metadataFieldsIds = ['material_combination_', 'surface_preparation_', 'atmosphere_', 'data_type_', 'analysis_method_'];
      let metadataFields = ['Material or Material Combination', 'Surface Preparation', 'Atmosphere', 'Data type', 'Measurement/Analysis Method'];
      let prefix = 'resource-checkbox-input-';
      let showWarning = false;
      for(let i=0; i < metadataFieldsIds.length; i++){       
        let resources_for_this_metadata = $('.' + prefix + metadataFieldsIds[i]);
        let resource_name = "";  
        let already_seen_resources = [];
        let selected_resources = [];
        for(let m=0; m < resources_for_this_metadata.length; m++){
          resource_name = $(resources_for_this_metadata[m]).attr("resource_name");
          if(!already_seen_resources.includes(resource_name)){
            already_seen_resources.push(resource_name);
          }      
          if($(resources_for_this_metadata[m]).prop('checked') == true){
            let name = $(resources_for_this_metadata[m]).attr('name');
            let id = name.split("custom_metadata_")[1];            
            if ($('#' + id).val() !== ''){
              selected_resources.push(resource_name);          
            }
            
          }
        }
      
        $('#warning_result_box').append("<strong>" +  metadataFields[i] + "</strong>");
        $('#warning_result_box').append('<br>');
        $('#warning_result_box').append('<ul>');
        for(let n=0; n < already_seen_resources.length; n++){
          if(!selected_resources.includes(already_seen_resources[n])){
            showWarning = true;                            
            $('#warning_result_box').append("<li class='missing-resource-name'>" + already_seen_resources[n] + "</li>");            
          }
        }
        $('#warning_result_box').append('</ul>');  
        $('#warning_result_box').append('<br>'); 
      }
      
      if(showWarning){
        $('#resource_metadata_warning').modal('show');
      }
      else {
        $("#reload_page").val("yes")
        e.target.submit();
      }
      
    });


    /**
     * remove a field box
     * 
     */
    $('.box-remove-anchor').click(function(){
        let id = $(this).attr('id');
        id = id[id.length - 1];
        field_name_box = $(this).attr('id').split('remove_')[0];
        // hide the field box
        $('#' + field_name_box + id).fadeOut(); 
        
        // unselect the checkboxes
        field_name = $(this).attr('id').split('box_remove_')[0];
        let checkBoxes = $('.resource-checkbox-input-' + field_name + id);
        for(let i=0; i < checkBoxes.length; i++){
            if($(checkBoxes[i]).prop('checked') == true){
              $(checkBoxes[i]).click();
            }
        }
        
        // unselect the select-all 
        if($('#select-all-resources-' + field_name + id).prop('checked') == true){
          $('#select-all-resources-' + field_name + id).click();
        }
        
        $('#metadata-resource-count-span-' + field_name + id).text(0);
        $('#metadata-resource-count-box-' + field_name + id).hide();
        $('#' + field_name + id).val('');
        
    });


    /**
     * click the select all checkbox
     * 
     */
     $('.select-all-resources').click(function(){
        let id = $(this).attr('id');
        field_name_box_and_id = $(this).attr('id').split('select-all-resources-')[1];
        let checkBoxes = $('.resource-checkbox-input-' + field_name_box_and_id);
        for(let i=0; i < checkBoxes.length; i++){
            if($(checkBoxes[i]).is(':visible')){
              if($(checkBoxes[i]).prop('checked') == !($(this).prop('checked'))){
                  $(checkBoxes[i]).click();
              }
            }
        }
    });


     /**
     * hide a resource from other modals when the resource is chosen for one metadata in a modal
     * 
     */

      let resources =  $('.resource-box');
      for(let i=0; i < resources.length; i++){
        if($(resources[i]).prop('checked') == true){
          let otherCheckBoxesWithSameId = $(".resource-box[value=" + $(resources[i]).val() + "]");
          for(let j=0; j < otherCheckBoxesWithSameId.length; j++){
              if ($(otherCheckBoxesWithSameId[j]).attr('field_name') ===  $(resources[i]).attr('field_name')){
                $(otherCheckBoxesWithSameId[j]).parent().hide();
              }
          }
        }
      }
      for(let i=0; i < resources.length; i++){
        if($(resources[i]).prop('checked') == true){          
          $(resources[i]).parent().show();  
        }
      }

      $('.resource-box').click(function(){
          let resources_checkbox = $('.resource-box');
          for(let i=0; i < resources_checkbox.length; i++){
              if($(resources_checkbox[i]).val() ===  $(this).val() && $(resources_checkbox[i]).attr('field_name') ===  $(this).attr('field_name')){
                if($(this).prop('checked') == true){
                  $(resources_checkbox[i]).parent().hide();    
                }
                else{
                  $(resources_checkbox[i]).parent().show();
                }
              }
          }

          if($(this).prop('checked') == true){
            $(this).parent().show();          
          }
          
      });


      /**
     * Click Add button on a modal
     * 
     */
    $('.res_custom_metadat_modal_save').click(function(){
        setResourceCount(this);
      
    });


    /**
     * click the edit mark on the resource count box
     * 
     */

     $('.custom-metadata-resource_count_edit').click(function(){
      let id = $(this).attr('id');
      let field_name_box_and_id = id.split('metadata-resource-count-icon-')[1];      
      $('#resourcesModal_' + field_name_box_and_id).modal({
        backdrop: 'static',
        keyboard: false
       });
      $('#resourcesModal_' + field_name_box_and_id).modal('show'); 
    });


});



function setResourceCount (modalBtn){
    let id = $(modalBtn).attr('id');
    let field_name_box_and_id = id.split('modal-add-btn-')[1];
    let boxes = $('.resource-checkbox-input-' + field_name_box_and_id);
    let resourceCount = 0;
    for (let i=0; i < boxes.length; i++){
        if($(boxes[i]).prop('checked') == true){
            resourceCount += 1;
        }
    }
    
    if(resourceCount !== 0){
      $('#metadata-resource-count-span-' + field_name_box_and_id).text(resourceCount);
      $('#metadata-resource-count-box-' + field_name_box_and_id).show();
    }
    else{
      $('#metadata-resource-count-span-' + field_name_box_and_id).text(0);
      $('#metadata-resource-count-box-' + field_name_box_and_id).hide();
    }
}