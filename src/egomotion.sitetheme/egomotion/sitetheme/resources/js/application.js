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
        $('span[data-appui="prettydate"]').timeago();
        $('a[data-appui="gallery"]').prettyPhoto();
        if ($('#sweepstake-notice').length > 0) {
            $('#sweepstake-notice').expose();
        }
        $('a[data-appui="pagescroll"]').on('click', function (e) {
            e.preventDefault();
            var target_div = $(this).data('target');
            $.scrollTo(target_div, {
                "duration": "slow"
            });
        });
        var clip = new ZeroClipboard( $('#copy-button-id, #copy-button-code'), {
            moviePath: "/++theme++egomotion.sitetheme/img/ZeroClipboard.swf"
        });
        clip.on('complete', function(client, args) {
            $('#copy-notice').show().delay(3000).fadeOut('slow');
            //alert('Test triggered: ' + args.text);
        })
        $('#form-survey input[type="text"]').on('keypress', function (e) {
            if (e.keyCode === 13){
                e.preventDefault();
                console.log('Form submit supressed');
                return false;
            }
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
                        } else {
                            // This could be nicer in the future...
                            alert(error_msg + "\n\nError:\n" + data.messages);
                        }
                    }
                });
            });
        }
        $('#form-survey').on('load', function () {
            autoSaveSurvey;
        });
        //setTimeout(autoSaveSurvey(), 2000);
        setInterval(autoSaveSurvey, 30000);
    });
}(jQuery));
