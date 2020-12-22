// This file contains code that turns links with a certain class into a submit
// button with a given redirect after submitting

$(function () {
   $('a.js-submit-redirect').click(function (e) {
       // Prevent the link from actually going through
       e.preventDefault();

       let link = $(this).attr('href');
       let form = $('form:not(.language-form)');
       let currentAction = form.attr('action');

       let actionURL = undefined;

       // Most of the time the action is empty, but sometimes it isn't.
       if (currentAction)
       {
           // When it isn't, create an URL object from that action (with origin,
           // as URL expects a full URL or an origin)
           actionURL = new URL(currentAction, window.location.origin);
       }
       else
       {
           // If it is empty, just create it from the current page
           actionURL = new URL(window.location);
       }

       // If the action URL contains GET parameters, add it to the parameters
       if (actionURL.search.startsWith('?'))
           actionURL.search = actionURL.search + "&next=" + encodeURI(link)
       else
           // Otherwise, set the GET parameters
           actionURL.search = "?next=" + encodeURI(link)

       // Override the form action
       form.attr('action', actionURL.toString());
       // And submit
       form.submit();

       // Another measure to prevent the link from going through
       return false;
   });
});