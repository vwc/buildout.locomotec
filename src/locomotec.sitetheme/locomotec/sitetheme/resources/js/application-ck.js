/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true *//*global jQuery:false, document:false, window:false, location:false */(function(e){e(document).ready(function(){if(jQuery.browser.msie&&parseInt(jQuery.browser.version,10)<7)return;e('a[data-appui="tocnav"]').on("click",function(t){t.preventDefault();var n=e(this).data("target");e.scrollTo(n,{duration:"slow"},{onAfter:function(){n==="#navigation"&&e("#scroll-top").fadeOut("slow")}})})})})(jQuery);