/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true *//*global jQuery:false, document:false, window:false, location:false */(function(e) {
    e(document).ready(function() {
        if (jQuery.browser.msie && parseInt(jQuery.browser.version, 10) < 7) return;
        e('a[data-appui="gallery"]').prettyPhoto();
        e('a[data-appui="pagescroll"]').on("click", function(t) {
            t.preventDefault();
            var n = e(this).data("target");
            e.scrollTo(n, {
                duration: "slow"
            });
        });
        var t = e('form[data-appui="autosave"]'), n = e(t).data("appui-target");
        e(t).autosave({
            callbacks: {
                trigger: [ "change", function() {
                    var t = this;
                    e('input[name="form.buttons.Submit"]').click(function() {
                        t.save();
                    });
                } ],
                save: {
                    method: "ajax",
                    options: {
                        url: n,
                        success: function() {
                            alert("autosaved");
                        }
                    }
                }
            }
        });
    });
})(jQuery);