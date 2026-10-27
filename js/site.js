(function () {
  "use strict";

  function showCookieNotice() {
    var notice = document.getElementById("cookieNotice");
    if (!notice) {
      return;
    }
    var dismissed = false;
    try {
      dismissed = !!window.localStorage.getItem("cookieNoticeDismissed");
    } catch (err) {
      dismissed = false;
    }
    if (!dismissed) {
      notice.hidden = false;
    }
    var accept = document.getElementById("cookieAccept");
    if (accept) {
      accept.addEventListener("click", function () {
        notice.hidden = true;
        try {
          window.localStorage.setItem("cookieNoticeDismissed", "1");
        } catch (err) {
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", showCookieNotice);
  } else {
    showCookieNotice();
  }
})();
