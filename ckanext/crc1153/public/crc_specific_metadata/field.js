$(document).ready(function(){  
  /**
     * Add new metadata input field for material combination
     * 
     */
     
    let mc_processed_count = $('#processed_metadata_count_material_combination_').val();
    if(parseInt(mc_processed_count) !== 0){
      for(let i=1; i <= parseInt(mc_processed_count); i++){
        $('#material_combination_box_' + i).show();
      }
    }
    else{
      $('#material_combination_box_1').show();
    }
     $('#mat_comb').click(function(){
       let all_visible = false;
       for(let i=1; i <= $('.material-comb-box').length; i++){
         if ($('#material_combination_box_' + i).is(':hidden')){
           $('#material_combination_box_' + i).fadeIn();
           all_visible = true;
           break;
         }
       }
      //  if(!all_visible){
      //    $(this).hide();
      //  }
     });



     /**
     * Add new metadata input field for demonstrator
     * 
     */

      let dem_processed_count = $('#processed_metadata_count_demonstrator_').val();
      if(parseInt(dem_processed_count) !== 0){
        for(let i=1; i <= parseInt(dem_processed_count); i++){
          $('#demonstrator_box_' + i).show();
        }
      }
      else{
        $('#demonstrator_box_1').show();
      }

      $('#demonstrator_new').click(function(){
        let all_visible = false;
        for(let i=1; i <= $('.demonstrator-box').length; i++){
          if ($('#demonstrator_box_' + i).is(':hidden')){
            $('#demonstrator_box_' + i).fadeIn();
            all_visible = true;
            break;
          }
        }
        if(!all_visible){
          $(this).hide();
        }
      });



      /**
     * Add new metadata input field for manufacturing_process
     * 
     */
       let mp_processed_count = $('#processed_metadata_count_manufacturing_process_').val();
       if(parseInt(mp_processed_count) !== 0){
         for(let i=1; i <= parseInt(at_processed_count); i++){
           $('#manufacturing_process_box_' + i).show();
         }
       }
       else{
          $('#manufacturing_process_box_1').show();
       }
       
       $('#manufacturing_process_new').click(function(){
         let all_visible = false;
         for(let i=1; i <= $('.manufacturing_process-box').length; i++){
           if ($('#manufacturing_process_box_' + i).is(':hidden')){
             $('#manufacturing_process_box_' + i).fadeIn();
             all_visible = true;
             break;
           }
         }
         if(!all_visible){
           $(this).hide();
         }
       });
    

     /**
     * Add new metadata input field for Analysis Method
     * 
     */

      let am_processed_count = $('#processed_metadata_count_analysis_method_').val();
      if(parseInt(am_processed_count) !== 0){
        for(let i=1; i <= parseInt(am_processed_count); i++){
          $('#analysis_method_box_' + i).show();
        }
      }
      else{
        $('#analysis_method_box_1').show();
      }
      
      $('#analysis_method_new').click(function(){
        let all_visible = false;
        for(let i=1; i <= $('.analysis-method-box').length; i++){
          if ($('#analysis_method_box_' + i).is(':hidden')){
            $('#analysis_method_box_' + i).fadeIn();
            all_visible = true;
            break;
          }
        }
        if(!all_visible){
          $(this).hide();
        }
      });
});
