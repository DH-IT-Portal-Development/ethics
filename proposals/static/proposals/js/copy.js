$(function () {
     $('#id_parent').change(function () {
         // Get the displayed value
         let chosen = $( "#id_parent option:selected" ).text();
         // Split on the ( and trim to remove the user part
         chosen = chosen.split('(')[0].trim();
         // Set it as the new title
         $('#id_title').val(chosen);
     })
});