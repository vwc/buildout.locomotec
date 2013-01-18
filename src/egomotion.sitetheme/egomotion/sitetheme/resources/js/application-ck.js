/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true *//*global jQuery:false, document:false, window:false, location:false */(function(e) {
    e(document).ready(function() {
        function t() {
            e('form[data-appui="autosave"]').each(function() {
                var t = e(this).data("appui-target");
                e.ajax({
                    url: t,
                    data: e(this).serializeArray(),
                    success: function(t) {
                        if (t.success) {
                            message = t.message;
                            e.gritter.add({
                                title: message,
                                text: t.timestamp
                            });
                        } else alert(error_msg + "\n\nError:\n" + t.messages);
                    }
                });
            });
        }
        if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) return;
        e('span[data-appui="prettydate"]').timeago();
        e('a[data-appui="gallery"]').prettyPhoto();
        e("#sweepstake-notice").length > 0 && e("#sweepstake-notice").expose();
        e('a[data-appui="pagescroll"]').on("click", function(t) {
            t.preventDefault();
            var n = e(this).data("target");
            e.scrollTo(n, {
                duration: "slow"
            });
        });
        e("#form-survey").on("load", function() {
            t;
        });
        setInterval(t, 3e4);
    });
})(jQuery);