/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

(function ($) {
    $(document).ready(function () {
        if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) {
            // it's not realistic to think we can deal with all the bugs
            // of IE 6 and lower. Fortunately, all this is just progressive
            // enhancement.
            return;
        }
        $('a[data-appui="gallery"]').prettyPhoto();
        $('a[data-appui="pagescroll"]').on('click', function (e) {
            e.preventDefault();
            var target_div = $(this).data('target');
            $.scrollTo(target_div, {
                "duration": "slow"
            });
        });
        function autoSaveSurvey() {
            $('form[data-appui="autosave"]').each(function () {
                var ajax_url = $(this).data('appui-target');
                $.ajax({
                    url: ajax_url,
                    data: $(this).serializeArray(),
                    success: function (data) {
                        if (data.success) {
                            message = data.message;
                            $.gritter.add({
                                // (string | mandatory) the heading of the notification
                                title: message,
                                // (string | mandatory) the text inside the notification
                                text: data.timestamp
                            });
                            //var htmlString = '<p class="text-warning">' + message + '</p>';
                            //$('#form-state').append(htmlString).slideDown('slow');
                        } else {
                            // This could be nicer in the future...
                            alert(error_msg + "\n\nError:\n" + data.messages);
                        }
                    }
                });
            });
        }
        //setTimeout(autoSaveSurvey(), 2000);
        setInterval(autoSaveSurvey, 30000);
    });
}(jQuery));
