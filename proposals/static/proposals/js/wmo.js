function check_metc_required(check_url) {
    $("input[name=metc]").change(function() {
        // On change of the metc field, hide/unset the status
        $("#metc_status").empty().removeClass();

        // Set the is_medical field based on the checked value
        var no_metc = $.inArray($("input[name=metc]:checked").val(), ["N", "?"]) > -1;
        $("input[name=is_medical]").parents("tr").toggle(no_metc);
        $("input[name=is_behavioristic]").parents("tr").toggle(no_metc);
    });
    $("input[name=metc]").change();

    $("input[name=metc], input[name=is_medical], input[name=is_behavioristic]").change(function() {
        // Check which status message should be displayed
        var metc = $("input[name=metc]:checked").val();
        var medical = $("input[name=is_medical]:checked").val();
        var behavioristic = $("input[name=is_behavioristic]:checked").val();

        // Only do the check if the fields are filled
        if (metc === "Y" || (medical !== undefined && behavioristic !== undefined)) {
            var params = {"metc": metc, "medical": medical, "behavioristic": behavioristic};
            $.post(check_url, params, function(data) {
                $("#metc_status").html(data.message);
                $("#metc_status").attr("class", data.message_class);
            });
        }
    });
    $("input[name=metc], input[name=is_medical], input[name=is_behavioristic]").change();
}
