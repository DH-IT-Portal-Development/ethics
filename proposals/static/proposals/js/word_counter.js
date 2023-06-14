function wordCounter(element, translated_string) {    
    $(function () {  
          
        // Add a running word count to a textfield
        // The element argument should be the name of the textField in the model
        // The translated string should be a translateable string variable. 
        // It needs to be declared outside of this function so that it can be translated in the template

        let textField = $("#id_" + element);
        if (textField.length) {
        textField.after("<div id='wordcount_" + element + "' />");
        textField[0].addEventListener("input", function () {
            var wordCount = 0;
            if (this.value.trim()) {
            wordCount = this.value.match(/\S+/g).length;
            }
            $("#wordcount_" + element).text(translated_string + wordCount);
        }, false);
        }
    });
}