function word_counter(element_id) {
    $(function () {    
        // Add a running word count to the textField
        let textField = $(element_id);
        if (textField.length) {
        textField.after("<div id='wordcount_textField' />");
        textField[0].addEventListener("input", function () {
            var wordCount = 0;
            if (this.value.trim()) {
            wordCount = this.value.match(/\S+/g).length;
            }
            $("#wordcount_textField").text(" {% trans 'Aantal woorden:' %} " + wordCount);
        }, false);
        }
    });
}