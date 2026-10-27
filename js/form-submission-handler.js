(function() {
  var FIELD_LABELS = {
    name: "שם מלא",
    phone: "מספר טלפון",
    email: "כתובת מייל",
    message: "הודעה"
  };

  /* Native browser bubbles follow the browser UI language (often English);
     override each field's message with a Hebrew string on the 'invalid' event */
  function hebrewValidityMessage(el) {
    var v = el.validity;
    if (v.valueMissing) {
      if (el.type === "checkbox") {
        return "נא לסמן את תיבת האישור לשליחת הפרטים, בהתאם למדיניות הפרטיות והעוגיות.";
      }
      return "נא למלא את השדה: " + (FIELD_LABELS[el.id] || "השדה") + ".";
    }
    if (v.typeMismatch) {
      return "הכתובת שהוזנה אינה כתובת מייל תקינה (חסר הסימן @).";
    }
    if (v.patternMismatch) {
      return "הערך שהוזן אינו תקין. נא להזין את הפורמט המבוקש.";
    }
    return "הערך שהוזן אינו תקין. נא לתקן ולנסות שוב.";
  }

  function bindHebrewValidationMessages(form) {
    var controls = form.querySelectorAll("input, textarea");
    for (var i = 0; i < controls.length; i++) {
      (function(el) {
        el.addEventListener("invalid", function() {
          el.setCustomValidity(hebrewValidityMessage(el));
        }, false);
        el.addEventListener("input", function() {
          el.setCustomValidity("");
        }, false);
        el.addEventListener("change", function() {
          el.setCustomValidity("");
        }, false);
      })(controls[i]);
    }
  }

  function getFormData(form) {
    var elements = form.elements;
    var honeypot;

    var fields = Object.keys(elements)
      .filter(function(k) {
        if (elements[k].name === "notUsed") {
          honeypot = elements[k].value;
          return false;
        }
        return true;
      })
      .map(function(k) {
        if (elements[k] && elements[k].name !== undefined) {
          return elements[k].name;
        }
        if (elements[k] && elements[k].length > 0) {
          return elements[k].item(0).name;
        }
        return undefined;
      })
      .filter(function(item, pos, self) {
        return self.indexOf(item) == pos && item;
      });

    var formData = {};
    fields.forEach(function(name) {
      var element = elements[name];

      formData[name] = element.value;

      if (element.length) {
        var data = [];
        for (var i = 0; i < element.length; i++) {
          var item = element.item(i);
          if (item.checked || item.selected) {
            data.push(item.value);
          }
        }
        formData[name] = data.join(', ');
      }
    });

    formData.formDataNameOrder = JSON.stringify(fields);
    formData.formGoogleSheetName = form.dataset.sheet || "responses";
    formData.formGoogleSendEmail = form.dataset.email || "";

    return {data: formData, honeypot: honeypot};
  }

  function showFailure(form) {
    var failureMessage = form.querySelector(".failure_message");
    if (failureMessage) {
      failureMessage.classList.remove("d-none");
      failureMessage.focus && failureMessage.focus();
    }
  }

  function handleFormSubmit(event) {
    var url, formData, data, encoded, xhr, formElements, thankYouMessage,
        failureMessage, buttons, i;

    event.preventDefault();
    var form = event.target;

    try {
      formData = getFormData(form);
    } catch (err) {
      showFailure(form);
      return false;
    }
    data = formData.data;

    if (formData.honeypot) {
      return false;
    }

    failureMessage = form.querySelector(".failure_message");
    if (failureMessage) {
      failureMessage.classList.add("d-none");
    }

    url = form.action;
    xhr = new XMLHttpRequest();
    xhr.open('POST', url);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
      if (xhr.readyState !== 4) {
        return;
      }
      buttons = form.querySelectorAll("button");
      for (i = 0; i < buttons.length; i++) {
        buttons[i].disabled = false;
      }
      if (xhr.status === 200) {
        formElements = form.querySelectorAll(".form-control");
        for (i = 0; i < formElements.length; i++) {
          formElements[i].readOnly = true;
        }
        for (i = 0; i < buttons.length; i++) {
          buttons[i].disabled = true;
        }
        thankYouMessage = form.querySelector(".thankyou_message");
        if (thankYouMessage) {
          thankYouMessage.classList.remove("d-none");
          thankYouMessage.focus && thankYouMessage.focus();
        }
      } else {
        showFailure(form);
      }
    };
    xhr.onerror = function() {
      showFailure(form);
    };
    encoded = Object.keys(data).map(function(k) {
      return encodeURIComponent(k) + "=" + encodeURIComponent(data[k]);
    }).join('&');
    xhr.send(encoded);
  }

  function loaded() {
    var forms = document.querySelectorAll("form.gform");
    for (var i = 0; i < forms.length; i++) {
      forms[i].addEventListener("submit", handleFormSubmit, false);
      bindHebrewValidationMessages(forms[i]);
    }
  }

  document.addEventListener("DOMContentLoaded", loaded, false);
})();
