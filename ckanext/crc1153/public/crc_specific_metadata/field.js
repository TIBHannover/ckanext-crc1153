$(document).ready(function(){

  /* 
    Material/Material combination autocomplete
  */
  let materials = [
          {value : "Aluminium" , data: "Aluminium"},
          {value : "Kupfer" , data: "Kupfer"},
          {value : "Stahl" , data: "Stahl"},
          {value : "Titan" , data: "Titan"},
          {value : "Titan_Pulver" , data: "Titan_Pulver"}
        ];
  $('.input-material_combination_').autocomplete({lookup:materials}); 

  /* 
    data types autocomplete
  */
    let dataTypes = [
      {value : "Mech.-Eigenschaften" , data: "Mech.-Eigenschaften"},
      {value : "Phys.-Eigenschaften" , data: "Phys.-Eigenschaften"}
    ];
  $('.input-data_type_').autocomplete({lookup:dataTypes});

  
  /* 
    surface prepration autocomplete
  */
    let surfaces = [
      {value : "Oberflächenbehandlung" , data: "Oberflächenbehandlung"},
      {value : "Buersten" , data: "Buersten"},
      {value : "Chemisch" , data: "Chemisch"},
      {value : "Plasma" , data: "Plasma"},
      {value : "Schleifen" , data: "Schleifen"},
      {value : "Unbehandelt" , data: "Unbehandelt"}
    ];
  $('.input-surface_preparation_').autocomplete({lookup:surfaces});


   /* 
    Atmosphere autocomplete
  */
    let atmospheres = [
      {value : "Ar" , data: "Ar"},
      {value : "Ar-Silan" , data: "Ar-Silan"},
      {value : "H2" , data: "H2"},
      {value : "H2-Silan" , data: "H2-Silan"},
      {value : "Schleifen" , data: "Schleifen"},
      {value : "Normal-O2" , data: "Normal-O2"}
    ];
  $('.input-atmosphere_').autocomplete({lookup:atmospheres});
  
  
  
  
  /**
     * Add new metadata input field for material combination
     * 
     */
     
    let mc_processed_count = $('#processed_metadata_count_material_combination_').val();
    if(parseInt(mc_processed_count) != 0){
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
     * Add new metadata input field for surface preparation
     * 
     */

      let sp_processed_count = $('#processed_metadata_count_surface_preparation_').val();
      if(parseInt(sp_processed_count) != 0){
        for(let i=1; i <= parseInt(sp_processed_count); i++){
          $('#surface_preparation_box_' + i).show();
        }
      }
      else{
        $('#surface_preparation_box_1').show();
      }

      $('#surface_preparation_new').click(function(){
        let all_visible = false;
        for(let i=1; i <= $('.surface-preparation-box').length; i++){
          if ($('#surface_preparation_box_' + i).is(':hidden')){
            $('#surface_preparation_box_' + i).fadeIn();
            all_visible = true;
            break;
          }
        }
        if(!all_visible){
          $(this).hide();
        }
      });



      /**
     * Add new metadata input field for Atmosphere
     * 
     */
       let at_processed_count = $('#processed_metadata_count_atmosphere_').val();
       if(parseInt(at_processed_count) != 0){
         for(let i=1; i <= parseInt(at_processed_count); i++){
           $('#atmosphere_box_' + i).show();
         }
       }
       else{
          $('#atmosphere_box_1').show();
       }
       
       $('#atmosphere_new').click(function(){
         let all_visible = false;
         for(let i=1; i <= $('.atmosphere-box').length; i++){
           if ($('#atmosphere_box_' + i).is(':hidden')){
             $('#atmosphere_box_' + i).fadeIn();
             all_visible = true;
             break;
           }
         }
         if(!all_visible){
           $(this).hide();
         }
       });



       /**
     * Add new metadata input field for Data Type
     * 
     */
        let dt_processed_count = $('#processed_metadata_count_data_type_').val();
        if(parseInt(dt_processed_count) != 0){
          for(let i=1; i <= parseInt(dt_processed_count); i++){
            $('#data_type_box_' + i).show();
          }
        }
        else{
          $('#data_type_box_1').show();
        }
        
        $('#data_type_new').click(function(){
          let all_visible = false;
          for(let i=1; i <= $('.data-type-box').length; i++){
            if ($('#data_type_box_' + i).is(':hidden')){
              $('#data_type_box_' + i).fadeIn();
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
      if(parseInt(am_processed_count) != 0){
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