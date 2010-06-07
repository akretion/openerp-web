/**
 * Opens the provided URL in the application content section.
 *
 * If the application content section (#appContent) does not
 * exist, simply change the location.
 *
 * @param url the URL to GET and insert into #appContent
 * @default afterLoad callback to execute after URL has been loaded and
 *                    inserted, if any. Takes the parameters provided
 *                    by jQuery.load: responseText, textStatus and
 *                    XMLHttpRequest
 */
var console;
function openLink(url /*optional afterLoad */) {
    var app = jQuery('#appContent');
    var afterLoad = arguments[1];
    if(app.length) {
        jQuery.ajax({
            url: url,
            complete: function (xhr) {
                console.debug(app.get(0));
                console.debug(xhr);
                app.html(xhr.responseText);
                if(afterLoad) { afterLoad(); }
            }
        });
    } else {
        window.location.assign(url);
    }
}

// Timers before displaying the wait box, in case the remote query takes too long
/** @constant */
var LINK_WAIT_NO_ACTIVITY = 300;
/** @constant */
var FORM_WAIT_NO_ACTIVITY = 500;
jQuery(document).ready(function () {
    var app = jQuery('#appContent');
    if (app.length) {
        var waitBox = new openerp.ui.WaitBox();
        // open un-targeted links in #appContent via xhr. Links with @target are considered
        // external links. Ignore hash-links.
        jQuery(document).delegate('a[href]:not([target]):not([href^="#"]):not([href^="javascript"])', 'click', function () {
            if(console) {
                console.debug('opening link', this);
            }
            waitBox.showAfter(LINK_WAIT_NO_ACTIVITY);
            openLink(jQuery(this).attr('href'),
                     jQuery.proxy(waitBox, 'hide'));
            return false;
        });
        // do the same for forms
        jQuery(document).delegate('form:not([target])', 'submit', function () {
            var form = jQuery(this);
            if(console) {
                console.debug('submitting form', this);
            }
            // Don't make the wait box appear immediately
            waitBox.showAfter(FORM_WAIT_NO_ACTIVITY);
            jQuery.ajax({
                url: form.attr("action"),
                data: form.serialize(),
                type: form.attr('method') || 'GET',
                contentType: form.attr('enctype') || 'application/x-www-form-urlencoded',
                complete: function (xhr) {
                    app.html(xhr.responseText);
                    jQuery.proxy(waitBox, 'hide');
                }
            });
            return false;
        });
    }
});
