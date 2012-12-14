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
        $('a[data-appui="tocnav"]').on('click', function (e) {
            e.preventDefault();
            var target_id = $(this).data('target');
            $.scrollTo(target_id, {
                "duration": "slow"
            }, {onAfter: function () {
                if (target_id === '#navigation') {
                    $('#scroll-top').fadeOut('slow');
                }
            }});
        });
    });
}(jQuery));
