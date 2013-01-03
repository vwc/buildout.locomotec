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
        var ajax_form = $('form[data-appui="autosave"]');
        var ajax_save_url = $(ajax_form).data('appui-target');
        $(ajax_form).autosave({
            callbacks: {
                trigger: ["change", function () {
                    var self = this;
                    $('input[name="form.buttons.Submit"]').click(function () {
                        self.save();
                    });
                }],
                save: {
                    method: "ajax",
                    options: {
                        url: ajax_save_url,
                        success: function () {
                            alert("autosaved");
                        }
                    }
                }
            }
        });
    });
}(jQuery));
